from typing import Optional
from pydantic import BaseModel, ConfigDict

class ChapterBase(BaseModel):
    chapter_number: int
    title: str
    start_page: int
    end_page: int

class ChapterCreate(ChapterBase):
    pass

class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    chapter_number: Optional[int] = None

class ChapterResponse(ChapterBase):
    id: str
    book_id: str
    is_detected: bool
    confidence: float
    detection_method: str

    model_config = ConfigDict(from_attributes=True)
