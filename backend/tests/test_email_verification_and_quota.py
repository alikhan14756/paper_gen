import pytest
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.init_db import init_db
from app.core.security import hash_password, create_access_token, ROLE_TEACHER, ROLE_SCHOOL_ADMIN
from app.models.core_entities import School, User
from app.models.document_entities import Book, Chapter
from app.models.paper_entities import Paper, Section, Question
from app.api.v1.auth import register_school, verify_email, login
from app.api.v1.books import list_books, get_book
from app.api.v1.papers import generate_paper, get_subject_quota
from app.api.v1.schools import upgrade_school_subscription
from app.schemas.auth import RegisterSchoolRequest, VerifyEmailRequest, LoginRequest
from app.schemas.paper import GeneratePaperRequest, SectionConfig

@pytest.fixture(scope="module")
def db():
    init_db()
    session = SessionLocal()
    yield session
    session.close()

def test_register_school_email_verification_flow(db: Session):
    unique_suffix = uuid.uuid4().hex[:6]
    admin_email = f"principal_{unique_suffix}@peshawar.edu.pk"
    school_slug = f"peshawar-model-{unique_suffix}"

    # 1. Register school
    reg_req = RegisterSchoolRequest(
        school_name=f"Peshawar Model College {unique_suffix}",
        slug=school_slug,
        address="University Road, Peshawar",
        admin_name="Prof. Tariq Khan",
        admin_email=admin_email,
        admin_password="Password123!"
    )
    reg_res = register_school(reg_req, db)
    assert reg_res.email == admin_email

    # Verify user in database is not yet email-verified
    user = db.query(User).filter(User.email == admin_email).first()
    assert user is not None
    assert user.is_email_verified is False
    assert user.verification_code is not None
    assert len(user.verification_code) == 6
    received_email_code = user.verification_code

    # Verify school is created with free_trial defaults
    school = db.query(School).filter(School.id == user.school_id).first()
    assert school.subscription_tier == "free_trial"
    assert school.is_paid is False
    assert school.free_papers_per_subject == 2

    # 2. Login before verification must fail with 403
    login_req = LoginRequest(email=admin_email, password="Password123!")
    with pytest.raises(HTTPException) as exc:
        login(login_req, db)
    assert exc.value.status_code == 403
    assert "not verified" in exc.value.detail.lower()

    # 3. Verify with wrong code must fail
    wrong_req = VerifyEmailRequest(email=admin_email, code="000000")
    with pytest.raises(HTTPException) as exc:
        verify_email(wrong_req, db)
    assert exc.value.status_code == 400

    # 4. Verify with correct code from email must succeed
    correct_req = VerifyEmailRequest(email=admin_email, code=received_email_code)
    token_res = verify_email(correct_req, db)
    assert token_res.access_token is not None
    assert token_res.user.is_email_verified is True

    # 5. User can now log in successfully
    verified_login = login(login_req, db)
    assert verified_login.access_token is not None

def test_new_school_has_access_to_global_kpk_books(db: Session):
    # Create a fresh school and teacher
    school = School(
        id=str(uuid.uuid4()),
        name="Abbottabad Public School",
        slug=f"aps-{uuid.uuid4().hex[:6]}",
        status="active",
        subscription_tier="free_trial",
        is_paid=False,
    )
    user = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=f"teacher_{uuid.uuid4().hex[:6]}@aps.edu.pk",
        hashed_password=hash_password("Pass123!"),
        full_name="APS Teacher",
        role=ROLE_TEACHER,
        is_active=True,
        is_email_verified=True,
    )
    db.add_all([school, user])
    db.commit()

    # List books for this newly registered school
    books = list_books(db, user)
    # Must include all 18 authentic global KPK textbooks
    global_kpk = [b for b in books if b.is_global]
    assert len(global_kpk) >= 18

    # Teacher can access a global book directly
    sample_global_book = global_kpk[0]
    fetched_book = get_book(sample_global_book.id, db, user)
    assert fetched_book.id == sample_global_book.id

