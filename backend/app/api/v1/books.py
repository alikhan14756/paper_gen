import os
import re
import uuid
import urllib.parse
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.core_entities import User
from app.models.document_entities import Book, BookFile, DocumentPage, TextChunk, Chapter, ProcessingJob
from app.schemas.book import BookResponse, BookProcessStatus
from app.schemas.chapter import ChapterResponse, ChapterCreate, ChapterUpdate
from app.services.document.extractor import DocumentExtractor
from app.services.chapter.detector import ChapterDetector

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/upload", response_model=BookResponse)
async def upload_book(
    title: str = Form(...),
    subject: str = Form(...),
    grade: str = Form(...),
    language: str = Form("en"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.school_id:
        raise HTTPException(status_code=400, detail="User must be associated with a school to upload books")

    # Read and validate PDF magic header
    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size ({settings.MAX_UPLOAD_SIZE_MB}MB)")

    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF document")

    file_hash = DocumentExtractor.calculate_file_hash(file_bytes)

    # Check for duplicate in school
    existing = db.query(Book).filter(Book.school_id == current_user.school_id, Book.file_hash == file_hash).first()
    if existing:
        return existing

    book_id = str(uuid.uuid4())
    safe_orig = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', os.path.basename(file.filename or "book.pdf"))
    safe_filename = f"{book_id}_{safe_orig}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    cache_path = os.path.join(settings.UPLOAD_DIR, f"{book_id}_cache.json")

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    book = Book(
        id=book_id,
        school_id=current_user.school_id,
        uploaded_by_id=current_user.id,
        title=title,
        subject=subject,
        grade=grade,
        language=language,
        file_path=file_path,
        file_hash=file_hash,
        file_size_bytes=len(file_bytes),
        processing_status="extracting",
    )
    db.add(book)

    # Create BookFile record
    book_file = BookFile(
        book_id=book.id,
        school_id=current_user.school_id,
        file_type="original_pdf",
        storage_path=file_path,
        file_size_bytes=len(file_bytes),
        mime_type="application/pdf",
    )
    db.add(book_file)

    # Create ProcessingJob record
    job = ProcessingJob(
        school_id=current_user.school_id,
        user_id=current_user.id,
        book_id=book.id,
        job_type="pdf_extract",
        status="running",
        progress_pct=10,
        started_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(book)

    # Extract text using PyMuPDF
    try:
        extraction_res = DocumentExtractor.extract_pdf_pages(file_path, cache_path)
        book.total_pages = extraction_res["total_pages"]
        job.progress_pct = 50

        # Store DocumentPage and TextChunk records
        for p_data in extraction_res["pages"]:
            doc_page = DocumentPage(
                book_id=book.id,
                school_id=current_user.school_id,
                page_number=p_data["page_number"],
                raw_text=p_data["text"],
                quality_score=p_data["quality_score"],
                quality_flag=p_data["quality_flag"],
                ocr_applied=False,
            )
            db.add(doc_page)
            db.flush()

            # Store chunk
            chunk = TextChunk(
                book_id=book.id,
                school_id=current_user.school_id,
                page_id=doc_page.id,
                page_number=p_data["page_number"],
                chunk_index=0,
                content=p_data["text"],
                token_estimate=len(p_data["text"].split()),
            )
            db.add(chunk)

        # Run Chapter Detection
        job.progress_pct = 80
        detected_chaps = ChapterDetector.detect_chapters(file_path, extraction_res["pages"])

        for c_data in detected_chaps:
            chapter = Chapter(
                book_id=book.id,
                school_id=current_user.school_id,
                chapter_number=c_data["chapter_number"],
                title=c_data["title"],
                start_page=c_data["start_page"],
                end_page=c_data["end_page"],
                is_detected=c_data.get("is_detected", True),
                confidence=c_data.get("confidence", 1.0),
                detection_method=c_data.get("detection_method", "heuristic"),
            )
            db.add(chapter)

        book.processing_status = "ready"
        job.status = "completed"
        job.progress_pct = 100
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(book)
    except Exception as e:
        book.processing_status = "failed"
        book.failure_reason = str(e)
        job.status = "failed"
        job.failure_reason = str(e)
        db.commit()
        db.refresh(book)
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")

    return book

@router.get("", response_model=List[BookResponse])
def list_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Book)
    if current_user.role != "super_admin":
        query = query.filter((Book.school_id == current_user.school_id) | (Book.is_global == True))
    return query.order_by(Book.is_global.desc(), Book.grade.asc(), Book.created_at.desc()).all()

@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if current_user.role != "super_admin" and book.school_id != current_user.school_id and not book.is_global:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot access other schools' books")
    return book

@router.get("/{book_id}/download-pdf")
def download_book_pdf(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allows downloading the authentic textbook PDF."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if current_user.role != "super_admin" and book.school_id != current_user.school_id and not book.is_global:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot download this textbook")

    if not book.file_path or not os.path.exists(book.file_path):
        raise HTTPException(status_code=404, detail="PDF textbook file not found on server")

    ascii_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', book.title)[:40]
    safe_filename = f"{ascii_title}_KPK_Textbook.pdf"
    encoded_filename = urllib.parse.quote(f"{book.title}.pdf")

    headers = {
        "Content-Disposition": f'attachment; filename="{safe_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    }
    return FileResponse(
        path=book.file_path,
        media_type="application/pdf",
        headers=headers,
    )

@router.post("/{book_id}/chapters", response_model=ChapterResponse)
def add_chapter(
    book_id: str,
    chapter_data: ChapterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if current_user.role != "super_admin" and book.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Validate page boundaries
    if chapter_data.start_page < 1:
        raise HTTPException(status_code=400, detail="Start page must be at least 1")
    if chapter_data.end_page < chapter_data.start_page:
        raise HTTPException(status_code=400, detail="End page cannot be less than start page")
    if book.total_pages > 0 and chapter_data.end_page > book.total_pages:
        raise HTTPException(status_code=400, detail=f"End page cannot exceed total book pages ({book.total_pages})")

    chapter = Chapter(
        book_id=book.id,
        school_id=current_user.school_id,
        chapter_number=chapter_data.chapter_number,
        title=chapter_data.title,
        start_page=chapter_data.start_page,
        end_page=chapter_data.end_page,
        is_detected=False,
        confidence=1.0,
        detection_method="manual",
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter

@router.patch("/{book_id}/chapters/{chapter_id}", response_model=ChapterResponse)
def update_chapter(
    book_id: str,
    chapter_id: str,
    chapter_data: ChapterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id, Chapter.book_id == book_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    if current_user.role != "super_admin" and chapter.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    new_start = chapter_data.start_page if chapter_data.start_page is not None else chapter.start_page
    new_end = chapter_data.end_page if chapter_data.end_page is not None else chapter.end_page
    if new_start < 1:
        raise HTTPException(status_code=400, detail="Start page must be at least 1")
    if new_end < new_start:
        raise HTTPException(status_code=400, detail="End page cannot be less than start page")

    for k, v in chapter_data.model_dump(exclude_unset=True).items():
        setattr(chapter, k, v)
    chapter.is_detected = False

    db.commit()
    db.refresh(chapter)
    return chapter

@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if current_user.role != "super_admin" and book.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(book)
    db.commit()
    return None
