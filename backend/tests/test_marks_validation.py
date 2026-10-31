import pytest
from app.schemas.paper import GeneratePaperRequest, SectionConfig
from app.api.v1.papers import validate_paper_marks

def test_marks_validation_exact_match():
    req = GeneratePaperRequest(
        book_id="book-123",
        selected_chapter_ids=["chap-1"],
        title="Midterm Biology Exam",
        grade="Grade 10",
        subject="Biology",
        language="en",
        total_marks=50,
        sections=[
            SectionConfig(title="Section A: MCQs", section_type="mcq", total_questions=10, questions_to_attempt=10, marks_per_question=1.0),
            SectionConfig(title="Section B: Short Questions", section_type="short", total_questions=8, questions_to_attempt=5, marks_per_question=4.0),
            SectionConfig(title="Section C: Long Questions", section_type="long", total_questions=3, questions_to_attempt=2, marks_per_question=10.0),
        ]
    )
    res = validate_paper_marks(req)
    # Section A: 10 * 1 = 10
    # Section B: 5 * 4 = 20
    # Section C: 2 * 10 = 20
    # Total = 50
    assert res.is_valid is True
    assert res.calculated_total_marks == 50.0
    assert res.difference == 0.0
    assert len(res.warnings) == 0

def test_marks_validation_mismatch_detected():
    req = GeneratePaperRequest(
        book_id="book-123",
        selected_chapter_ids=["chap-1"],
        title="Midterm Exam Mismatch",
        grade="Grade 9",
        subject="Physics",
        language="en",
        total_marks=100,  # Configured total is 100
        sections=[
            SectionConfig(title="MCQs", section_type="mcq", total_questions=20, questions_to_attempt=20, marks_per_question=1.0), # 20
            SectionConfig(title="Short Questions", section_type="short", total_questions=10, questions_to_attempt=5, marks_per_question=4.0), # 20
        ]  # Sum = 40 != 100
    )
    res = validate_paper_marks(req)
    assert res.is_valid is False
    assert res.calculated_total_marks == 40.0
    assert res.difference == -60.0
    assert len(res.warnings) > 0
    assert "does not match the sum of sections" in res.warnings[0]
