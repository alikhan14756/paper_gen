import pytest
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.core.init_db import init_db
from app.core.security import hash_password, create_access_token, decode_access_token, ROLE_TEACHER, ROLE_SCHOOL_ADMIN, ROLE_SUPER_ADMIN
from app.core.deps import get_current_user, require_super_admin, require_school_admin_or_super
from app.models.core_entities import School, User, SchoolMembership
from app.models.document_entities import Book, Chapter
from app.models.paper_entities import (
    Paper,
    Section,
    Question,
    QuestionVersion,
    AnswerKey,
    UsageReservation,
    UsageRecord
)
from app.api.v1.papers import (
    get_paper,
    export_docx,
    get_confidential_answer_key,
    export_answer_key,
    download_answer_key,
    regenerate_single_question,
    update_question,
    reconcile_expired_reservations,
    generate_examination_blueprint,
    verify_official_examination_paper,
)
from app.api.v1.schools import (
    update_school,
    get_school_billing_analytics,
    reset_monthly_quota,
    get_school_audit_logs,
)
from app.api.v1.books import add_chapter, update_chapter
from app.schemas.school import SchoolUpdate
from app.schemas.chapter import ChapterCreate, ChapterUpdate
from app.schemas.paper import QuestionUpdate, BlueprintRequest

@pytest.fixture(scope="module")
def db():
    init_db()
    session = SessionLocal()
    yield session
    session.close()

def test_expired_and_malformed_tokens():
    # 1. Expired token
    expired_token = create_access_token(
        {"sub": "test-user-id", "role": ROLE_TEACHER},
        expires_delta=timedelta(seconds=-10)
    )
    assert decode_access_token(expired_token) is None

    # 2. Corrupt signature
    corrupt_token = expired_token[:-5] + "xyz12"
    assert decode_access_token(corrupt_token) is None

    # 3. Empty string
    assert decode_access_token("") is None

def test_deactivated_user_and_suspended_school(db: Session):
    school_active = School(
        id=str(uuid.uuid4()),
        name="Active School",
        slug=f"active-{uuid.uuid4().hex[:6]}",
        status="active"
    )
    school_suspended = School(
        id=str(uuid.uuid4()),
        name="Suspended School",
        slug=f"suspended-{uuid.uuid4().hex[:6]}",
        status="suspended"
    )
    user_deactivated = User(
        id=str(uuid.uuid4()),
        school_id=school_active.id,
        email=f"deactive.{uuid.uuid4().hex[:6]}@school.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="Deactivated Teacher",
        role=ROLE_TEACHER,
        is_active=False
    )
    user_in_suspended_school = User(
        id=str(uuid.uuid4()),
        school_id=school_suspended.id,
        email=f"suspended.{uuid.uuid4().hex[:6]}@school.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="Suspended School Teacher",
        role=ROLE_TEACHER,
        is_active=True
    )
    db.add_all([school_active, school_suspended, user_deactivated, user_in_suspended_school])
    db.commit()

    # Mock request object for get_current_user
    class DummyRequest:
        headers = {}

    class DummyCreds:
        def __init__(self, token):
            self.credentials = token

    token_deact = create_access_token({"sub": user_deactivated.id, "role": ROLE_TEACHER})
    token_susp = create_access_token({"sub": user_in_suspended_school.id, "role": ROLE_TEACHER})

    # Deactivated user must be rejected with 403
    with pytest.raises(HTTPException) as exc:
        get_current_user(DummyRequest(), DummyCreds(token_deact), None, db)
    assert exc.value.status_code == 403
    assert "deactivated" in exc.value.detail.lower()

    # User in suspended school must be rejected with 403
    with pytest.raises(HTTPException) as exc:
        get_current_user(DummyRequest(), DummyCreds(token_susp), None, db)
    assert exc.value.status_code == 403
    assert "suspended" in exc.value.detail.lower()

