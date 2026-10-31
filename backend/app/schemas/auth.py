from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserResponse"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    school_id: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    school_id: Optional[str] = None
    role: str = "teacher"

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    school_id: Optional[str] = None
    school_name: Optional[str] = None
    is_active: bool
    is_email_verified: bool = True

    model_config = ConfigDict(from_attributes=True)

class SchoolBriefResponse(BaseModel):
    id: str
    name: str
    slug: str
    logo_url: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RegisterSchoolRequest(BaseModel):
    school_name: str
    slug: str
    logo_url: Optional[str] = None
    address: Optional[str] = None
    admin_name: str
    admin_email: EmailStr
    admin_password: str

class RegisterTeacherRequest(BaseModel):
    school_id: str
    full_name: str
    email: EmailStr
    password: str

class RegisterSchoolResponse(BaseModel):
    message: str
    email: EmailStr
    school_id: str
    school_name: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str

class ResendCodeRequest(BaseModel):
    email: EmailStr

Token.model_rebuild()
