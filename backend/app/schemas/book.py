from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.chapter import ChapterResponse

class BookBase(BaseModel):
    title: str
    subject: str
    grade: str
    language: str = "en"

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: str
    school_id: Optional[str] = None
    uploaded_by_id: Optional[str] = None
    is_global: bool = False
    file_path: str
    file_size_bytes: int
    total_pages: int
    processing_status: str
    failure_reason: Optional[str] = None
    created_at: datetime
    chapters: List[ChapterResponse] = []

    model_config = ConfigDict(from_attributes=True)

class BookProcessStatus(BaseModel):
    id: str
    processing_status: str
    total_pages: int
    chapters_count: int
    failure_reason: Optional[str] = None