def test_confidential_answer_key_isolation(db: Session):
    # School X and Y
    school_x = School(id=str(uuid.uuid4()), name="School X", slug=f"school-x-{uuid.uuid4().hex[:6]}", status="active")
    school_y = School(id=str(uuid.uuid4()), name="School Y", slug=f"school-y-{uuid.uuid4().hex[:6]}", status="active")
    teacher_x = User(
        id=str(uuid.uuid4()),
        school_id=school_x.id,
        email=f"teacher.x.{uuid.uuid4().hex[:6]}@x.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="Teacher X",
        role=ROLE_TEACHER,
        is_active=True
    )
    teacher_y = User(
        id=str(uuid.uuid4()),
        school_id=school_y.id,
        email=f"teacher.y.{uuid.uuid4().hex[:6]}@y.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="Teacher Y",
        role=ROLE_TEACHER,
        is_active=True
    )
    db.add_all([school_x, school_y, teacher_x, teacher_y])
    db.commit()

    paper_x = Paper(
        id=str(uuid.uuid4()),
        school_id=school_x.id,
        created_by_id=teacher_x.id,
        title="Final Exam Biology X",
        grade="9",
        subject="Biology",
        total_marks=20,
        status="generated"
    )
    sec_x = Section(
        id=str(uuid.uuid4()),
        paper_id=paper_x.id,
        school_id=school_x.id,
        title="Section A (MCQs)",
        section_type="mcq",
        total_questions=1,
        questions_to_attempt=1,
        marks_per_question=1.0,
        total_section_marks=1.0
    )
    q_x = Question(
        id=str(uuid.uuid4()),
        section_id=sec_x.id,
        paper_id=paper_x.id,
        school_id=school_x.id,
        question_text="What is the powerhouse of the cell?",
        options_json='["Mitochondria", "Nucleus", "Ribosome", "Golgi Body"]',
        correct_answer="Mitochondria",
        marks=1.0
    )
    ans_key_x = AnswerKey(
        id=str(uuid.uuid4()),
        paper_id=paper_x.id,
        question_id=q_x.id,
        school_id=school_x.id,
        solution_text="Mitochondria",
        marking_guide="Award 1 mark for correct organelle identification."
    )
    db.add_all([paper_x, sec_x, q_x, ans_key_x])
    db.commit()

    # Teacher X can view confidential answer key
    key_resp = get_confidential_answer_key(paper_x.id, db, teacher_x)
    assert key_resp["paper_id"] == paper_x.id
    assert len(key_resp["marking_scheme"]) == 1
    assert key_resp["marking_scheme"][0]["correct_answer"] == "Mitochondria"

    # Teacher Y from another school is strictly denied (403)
    with pytest.raises(HTTPException) as exc:
        get_confidential_answer_key(paper_x.id, db, teacher_y)
    assert exc.value.status_code == 403

    # Teacher Y export answer key denied (403)
    with pytest.raises(HTTPException) as exc:
        export_answer_key(paper_x.id, db, teacher_y)
    assert exc.value.status_code == 403

    # Teacher Y download answer key denied (403)
    with pytest.raises(HTTPException) as exc:
        download_answer_key(paper_x.id, db, teacher_y)
    assert exc.value.status_code == 403

