import os
import json
import uuid
import sys
from app.core.database import SessionLocal
from app.models.document_entities import Book, Chapter
from app.models.core_entities import School

def seed_db():
    db = SessionLocal()
    
    kpk_school = db.query(School).filter(School.id == "kpk-textbook-board").first()
    if not kpk_school:
        kpk_school = School(
            id="kpk-textbook-board",
            name="Khyber Pakhtunkhwa Textbook Board Peshawar",
            slug="kpk-textbook-board",
            status="active",
            is_active=True,
            subscription_tier="enterprise",
            is_paid=True
        )
        db.add(kpk_school)
        db.commit()
        db.refresh(kpk_school)

    with open("books/kpk_textbooks_catalog.json", "r", encoding="utf-8") as f:
        catalog = json.load(f)

    print(f"Loaded {len(catalog)} textbooks from catalog. Registering in database...")
    count = 0
    for b in catalog:
        existing = db.query(Book).filter(Book.title == b["title"]).first()
        if not existing:
            new_book = Book(
                id=str(uuid.uuid4()),
                school_id=kpk_school.id,
                is_global=True,
                title=b["title"],
                subject=b["subject"],
                grade=str(b["grade"]),
                language=b["language"],
                file_path=b["pdfPath"],
                file_size_bytes=int(b["fileSizeKb"] * 1024),
                processing_status="completed"
            )
            db.add(new_book)
            db.commit()
            db.refresh(new_book)

            for order, ch_title in enumerate(b["chapters"], 1):
                new_ch = Chapter(
                    id=str(uuid.uuid4()),
                    book_id=new_book.id,
                    school_id=kpk_school.id,
                    chapter_number=order,
                    title=ch_title,
                    start_page=(order - 1) * 12 + 1,
                    end_page=order * 12
                )
                db.add(new_ch)
            db.commit()
            count += 1
    print(f"Registered {count} new books in database.")
    db.close()

if __name__ == "__main__":
    seed_db()
