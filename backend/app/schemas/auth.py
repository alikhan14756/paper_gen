from typing import Optional, List
from datetime import datetime
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
    username_or_email: Optional[str] = None
    email: Optional[str] = None
    password: str

class UserCreate(BaseModel):
    email: str
    username: Optional[str] = None
    password: str
    full_name: str
    school_id: Optional[str] = None
    role: str = "teacher"

class UserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    full_name: str
    role: str
    school_id: Optional[str] = None
    school_name: Optional[str] = None
    phone_number: Optional[str] = None
    principal_name: Optional[str] = None
    is_active: bool
    is_email_verified: bool = True
    is_verified: bool = True

    model_config = ConfigDict(from_attributes=True)

class OwnerCreateSchoolRequest(BaseModel):
    school_name: str
    username: str
    password: str
    principal_name: Optional[str] = "Principal"
    phone_number: Optional[str] = "+923215423874"
    quota: Optional[str] = "Unlimited"

class OwnerCreateSchoolResponse(BaseModel):
    success: bool
    message: str
    school_id: str
    school_name: str
    username: str
    role: str
    quota: str
    createdAt: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class SchoolBriefResponse(BaseModel):
    id: str
    name: str
    slug: str
    logo_url: Optional[str] = None
    address: Optional[str] = None
    principal_name: Optional[str] = None
    phone_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RegisterSchoolRequest(BaseModel):
    school_name: str
    slug: str
    logo_url: Optional[str] = None
    address: Optional[str] = None
    admin_name: str
    admin_email: EmailStr
    admin_password: str
    phone_number: Optional[str] = None
    verification_method: Optional[str] = "email"

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

# Automatic OTP Architecture Schemas
class RegisterInitiateRequest(BaseModel):
    school_name: str
    principal_name: str
    email: EmailStr
    phone_number: str
    password: str
    verification_method: str = "email"  # "email" | "whatsapp"

class RegisterInitiateResponse(BaseModel):
    message: str
    identifier: str
    school_id: str
    user_id: str
    school_name: str
    principal_name: str
    verification_method: str
    resend_cooldown_seconds: int = 60
    expires_in_seconds: int = 300
    session_code: Optional[str] = None

class VerifyOTPRequest(BaseModel):
    identifier: str
    otp_code: str

class ResendOTPRequest(BaseModel):
    identifier: str

class ResendOTPResponse(BaseModel):
    message: str
    identifier: str
    resend_cooldown_seconds: int = 60
    expires_in_seconds: int = 300

class OwnerVerificationItem(BaseModel):
    id: str
    identifier: str
    school_name: Optional[str] = None
    principal_name: Optional[str] = None
    delivery_channel: str
    status: str
    attempts: int
    created_at: str
    expires_at: str
    is_locked: bool
    user_id: Optional[str] = None
    school_id: Optional[str] = None

class OwnerVerificationsResponse(BaseModel):
    items: List[OwnerVerificationItem]
    total_schools: int
    verified_schools: int
    pending_verifications: int
    locked_accounts: int