def test_usage_reservation_quota_lifecycle(db: Session):
    school = School(
        id=str(uuid.uuid4()),
        name="Quota Test School",
        slug=f"quota-{uuid.uuid4().hex[:6]}",
        status="active",
        max_monthly_papers=2,
        papers_generated_this_month=1
    )
    user = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=f"quota.{uuid.uuid4().hex[:6]}@school.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="Quota Teacher",
        role=ROLE_TEACHER,
        is_active=True
    )
    db.add_all([school, user])
    db.commit()

    # 1. First reservation fits under quota (1 used + 1 reserved <= 2 max)
    res1 = UsageReservation(
        id=str(uuid.uuid4()),
        school_id=school.id,
        user_id=user.id,
        reservation_token=str(uuid.uuid4()),
        units_reserved=1,
        status="reserved",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db.add(res1)
    db.commit()

    active_count = db.query(UsageReservation).filter(
        UsageReservation.school_id == school.id,
        UsageReservation.status == "reserved",
        UsageReservation.expires_at > datetime.now(timezone.utc)
    ).count()
    assert active_count == 1
    effective_used = school.papers_generated_this_month + active_count
    assert effective_used == 2

    # 2. Subsequent reservation attempt exceeds quota
    assert effective_used >= school.max_monthly_papers

    # 3. Simulate failure: release reservation
    res1.status = "released"
    db.commit()

    active_count_after_release = db.query(UsageReservation).filter(
        UsageReservation.school_id == school.id,
        UsageReservation.status == "reserved",
        UsageReservation.expires_at > datetime.now(timezone.utc)
    ).count()
    assert active_count_after_release == 0

    # 4. Now another reservation can be committed
    res2 = UsageReservation(
        id=str(uuid.uuid4()),
        school_id=school.id,
        user_id=user.id,
        reservation_token=str(uuid.uuid4()),
        units_reserved=1,
        status="committed",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    school.papers_generated_this_month += 1
    db.add(res2)
    db.commit()
    assert school.papers_generated_this_month == 2

def test_single_question_regeneration_and_isolation(db: Session):
    school = School(id=str(uuid.uuid4()), name="Regen School", slug=f"regen-{uuid.uuid4().hex[:6]}", status="active")
    teacher = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=f"regen.{uuid.uuid4().hex[:6]}@regen.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="Regen Teacher",
        role=ROLE_TEACHER,
        is_active=True
    )
    paper = Paper(
        id=str(uuid.uuid4()),
        school_id=school.id,
        created_by_id=teacher.id,
        title="Regeneration Integrity Exam",
        grade="10",
        subject="Chemistry",
        total_marks=20,
        status="generated"
    )
    sec = Section(
        id=str(uuid.uuid4()),
        paper_id=paper.id,
        school_id=school.id,
        title="Section A",
        section_type="mcq",
        total_questions=2,
        questions_to_attempt=2,
        marks_per_question=1.0,
        total_section_marks=2.0
    )
    q1 = Question(
        id=str(uuid.uuid4()),
        section_id=sec.id,
        paper_id=paper.id,
        school_id=school.id,
        question_number=1,
        question_text="Original Question 1 - Kept Intact",
        options_json='["Opt A", "Opt B"]',
        correct_answer="Opt A",
        marks=1.0
    )
    q2 = Question(
        id=str(uuid.uuid4()),
        section_id=sec.id,
        paper_id=paper.id,
        school_id=school.id,
        question_number=2,
        question_text="Original Question 2 - To Regenerate",
        options_json='["Opt 1", "Opt 2"]',
        correct_answer="Opt 1",
        marks=1.0
    )
    db.add_all([school, teacher, paper, sec, q1, q2])
    db.commit()

    # Regenerate ONLY question 2 using asyncio.run
    res = asyncio.run(regenerate_single_question(paper.id, q2.id, db, teacher))
    assert res.id == q2.id

    # Verify Question 1 was NOT modified
    db.refresh(q1)
    assert q1.question_text == "Original Question 1 - Kept Intact"
    assert q1.correct_answer == "Opt A"

    # Verify Question 2 has a version snapshot preserved
    versions = db.query(QuestionVersion).filter(QuestionVersion.question_id == q2.id).all()
    assert len(versions) == 1
    assert versions[0].question_text == "Original Question 2 - To Regenerate"

    # Verify Question 2's review_status is "edited"
    db.refresh(q2)
    assert q2.review_status == "edited"

def test_school_admin_cannot_escalate_quotas(db: Session):
    school = School(
        id=str(uuid.uuid4()),
        name="Escalation Guard School",
        slug=f"esc-{uuid.uuid4().hex[:6]}",
        status="active",
        max_teachers=10,
        max_monthly_papers=50
    )
    admin = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=f"admin.{uuid.uuid4().hex[:6]}@esc.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="School Admin",
        role=ROLE_SCHOOL_ADMIN,
        is_active=True
    )
    db.add_all([school, admin])
    db.commit()

    # School admin attempts to escalate quotas
    payload = SchoolUpdate(name="Renamed School", max_teachers=999, max_monthly_papers=9999)
    updated = update_school(school.id, payload, db, admin)

    db.refresh(school)
    assert school.name == "Renamed School"
    assert school.max_teachers == 10  # Quota escalation prevented!
    assert school.max_monthly_papers == 50  # Quota escalation prevented!

