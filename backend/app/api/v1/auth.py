import secrets
from typing import List
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.core.deps import get_current_user
from app.models.core_entities import User, School, SchoolMembership, SchoolSubscription, SubscriptionPlan
from app.schemas.auth import (
    Token,
    LoginRequest,
    UserResponse,
    UserCreate,
    SchoolBriefResponse,
    RegisterSchoolRequest,
    RegisterSchoolResponse,
    VerifyEmailRequest,
    ResendCodeRequest,
    RegisterTeacherRequest,
)
from app.services.email.mailer import EmailService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/schools", response_model=List[SchoolBriefResponse])
def list_registered_schools(db: Session = Depends(get_db)):
    """Lists all active schools for login/registration selection."""
    schools = db.query(School).filter(School.status == "active").order_by(School.name).all()
    return schools

@router.post("/register-school", response_model=RegisterSchoolResponse)
def register_school(req: RegisterSchoolRequest, db: Session = Depends(get_db)):
    """
    Registers a new school and creates its initial School Administrator account.
    Dispatches a 6-digit email verification code to activate the account.
    """
    existing_school = db.query(School).filter((School.slug == req.slug) | (School.name == req.school_name)).first()
    if existing_school:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A school with this name or code/slug already exists",
        )

    existing_user = db.query(User).filter(User.email == req.admin_email.strip().lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this administrator email already exists",
        )

    # 1. Create School with Free Trial defaults (2 free papers per subject)
    new_school = School(
        name=req.school_name.strip(),
        slug=req.slug.lower().strip().replace(" ", "-"),
        logo_url=req.logo_url,
        address=req.address,
        status="active",
        is_active=True,
        subscription_tier="free_trial",
        is_paid=False,
        free_papers_per_subject=2,
        max_teachers=20,
        max_monthly_papers=50,
        papers_generated_this_month=0,
    )
    db.add(new_school)
    db.flush()

    # 2. Generate 6-digit numeric verification code
    code = f"{secrets.randbelow(900000) + 100000}"

    # 3. Create Admin User (pending email verification)
    admin_user = User(
        school_id=new_school.id,
        email=req.admin_email.strip().lower(),
        hashed_password=hash_password(req.admin_password),
        full_name=req.admin_name.strip(),
        role="school_admin",
        is_active=True,
        is_email_verified=False,
        verification_code=code,
        verification_code_expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    db.add(admin_user)
    db.flush()

    # 4. Create School Membership
    membership = SchoolMembership(
        school_id=new_school.id,
        user_id=admin_user.id,
        role="school_admin",
        is_active=True,
    )
    db.add(membership)

    db.commit()
    db.refresh(admin_user)
    db.refresh(new_school)

    # 5. Dispatch email with verification code
    EmailService.send_verification_email(admin_user.email, new_school.name, code)

    return RegisterSchoolResponse(
        message="School registered successfully. A 6-digit verification code has been dispatched to your email. Please check your inbox.",
        email=admin_user.email,
        school_id=new_school.id,
        school_name=new_school.name,
    )

@router.post("/verify-email", response_model=Token)
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verifies the 6-digit email code and activates the account."""
    user = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account with this email not found.",
        )
    if user.is_email_verified:
        # Already verified, generate token and proceed
        school_name = user.school.name if user.school else None
        token_data = {
            "sub": user.id,
            "school_id": user.school_id,
            "role": user.role,
            "email": user.email,
        }
        access_token = create_access_token(token_data)
        user_resp = UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            school_id=user.school_id,
            school_name=school_name,
            is_active=user.is_active,
            is_email_verified=True,
        )
        return Token(access_token=access_token, token_type="bearer", user=user_resp)

    if not user.verification_code or user.verification_code.strip() != req.code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please check your email and try again.",
        )

    if user.verification_code_expires_at:
        expires = user.verification_code_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new code.",
            )

    user.is_email_verified = True
    user.verification_code = None
    user.verification_code_expires_at = None
    db.commit()
    db.refresh(user)

    school_name = user.school.name if user.school else None
    token_data = {
        "sub": user.id,
        "school_id": user.school_id,
        "role": user.role,
        "email": user.email,
    }
    access_token = create_access_token(token_data)

    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        school_id=user.school_id,
        school_name=school_name,
        is_active=user.is_active,
        is_email_verified=True,
    )
    return Token(access_token=access_token, token_type="bearer", user=user_resp)

@router.post("/resend-code")
def resend_verification_code(req: ResendCodeRequest, db: Session = Depends(get_db)):
    """Resends a fresh 6-digit verification code to the registered email."""
    user = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email.",
        )
    if user.is_email_verified:
        return {"message": "Email is already verified. You can sign in directly."}

    code = f"{secrets.randbelow(900000) + 100000}"
    user.verification_code = code
    user.verification_code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    db.commit()

    school_name = user.school.name if user.school else "Your School"
    EmailService.send_verification_email(user.email, school_name, code)

    return {
        "message": "New verification code has been dispatched to your email. Please check your inbox.",
        "email": user.email,
    }

@router.post("/register-teacher", response_model=Token)
def register_teacher(req: RegisterTeacherRequest, db: Session = Depends(get_db)):
    """Registers a teacher under an existing school."""
    school = db.query(School).filter(School.id == req.school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified school not found",
        )

    # Check school teacher limit
    teacher_count = db.query(User).filter(User.school_id == req.school_id, User.role == "teacher").count()
    if teacher_count >= school.max_teachers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This school has reached its limit of {school.max_teachers} teachers. Contact school administrator.",
        )

    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists",
        )

    teacher = User(
        school_id=school.id,
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role="teacher",
        is_active=True,
    )
    db.add(teacher)
    db.flush()

    membership = SchoolMembership(
        school_id=school.id,
        user_id=teacher.id,
        role="teacher",
        is_active=True,
    )
    db.add(membership)
    db.commit()
    db.refresh(teacher)

    token_data = {
        "sub": teacher.id,
        "school_id": teacher.school_id,
        "role": teacher.role,
        "email": teacher.email,
    }
    access_token = create_access_token(token_data)

    user_resp = UserResponse(
        id=teacher.id,
        email=teacher.email,
        full_name=teacher.full_name,
        role=teacher.role,
        school_id=teacher.school_id,
        school_name=school.name,
        is_active=teacher.is_active,
    )
    return Token(access_token=access_token, token_type="bearer", user=user_resp)

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact your school administrator.",
        )
    if not user.is_email_verified and user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address not verified. Please enter the 6-digit verification code sent to your email to activate your account.",
            headers={"X-Error-Code": "EMAIL_NOT_VERIFIED"}
        )
    if user.school and (user.school.status == "suspended" or not user.school.is_active) and user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School account has been suspended. Please contact platform administration.",
        )

    school_name = user.school.name if user.school else None
    token_data = {
        "sub": user.id,
        "school_id": user.school_id,
        "role": user.role,
        "email": user.email,
    }
    access_token = create_access_token(token_data)

    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        school_id=user.school_id,
        school_name=school_name,
        is_active=user.is_active,
    )

    return Token(access_token=access_token, token_type="bearer", user=user_resp)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    school_name = current_user.school.name if current_user.school else None
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        school_id=current_user.school_id,
        school_name=school_name,
        is_active=current_user.is_active,
    )
