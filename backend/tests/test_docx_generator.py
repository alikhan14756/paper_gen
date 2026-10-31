import os
import pytest
from docx import Document
from app.services.export.docx_generator import DocxGenerator
from app.core.config import settings

def test_generate_english_exam_docx(tmp_path):
    output_docx = str(tmp_path / "test_english_exam.docx")
    paper_data = {
        "title": "Grade 10 Physics Annual Examination",
        "academic_session": "2025-2026",
        "grade": "10",
        "subject": "Physics",
        "language": "en",
        "time_allowed_minutes": 180,
        "total_marks": 75,
        "instructions": "Attempt all sections. Calculator is permitted.",
        "sections": [
            {
                "title": "Section A — Multiple Choice Questions",
                "section_type": "mcq",
                "total_section_marks": 12,
                "instructions": "Choose the best option for each question.",
                "questions": [
                    {
                        "question_text": "What is the SI unit of electric potential?",
                        "options": ["A. Ampere", "B. Volt", "C. Ohm", "D. Joule"],
                        "correct_answer": "B. Volt",
                        "marks": 1,
                        "question_type": "mcq",
                        "source_reference": "Chapter 14, Page 85",
                        "explanation": "Potential difference is measured in Volts (V = W/Q)."
                    }
                ]
            },
            {
                "title": "Section B — Short Questions",
                "section_type": "short",
                "total_section_marks": 30,
                "instructions": "Attempt any 5 questions.",
                "questions": [
                    {
                        "question_text": "State Ohm's Law and write its mathematical formula.",
                        "options": [],
                        "correct_answer": "V = IR where V is potential, I is current, R is resistance.",
                        "marks": 3,
                        "question_type": "short",
                        "source_reference": "Chapter 14, Page 89",
                        "explanation": "1 mark for statement, 2 marks for formula and variables."
                    }
                ]
            }
        ]
    }
    school_info = {"name": "Lahore Grammar School"}

    res_path = DocxGenerator.generate_exam_docx(paper_data, school_info, output_docx, include_answer_key=True)
    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 1000

    # Verify docx content
    doc = Document(res_path)
    full_text = "\n".join([p.text for p in doc.paragraphs])
    assert "LAHORE GRAMMAR SCHOOL" in full_text
    assert "Physics" in full_text
    assert "Ohm's Law" in full_text
    assert "OFFICIAL ANSWER KEY" in full_text
    assert "B. Volt" in full_text

def test_generate_urdu_exam_docx(tmp_path):
    output_docx = str(tmp_path / "test_urdu_exam.docx")
    paper_data = {
        "title": "سالانہ امتحان مطالعہ پاکستان",
        "academic_session": "2025-2026",
        "grade": "جماعت نہم",
        "subject": "مطالعہ پاکستان",
        "language": "ur",
        "time_allowed_minutes": 120,
        "total_marks": 50,
        "instructions": "تمام سوالات لازمی ہیں۔ سوالات کے جوابات خوش خط تحریر کریں۔",
        "sections": [
            {
                "title": "حصہ اول — کثیر الانتخابی سوالات",
                "section_type": "mcq",
                "total_section_marks": 10,
                "instructions": "درست جواب کا انتخاب کریں۔",
                "questions": [
                    {
                        "question_text": "قرارداد پاکستان کب منظور ہوئی؟",
                        "options": ["الف) 1930", "ب) 1940", "ج) 1946", "د) 1947"],
                        "correct_answer": "ب) 1940",
                        "marks": 1,
                        "question_type": "mcq",
                        "source_reference": "باب نمبر 2، صفحہ 15",
                        "explanation": "23 مارچ 1940 کو لاہور میں منظور ہوئی۔"
                    }
                ]
            }
        ]
    }
    school_info = {"name": "گورنمنٹ ماڈل ہائی سکول لاہور"}

    res_path = DocxGenerator.generate_exam_docx(paper_data, school_info, output_docx, include_answer_key=True)
    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 1000

    doc = Document(res_path)
    full_text = "\n".join([p.text for p in doc.paragraphs])
    assert "گورنمنٹ ماڈل ہائی سکول لاہور" in full_text
    assert "قرارداد پاکستان" in full_text
    assert "1940" in full_text
    assert "◯" in full_text  # Verify fill bubbles
    assert "صفحہ" not in full_text  # Verify page numbers stripped

def test_student_paper_excludes_answer_key(tmp_path):
    output_docx = str(tmp_path / "student_only_exam.docx")
    paper_data = {
        "title": "Grade 9 Chemistry Midterm",
        "grade": "9",
        "subject": "Chemistry",
        "language": "en",
        "total_marks": 25,
        "sections": [
            {
                "title": "Section A",
                "section_type": "mcq",
                "total_section_marks": 5,
                "questions": [
                    {
                        "question_text": "What is the atomic number of Carbon?",
                        "options": ["4", "6", "12", "14"],
                        "correct_answer": "6",
                        "marks": 1,
                        "explanation": "Carbon has 6 protons."
                    }
                ]
            }
        ]
    }
    school_info = {"name": "Cadet College Kohat"}
    res_path = DocxGenerator.generate_exam_docx(paper_data, school_info, output_docx, include_answer_key=False)
    doc = Document(res_path)
    full_text = "\n".join([p.text for p in doc.paragraphs])
    assert "CONFIDENTIAL MARKING SCHEME" not in full_text
    assert "OFFICIAL ANSWER KEY" not in full_text
    assert "◯" in full_text

def test_generate_standalone_confidential_answer_key(tmp_path):
    output_docx = str(tmp_path / "standalone_answer_key.docx")
    paper_data = {
        "title": "Grade 9 Chemistry Midterm",
        "grade": "9",
        "subject": "Chemistry",
        "language": "en",
        "total_marks": 25,
        "sections": [
            {
                "title": "Section A",
                "section_type": "mcq",
                "total_section_marks": 5,
                "questions": [
                    {
                        "question_text": "What is the atomic number of Carbon?",
                        "options": ["4", "6", "12", "14"],
                        "correct_answer": "6",
                        "marks": 1,
                        "explanation": "Carbon has 6 protons."
                    }
                ]
            }
        ]
    }
    school_info = {"name": "Cadet College Kohat"}
    res_path = DocxGenerator.generate_confidential_answer_key_docx(paper_data, school_info, output_docx)
    assert os.path.exists(res_path)
    doc = Document(res_path)
    full_text = "\n".join([p.text for p in doc.paragraphs])
    assert "OFFICIAL MARKING SCHEME & ANSWER KEY" in full_text
    assert "CONFIDENTIAL" in full_text
    assert "6" in full_text