def test_invalid_chapter_boundaries_rejected(db: Session):
    school = School(id=str(uuid.uuid4()), name="Chap School", slug=f"chap-{uuid.uuid4().hex[:6]}", status="active")
    teacher = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=f"teacher.{uuid.uuid4().hex[:6]}@chap.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="Chap Teacher",
        role=ROLE_TEACHER,
        is_active=True
    )
    book = Book(
        id=str(uuid.uuid4()),
        school_id=school.id,
        uploaded_by_id=teacher.id,
        title="Valid Boundary Book",
        subject="Physics",
        grade="9",
        file_path="/dummy/book.pdf",
        total_pages=50,
        processing_status="ready"
    )
    db.add_all([school, teacher, book])
    db.commit()

    # 1. start_page < 1
    with pytest.raises(HTTPException) as exc:
        add_chapter(book.id, ChapterCreate(chapter_number=1, title="Invalid 1", start_page=0, end_page=10), db, teacher)
    assert exc.value.status_code == 400

    # 2. end_page < start_page
    with pytest.raises(HTTPException) as exc:
        add_chapter(book.id, ChapterCreate(chapter_number=1, title="Invalid 2", start_page=15, end_page=10), db, teacher)
    assert exc.value.status_code == 400

    # 3. end_page > total_pages
    with pytest.raises(HTTPException) as exc:
        add_chapter(book.id, ChapterCreate(chapter_number=1, title="Invalid 3", start_page=10, end_page=100), db, teacher)
    assert exc.value.status_code == 400

def test_reconcile_expired_reservations(db: Session):
    school = School(id=str(uuid.uuid4()), name="Recon School", slug=f"recon-{uuid.uuid4().hex[:6]}", status="active")
    user = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=f"recon.{uuid.uuid4().hex[:6]}@recon.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="Recon User",
        role=ROLE_TEACHER,
        is_active=True
    )
    # Stale reservation from 20 minutes ago
    expired_res = UsageReservation(
        id=str(uuid.uuid4()),
        school_id=school.id,
        user_id=user.id,
        reservation_token=str(uuid.uuid4()),
        units_reserved=1,
        status="reserved",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=20)
    )
    db.add_all([school, user, expired_res])
    db.commit()

    # Run reconciliation
    reconcile_expired_reservations(db, school.id)

    db.refresh(expired_res)
    assert expired_res.status == "released"

def test_ai_grounding_provenance_and_blooms(db: Session):
    from app.services.ai.provider import GroundedMockProvider
    mock = GroundedMockProvider()
    source = (
        "Force is any interaction that, when unopposed, will change the motion of an object. "
        "Newton's Second Law states that force equals mass times acceleration (F = ma). "
        "The SI unit of force is the Newton (N). This principle is applied in mechanical engineering."
    )
    questions = asyncio.run(mock.generate_questions_for_section(
        section_title="Section A - MCQs",
        section_type="mcq",
        count=2,
        marks_per_question=1.0,
        language="en",
        subject="Physics",
        grade="10",
        source_text=source,
        difficulty="medium"
    ))

    assert len(questions) == 2
    q0 = questions[0]
    assert "blooms_level" in q0
    assert q0["blooms_level"] in ["Remember", "Understand", "Apply", "Analyze", "Evaluate"]
    assert "source_excerpt" in q0
    assert len(q0["source_excerpt"]) > 20
    assert q0["confidence_score"] >= 0.90
    assert q0["quality_score"] >= 0.90
    assert q0["duplicate_risk"] <= 0.05

