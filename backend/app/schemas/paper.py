from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# --- Question Schemas ---
class QuestionItem(BaseModel):
    id: Optional[str] = None
    question_number: int
    question_type: str = "mcq"  # mcq, short, long, fill_blanks, true_false
    question_text: str
    options: List[str] = []
    correct_answer: Optional[str] = None
    marks: float = 1.0
    difficulty: str = "medium"  # easy, medium, hard
    blooms_level: str = "Understand"  # Remember, Understand, Apply, Analyze, Evaluate, Create
    source_reference: Optional[str] = None
    source_page: Optional[int] = None
    source_excerpt: Optional[str] = None  # Exact textbook sentence/paragraph grounding this question
    confidence_score: float = 0.95
    quality_score: float = 0.92
    duplicate_risk: float = 0.03
    explanation: Optional[str] = None
    sort_order: int = 1
    review_status: str = "pending"

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    marks: Optional[float] = None
    difficulty: Optional[str] = None
    blooms_level: Optional[str] = None
    source_reference: Optional[str] = None
    source_page: Optional[int] = None
    source_excerpt: Optional[str] = None
    confidence_score: Optional[float] = None
    quality_score: Optional[float] = None
    duplicate_risk: Optional[float] = None
    explanation: Optional[str] = None
    sort_order: Optional[int] = None
    review_status: Optional[str] = None

class QuestionResponse(QuestionItem):
    id: str
    section_id: str

    model_config = ConfigDict(from_attributes=True)

# --- Section Schemas ---
class SectionConfig(BaseModel):
    id: Optional[str] = None
    title: str
    section_type: str = "mcq"  # mcq, short, long
    sort_order: int = 1
    total_questions: int = 10
    questions_to_attempt: int = 10
    marks_per_question: float = 1.0
    total_section_marks: float = 10.0
    instructions: Optional[str] = None

class SectionResponse(SectionConfig):
    id: str
    paper_id: str
    questions: List[QuestionResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Paper Schemas ---
class PaperCreate(BaseModel):
    title: str
    book_id: Optional[str] = None
    exam_type: str = "Final Examination"
    academic_session: str = "2025-2026"
    grade: str
    subject: str
    language: str = "en"  # en, ur, bilingual
    time_allowed_minutes: int = 120
    total_marks: int = 100
    instructions: Optional[str] = None
    selected_chapter_ids: List[str] = []
    sections: List[SectionConfig] = []

class PaperUpdate(BaseModel):
    title: Optional[str] = None
    exam_type: Optional[str] = None
    academic_session: Optional[str] = None
    grade: Optional[str] = None
    subject: Optional[str] = None
    language: Optional[str] = None
    time_allowed_minutes: Optional[int] = None
    total_marks: Optional[int] = None
    instructions: Optional[str] = None
    status: Optional[str] = None

class PaperResponse(BaseModel):
    id: str
    school_id: str
    created_by_id: Optional[str] = None
    book_id: Optional[str] = None
    title: str
    exam_type: str
    academic_session: str
    grade: str
    subject: str
    language: str
    time_allowed_minutes: int
    total_marks: int
    instructions: Optional[str] = None
    status: str
    selected_chapters: List[str] = []
    docx_path: Optional[str] = None
    answer_key_docx_path: Optional[str] = None
    verification_code: Optional[str] = None
    watermark_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    sections: List[SectionResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Marks Validation Schema ---
class SectionMarksBreakdown(BaseModel):
    section_title: str
    total_questions: int
    questions_to_attempt: int
    marks_per_question: float
    calculated_section_marks: float

class MarksValidationResult(BaseModel):
    is_valid: bool
    configured_total_marks: float
    calculated_total_marks: float
    difference: float
    breakdown: List[SectionMarksBreakdown]
    warnings: List[str] = []

# --- AI Generation Request ---
class GeneratePaperRequest(BaseModel):
    book_id: str
    selected_chapter_ids: List[str]
    title: str
    exam_type: str = "Midterm Examination"
    academic_session: str = "2025-2026"
    grade: str
    subject: str
    language: str = "en"  # en, ur, bilingual
    time_allowed_minutes: int = 120
    total_marks: int = 100
    instructions: Optional[str] = "Attempt all questions. Choose the most appropriate option for Section A."
    sections: List[SectionConfig]
    difficulty_distribution: Optional[dict[str, int]] = Field(
        default_factory=lambda: {"easy": 40, "medium": 40, "hard": 20}
    )

class RegenerateSingleQuestionRequest(BaseModel):
    paper_id: str
    section_id: str
    question_id: str
    custom_instruction: Optional[str] = None

# --- Automatic Examination Blueprint Schemas ---
class ChapterBlueprintItem(BaseModel):
    chapter_id: str
    chapter_title: str
    weightage_pct: float
    marks_allocated: int
    mcq_count: int
    short_count: int
    long_count: int
    blooms_focus: str  # Remember, Understand, Apply, Analyze

class BlueprintRequest(BaseModel):
    grade: str
    subject: str
    total_marks: int = 50
    selected_chapter_ids: List[str]

class BlueprintResponse(BaseModel):
    total_marks: int
    subject: str
    grade: str
    chapters: List[ChapterBlueprintItem]
    blooms_summary: dict[str, int]
    difficulty_summary: dict[str, int]
