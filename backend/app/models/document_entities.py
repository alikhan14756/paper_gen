import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=True, index=True)
    uploaded_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_global = Column(Boolean, default=False, index=True)
    
    title = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    grade = Column(String(50), nullable=False, index=True)
    language = Column(String(20), default="en")  # en, ur, bilingual
    
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=True, index=True)
    file_size_bytes = Column(Integer, default=0)
    total_pages = Column(Integer, default=0)
    
    # Lifecycle status: uploaded, extracting, ocr_processing, detecting_chapters, needs_review, ready, failed
    processing_status = Column(String(50), default="uploaded", index=True)
    failure_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    school = relationship("School", back_populates="books")
    uploader = relationship("User", back_populates="uploaded_books")
    files = relationship("BookFile", back_populates="book", cascade="all, delete-orphan")
    pages = relationship("DocumentPage", back_populates="book", cascade="all, delete-orphan", order_by="DocumentPage.page_number")
    chunks = relationship("TextChunk", back_populates="book", cascade="all, delete-orphan")
    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan", order_by="Chapter.chapter_number")
    papers = relationship("Paper", back_populates="book")
    processing_jobs = relationship("ProcessingJob", back_populates="book", cascade="all, delete-orphan")

class BookFile(Base):
    __tablename__ = "book_files"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = Column(String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=True, index=True)
    file_type = Column(String(50), nullable=False)  # original_pdf, ocr_preprocessed, extracted_cache
    storage_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    mime_type = Column(String(100), default="application/pdf")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="files")

class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = Column(String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=True, index=True)
    page_number = Column(Integer, nullable=False)  # 1-based index
    raw_text = Column(Text, nullable=False, default="")
    quality_score = Column(Float, default=1.0)
    quality_flag = Column(String(50), default="high_quality")  # high_quality, ocr_needed, scanned
    ocr_applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_book_page", "book_id", "page_number"),
    )

    book = relationship("Book", back_populates="pages")
    chunks = relationship("TextChunk", back_populates="page", cascade="all, delete-orphan")

class TextChunk(Base):
    __tablename__ = "extracted_text_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = Column(String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=True, index=True)
    page_id = Column(String(36), ForeignKey("document_pages.id", ondelete="CASCADE"), nullable=True)
    page_number = Column(Integer, nullable=False)
    chunk_index = Column(Integer, default=0)
    content = Column(Text, nullable=False)
    token_estimate = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="chunks")
    page = relationship("DocumentPage", back_populates="chunks")

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = Column(String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=True, index=True)
    
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)
    
    is_detected = Column(Boolean, default=True)
    confidence = Column(Float, default=1.0)
    detection_method = Column(String(50), default="pdf_toc_bookmarks")  # bookmarks, regex, manual
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="chapters")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    book_id = Column(String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=True)
    
    job_type = Column(String(50), nullable=False)  # pdf_extract, ocr_process, detect_chapters, export_docx
    status = Column(String(50), default="queued", index=True)  # queued, running, completed, failed
    progress_pct = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    failure_reason = Column(Text, nullable=True)
    payload_json = Column(Text, default="{}")
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    school = relationship("School", back_populates="processing_jobs")
    book = relationship("Book", back_populates="processing_jobs")