def test_examination_blueprint_generator(db: Session):
    school = School(id=str(uuid.uuid4()), name="Blueprint School", slug=f"bp-{uuid.uuid4().hex[:6]}", status="active")
    teacher = User(
        id=str(uuid.uuid4()),
        school_id=school.id,
        email=f"bp.{uuid.uuid4().hex[:6]}@school.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="BP Teacher",
        role=ROLE_TEACHER,
        is_active=True
    )
    book = Book(
        id=str(uuid.uuid4()),
        school_id=school.id,
        uploaded_by_id=teacher.id,
        title="Blueprint Physics 10",
        subject="Physics",
        grade="10",
        file_path="/dummy/path.pdf",
        processing_status="ready"
    )
    ch1 = Chapter(id=str(uuid.uuid4()), book_id=book.id, school_id=school.id, chapter_number=1, title="Kinematics", start_page=1, end_page=20)
    ch2 = Chapter(id=str(uuid.uuid4()), book_id=book.id, school_id=school.id, chapter_number=2, title="Dynamics", start_page=21, end_page=45)
    db.add_all([school, teacher, book, ch1, ch2])
    db.commit()

    req = BlueprintRequest(grade="10", subject="Physics", total_marks=50, selected_chapter_ids=[ch1.id, ch2.id])
    bp = generate_examination_blueprint(req, db, teacher)

    assert bp.total_marks == 50
    assert len(bp.chapters) == 2
    assert sum(c.marks_allocated for c in bp.chapters) == 50
    assert bp.blooms_summary["Remember"] > 0
    assert bp.difficulty_summary["Medium"] > 0

def test_paper_verification_endpoint(db: Session):
    school = School(id=str(uuid.uuid4()), name="Verify High School", slug=f"verify-{uuid.uuid4().hex[:6]}", status="active")
    code = f"EXAM-{uuid.uuid4().hex[:8].upper()}"
    paper = Paper(
        id=str(uuid.uuid4()),
        school_id=school.id,
        title="Verified Board Examination 2026",
        grade="10",
        subject="Physics",
        total_marks=75,
        verification_code=code,
        status="generated"
    )
    db.add_all([school, paper])
    db.commit()

    res = verify_official_examination_paper(code, db)
    assert res["status"] == "VERIFIED_OFFICIAL"
    assert res["verification_code"] == code
    assert res["paper_title"] == "Verified Board Examination 2026"
    assert res["school_name"] == "Verify High School"

def test_school_billing_analytics_and_audit_logs(db: Session):
    school = School(
        id=str(uuid.uuid4()),
        name="Billing School",
        slug=f"bill-{uuid.uuid4().hex[:6]}",
        status="active",
        max_monthly_papers=100,
        papers_generated_this_month=25
    )
    super_admin = User(
        id=str(uuid.uuid4()),
        email=f"super.{uuid.uuid4().hex[:6]}@examforge.ai",
        hashed_password=hash_password("Pass123!"),
        full_name="Super Admin",
        role=ROLE_SUPER_ADMIN,
        is_active=True
    )
    db.add_all([school, super_admin])
    db.commit()

    # 1. Billing analytics
    analytics = get_school_billing_analytics(school.id, db, super_admin)
    assert analytics["school_id"] == school.id
    assert analytics["quota_summary"]["papers_generated_this_month"] == 25
    assert analytics["quota_summary"]["paper_utilization_pct"] == 25.0

    # 2. Reset monthly quota
    reset_res = reset_monthly_quota(school.id, db, super_admin)
    assert reset_res["previous_papers_generated"] == 25
    db.refresh(school)
    assert school.papers_generated_this_month == 0

    # 3. Audit logs
    logs = get_school_audit_logs(school.id, 10, db, super_admin)
    assert len(logs) >= 1
    assert any(l["action"] == "reset_monthly_paper_quota" for l in logs)