def test_free_trial_two_papers_per_subject_quota(db: Session):
    # Setup school on Free Trial (is_paid=False)
    school = School(
        id=str(uuid.uuid4()),
        name="Swat Model High School",
        slug=f"smhs-{uuid.uuid4().hex[:6]}",
        status="active",
        subscription_tier="free_trial",
        is_paid=False,
        free_papers_per_subject=2,
        max_monthly_papers=50,
    )
    teacher = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=f"swat_teacher_{uuid.uuid4().hex[:6]}@smhs.edu.pk",
        hashed_password=hash_password("Pass123!"),
        full_name="Swat Teacher",
        role=ROLE_TEACHER,
        is_active=True,
        is_email_verified=True,
    )
    # Find global Physics book
    phys_book = db.query(Book).filter(Book.is_global == True, Book.subject == "Physics", Book.grade == "9").first()
    assert phys_book is not None

    chaps = db.query(Chapter).filter(Chapter.book_id == phys_book.id).all()
    assert len(chaps) > 0
    selected_ch_id = chaps[0].id

    db.add_all([school, teacher])
    db.commit()

    # Check subject quota before any papers generated
    quota_info = get_subject_quota("Physics", db, teacher)
    assert quota_info["papers_used"] == 0
    assert quota_info["max_free_papers"] == 2
    assert quota_info["remaining_free_papers"] == 2
    assert quota_info["can_generate"] is True

    # 1. Manually simulate 1st paper for Physics
    paper1 = Paper(
        id=str(uuid.uuid4()),
        school_id=school.id,
        created_by_id=teacher.id,
        book_id=phys_book.id,
        title="Physics Class 9 Quiz 1",
        grade="9",
        subject="Physics",
        total_marks=20,
    )
    db.add(paper1)
    db.commit()

    quota_info = get_subject_quota("Physics", db, teacher)
    assert quota_info["papers_used"] == 1
    assert quota_info["remaining_free_papers"] == 1
    assert quota_info["can_generate"] is True

    # 2. Manually simulate 2nd paper for Physics (reaches the 2 papers limit)
    paper2 = Paper(
        id=str(uuid.uuid4()),
        school_id=school.id,
        created_by_id=teacher.id,
        book_id=phys_book.id,
        title="Physics Class 9 Quiz 2",
        grade="9",
        subject="Physics",
        total_marks=20,
    )
    db.add(paper2)
    db.commit()

    quota_info = get_subject_quota("Physics", db, teacher)
    assert quota_info["papers_used"] == 2
    assert quota_info["remaining_free_papers"] == 0
    assert quota_info["can_generate"] is False

    # 3. Attempting to generate a 3rd Physics paper must raise 403 FREE_TRIAL_LIMIT_REACHED
    gen_req = GeneratePaperRequest(
        book_id=phys_book.id,
        title="Physics 3rd Paper Attempt",
        grade="9",
        subject="Physics",
        selected_chapter_ids=[selected_ch_id],
        total_marks=20,
        sections=[
            SectionConfig(
                title="Section A",
                section_type="mcq",
                total_questions=2,
                questions_to_attempt=2,
                marks_per_question=1.0,
            )
        ]
    )

    with pytest.raises(HTTPException) as exc:
        import asyncio
        asyncio.run(generate_paper(gen_req, db, teacher))
    assert exc.value.status_code == 403
    assert "free trial limit reached" in exc.value.detail.lower()
    assert "muhammad ali" in exc.value.detail.lower()

    # 4. However, generating paper for a DIFFERENT subject (e.g. Chemistry) has its own 2 free papers!
    chem_quota = get_subject_quota("Chemistry", db, teacher)
    assert chem_quota["papers_used"] == 0
    assert chem_quota["remaining_free_papers"] == 2
    assert chem_quota["can_generate"] is True

    # 5. School Admin upgrades subscription to "paid"
    upgrade_res = upgrade_school_subscription(school.id, "paid", db, teacher)
    assert upgrade_res["is_paid"] is True
    assert upgrade_res["subscription_tier"] == "paid"

    # Now Physics is unlocked!
    unlocked_quota = get_subject_quota("Physics", db, teacher)
    assert unlocked_quota["is_paid"] is True
    assert unlocked_quota["can_generate"] is True
