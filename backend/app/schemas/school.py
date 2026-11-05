from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SchoolBase(BaseModel):
    name: str
    slug: str
    contact_email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    default_language: str = "en"

class SchoolCreate(SchoolBase):
    pass

class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    default_language: Optional[str] = None
    max_teachers: Optional[int] = None
    max_monthly_papers: Optional[int] = None
    subscription_plan: Optional[str] = None
    is_active: Optional[bool] = None

class SchoolResponse(SchoolBase):
    id: str
    logo_url: Optional[str] = None
    subscription_plan: Optional[str] = "standard"
    subscription_tier: Optional[str] = "standard"
    is_active: bool
    max_teachers: int
    max_monthly_papers: int
    papers_generated_this_month: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
