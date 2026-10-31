import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.core.init_db import init_db
from app.core.security import hash_password, create_access_token, ROLE_TEACHER
from app.models.core_entities import School, User, SchoolMembership
from app.models.document_entities import Book, Chapter
from app.models.paper_entities import Paper, Section, Question
from app.api.v1.books import get_book, delete_book
from app.api.v1.papers import get_paper, export_docx, delete_question
from fastapi import HTTPException

@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_tenant_isolation_across_schools(db_session: Session):
    # 1. Setup School A and Teacher A
    school_a = School(
        id=str(uuid.uuid4()),
        name="School Alpha",
        slug=f"school-alpha-{uuid.uuid4().hex[:6]}",
        status="active"
    )
    teacher_a = User(
        id=str(uuid.uuid4()),
        school_id=school_a.id,
        email=f"teacher.a.{uuid.uuid4().hex[:6]}@alpha.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="Teacher Alpha",
        role=ROLE_TEACHER,
        is_active=True
    )

    # 2. Setup School B and Teacher B
    school_b = School(
        id=str(uuid.uuid4()),
        name="School Beta",
        slug=f"school-beta-{uuid.uuid4().hex[:6]}",
        status="active"
    )
    teacher_b = User(
        id=str(uuid.uuid4()),
        school_id=school_b.id,
        email=f"teacher.b.{uuid.uuid4().hex[:6]}@beta.edu",
        hashed_password=hash_password("Pass123!"),
        full_name="Teacher Beta",
        role=ROLE_TEACHER,
        is_active=True
    )

    db_session.add_all([school_a, teacher_a, school_b, teacher_b])
    db_session.commit()

    # 3. Teacher A creates Book A in School A
    book_a = Book(
        id=str(uuid.uuid4()),
        school_id=school_a.id,
        uploaded_by_id=teacher_a.id,
        title="Physics Alpha Book",
        subject="Physics",
        grade="10",
        file_path="/dummy/path.pdf",
        processing_status="ready"
    )
    db_session.add(book_a)
    db_session.commit()

    # 4. Teacher A creates Paper A in School A
    paper_a = Paper(
        id=str(uuid.uuid4()),
        school_id=school_a.id,
        created_by_id=teacher_a.id,
        book_id=book_a.id,
        title="Midterm Alpha Exam",
        grade="10",
        subject="Physics",
        total_marks=50,
        status="generated"
    )
    db_session.add(paper_a)
    db_session.commit()

    sec_a = Section(
        id=str(uuid.uuid4()),
        paper_id=paper_a.id,
        school_id=school_a.id,
        title="Section A",
        section_type="mcq",
        total_questions=1,
        questions_to_attempt=1,
        marks_per_question=1.0,
        total_section_marks=1.0
    )
    db_session.add(sec_a)
    db_session.commit()

    q_a = Question(
        id=str(uuid.uuid4()),
        section_id=sec_a.id,
        paper_id=paper_a.id,
        school_id=school_a.id,
        question_text="Sample Alpha Question",
        marks=1.0
    )
    db_session.add(q_a)
    db_session.commit()

    # 5. TEST: Teacher A can access their own book and paper
    fetched_book_a = get_book(book_a.id, db_session, teacher_a)
    assert fetched_book_a.id == book_a.id

    fetched_paper_a = get_paper(paper_a.id, db_session, teacher_a)
    assert fetched_paper_a.id == paper_a.id

    # 6. TEST: Teacher B from School B attempts to access School A's book -> MUST RAISE 403 FORBIDDEN
    with pytest.raises(HTTPException) as exc_info:
        get_book(book_a.id, db_session, teacher_b)
    assert exc_info.value.status_code == 403
    assert "Forbidden" in exc_info.value.detail

    # 7. TEST: Teacher B attempts to delete School A's book -> MUST RAISE 403 FORBIDDEN
    with pytest.raises(HTTPException) as exc_info:
        delete_book(book_a.id, db_session, teacher_b)
    assert exc_info.value.status_code == 403

    # 8. TEST: Teacher B attempts to access School A's paper -> MUST RAISE 403 FORBIDDEN
    with pytest.raises(HTTPException) as exc_info:
        get_paper(paper_a.id, db_session, teacher_b)
    assert exc_info.value.status_code == 403

    # 9. TEST: Teacher B attempts to delete question in School A's paper -> MUST RAISE 403 FORBIDDEN
    with pytest.raises(HTTPException) as exc_info:
        delete_question(paper_a.id, q_a.id, db_session, teacher_b)
    assert exc_info.value.status_code == 403

    # 10. TEST: Teacher B attempts to export DOCX of School A's paper -> MUST RAISE 403 FORBIDDEN
    with pytest.raises(HTTPException) as exc_info:
        export_docx(paper_a.id, db_session, teacher_b)
    assert exc_info.value.status_code == 403
