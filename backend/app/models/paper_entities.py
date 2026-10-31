import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class Paper(Base):
    __tablename__ = "papers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    book_id = Column(String(36), ForeignKey("books.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    exam_type = Column(String(100), default="Final Examination")
    academic_session = Column(String(50), default="2025-2026")
    grade = Column(String(50), nullable=False)
    subject = Column(String(100), nullable=False)
    language = Column(String(20), default="en")  # en, ur, bilingual
    
    time_allowed_minutes = Column(Integer, default=120)
    total_marks = Column(Integer, default=100)
    instructions = Column(Text, nullable=True)
    
    status = Column(String(50), default="draft")  # draft, generated, reviewed, finalized
    selected_chapters_json = Column(Text, default="[]")
    
    docx_path = Column(String(500), nullable=True)
    answer_key_docx_path = Column(String(500), nullable=True)
    current_version_id = Column(String(36), nullable=True)
    verification_code = Column(String(64), unique=True, index=True, nullable=True)
    watermark_text = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    school = relationship("School", back_populates="papers")
    creator = relationship("User", back_populates="created_papers")
    book = relationship("Book", back_populates="papers")
    sections = relationship("Section", back_populates="paper", cascade="all, delete-orphan", order_by="Section.sort_order")
    versions = relationship("PaperVersion", back_populates="paper", cascade="all, delete-orphan", order_by="PaperVersion.version_number.desc()")
    answer_keys = relationship("AnswerKey", back_populates="paper", cascade="all, delete-orphan")
    ai_jobs = relationship("AIGenerationJob", back_populates="paper", cascade="all, delete-orphan")

class PaperVersion(Base):
    __tablename__ = "paper_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, default=1)
    snapshot_json = Column(Text, nullable=False)  # Immutable snapshot of complete paper, sections, questions
    change_summary = Column(String(255), default="Generated paper")
    exported_docx_path = Column(String(500), nullable=True)
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    paper = relationship("Paper", back_populates="versions")

class Section(Base):
    __tablename__ = "sections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    section_type = Column(String(50), nullable=False, default="mcq")  # mcq, short, long, fill_blanks, true_false
    sort_order = Column(Integer, default=1)
    
    total_questions = Column(Integer, default=10)
    questions_to_attempt = Column(Integer, default=10)
    marks_per_question = Column(Float, default=1.0)
    total_section_marks = Column(Float, default=10.0)
    instructions = Column(Text, nullable=True)

    paper = relationship("Paper", back_populates="sections")
    questions = relationship("Question", back_populates="section", cascade="all, delete-orphan", order_by="Question.sort_order")

class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    section_id = Column(String(36), ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    paper_id = Column(String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    
    question_number = Column(Integer, default=1)
    question_type = Column(String(50), default="mcq")
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, default="[]")  # JSON string of options for MCQs
    correct_answer = Column(Text, nullable=True)  # Answer key
    
    marks = Column(Float, default=1.0)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    blooms_level = Column(String(50), default="Understand")  # Remember, Understand, Apply, Analyze, Evaluate, Create
    source_reference = Column(String(255), nullable=True)  # e.g., "Chapter 1, Page 12"
    source_page = Column(Integer, nullable=True)
    source_excerpt = Column(Text, nullable=True)  # Exact textbook excerpt for 100% provenance verification
    confidence_score = Column(Float, default=0.95)  # AI grounding confidence score (0.0 - 1.0)
    quality_score = Column(Float, default=0.92)  # Overall quality & clarity score (0.0 - 1.0)
    duplicate_risk = Column(Float, default=0.03)  # Duplicate collision probability
    explanation = Column(Text, nullable=True)
    
    sort_order = Column(Integer, default=1)
    review_status = Column(String(50), default="pending")  # pending, reviewed, edited

    section = relationship("Section", back_populates="questions")
    versions = relationship("QuestionVersion", back_populates="question", cascade="all, delete-orphan")
    answer_key = relationship("AnswerKey", back_populates="question", uselist=False, cascade="all, delete-orphan")

class QuestionVersion(Base):
    __tablename__ = "question_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, default=1)
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, default="[]")
    correct_answer = Column(Text, nullable=True)
    marks = Column(Float, default=1.0)
    edited_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    question = relationship("Question", back_populates="versions")

class AnswerKey(Base):
    __tablename__ = "answer_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    
    solution_text = Column(Text, nullable=False)
    marking_guide = Column(Text, nullable=True)
    source_page_start = Column(Integer, nullable=True)
    source_page_end = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    paper = relationship("Paper", back_populates="answer_keys")
    question = relationship("Question", back_populates="answer_key")

class ExamTemplate(Base):
    __tablename__ = "templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    grade = Column(String(50), nullable=True)
    subject = Column(String(100), nullable=True)
    language = Column(String(20), default="en")
    total_marks = Column(Integer, default=100)
    time_allowed_minutes = Column(Integer, default=120)
    sections_config_json = Column(Text, default="[]")
    is_school_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    school = relationship("School", back_populates="templates")

class UsageReservation(Base):
    __tablename__ = "usage_reservations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reservation_token = Column(String(64), unique=True, index=True, nullable=False)
    units_reserved = Column(Integer, default=1)
    status = Column(String(50), default="reserved", index=True)  # reserved, committed, released
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    school = relationship("School", back_populates="usage_reservations")

class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    metric_name = Column(String(100), nullable=False)  # paper_generated, ocr_pages, storage_bytes
    quantity = Column(Integer, default=1)
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AIGenerationJob(Base):
    __tablename__ = "ai_generation_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    paper_id = Column(String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    provider = Column(String(50), default="gemini")  # gemini, claude, mock
    model_name = Column(String(100), default="gemini-2.5-flash")
    action_type = Column(String(50), default="generate_paper")  # generate_paper, regenerate_question
    
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    
    status = Column(String(50), default="success", index=True)  # queued, running, success, failed
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    paper = relationship("Paper", back_populates="ai_jobs")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), nullable=True, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(36), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
