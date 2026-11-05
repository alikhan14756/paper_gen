import uuid
from typing import List
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_super_admin, require_school_admin_or_super
from app.core.security import hash_password, ROLE_SUPER_OWNER, ROLE_SUPER_ADMIN, ROLE_SCHOOL_ADMIN
from app.models.core_entities import School, User, SchoolMembership, Invitation, SchoolSubscription, SubscriptionPlan
from app.models.paper_entities import AuditLog
from app.schemas.school import SchoolCreate, SchoolUpdate, SchoolResponse
from sqlalchemy import func

router = APIRouter(prefix="/schools", tags=["Schools"])

class InviteTeacherRequest(BaseModel):
    email: EmailStr
    role: str = "teacher"

class RegisterSchoolWithAdminRequest(BaseModel):
    name: str
    username: str
    password: str
    principal_name: str = "Principal"
    phone_number: str = "+923215423874"
    quota: str = "Unlimited"

class InvitationResponse(BaseModel):
    id: str
    school_id: str
    email: str
    role: str
    status: str
    token: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[SchoolResponse])
def list_schools(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    schools = db.query(School).all()
    return schools

@router.post("", response_model=SchoolResponse)
def create_school(
    data: SchoolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    existing = db.query(School).filter(School.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="A school with this slug already exists")
    
    school = School(**data.model_dump())
    db.add(school)
    db.commit()
    db.refresh(school)
    return school

@router.post("/register-with-admin")
def register_school_with_admin(
    data: RegisterSchoolWithAdminRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    clean_username = data.username.strip().lower()
    clean_name = data.name.strip()
    clean_password = data.password.strip()

    if not clean_username or not clean_password or not clean_name:
        raise HTTPException(status_code=400, detail="Name, username, and password are required.")

    if db.query(User).filter(func.lower(User.username) == clean_username).first():
        raise HTTPException(status_code=400, detail=f"Username '{clean_username}' is already in use.")

    base_slug = "".join(c for c in clean_name.lower().replace(" ", "-") if c.isalnum() or c == "-").strip("-") or clean_username
    if db.query(School).filter(School.slug == base_slug).first():
        base_slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"

    school = School(
        name=clean_name,
        slug=base_slug,
        principal_name=data.principal_name,
        phone_number=data.phone_number,
        status="active",
        is_active=True,
        subscription_tier="paid" if data.quota == "Unlimited" else "standard",
        is_paid=True,
        free_papers_per_subject=1000,
        max_teachers=50,
        max_monthly_papers=5000 if data.quota == "Unlimited" else 100,
        papers_generated_this_month=0,
    )
    db.add(school)
    db.flush()

    admin_user = User(
        school_id=school.id,
        username=clean_username,
        email=f"{clean_username}@{base_slug}.examforge.edu.pk",
        hashed_password=hash_password(clean_password),
        full_name=f"{clean_name} Administrator",
        principal_name=data.principal_name,
        phone_number=data.phone_number,
        role="school_admin",
        is_active=True,
        is_email_verified=True,
        verification_method="manual",
    )
    db.add(admin_user)
    db.flush()

    membership = SchoolMembership(
        school_id=school.id,
        user_id=admin_user.id,
        role="school_admin",
        is_active=True,
    )
    db.add(membership)

    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.slug == "premium").first() or db.query(SubscriptionPlan).first()
    sub = SchoolSubscription(
        school_id=school.id,
        plan_id=plan.id if plan else None,
        status="active",
        current_period_start=datetime.now(timezone.utc),
        current_period_end=datetime.now(timezone.utc) + timedelta(days=365 * 5),
    )
    db.add(sub)

    db.commit()
    db.refresh(school)
    db.refresh(admin_user)

    return {
        "success": True,
        "school_id": school.id,
        "school_name": school.name,
        "username": admin_user.username,
        "role": admin_user.role,
        "quota": data.quota,
    }

@router.get("/{school_id}", response_model=SchoolResponse)
def get_school(
    school_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (ROLE_SUPER_ADMIN, ROLE_SUPER_OWNER) and current_user.school_id != school_id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot access other schools")
    
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school

@router.patch("/{school_id}", response_model=SchoolResponse)
def update_school(
    school_id: str,
    data: SchoolUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_school_admin_or_super)
):
    if current_user.role not in (ROLE_SUPER_ADMIN, ROLE_SUPER_OWNER) and current_user.school_id != school_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    update_dict = data.model_dump(exclude_unset=True)
    if current_user.role not in (ROLE_SUPER_ADMIN, ROLE_SUPER_OWNER):
        # Disallow quota & subscription tampering by school admins
        protected_fields = ["max_teachers", "max_monthly_papers", "subscription_plan", "is_active", "status"]
        for pf in protected_fields:
            update_dict.pop(pf, None)

    for field, value in update_dict.items():
        setattr(school, field, value)

    db.commit()
    db.refresh(school)
    return school

@router.post("/{school_id}/invitations", response_model=InvitationResponse)
def invite_teacher(
    school_id: str,
    data: InviteTeacherRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_school_admin_or_super)
):
    if current_user.role not in (ROLE_SUPER_ADMIN, ROLE_SUPER_OWNER) and current_user.school_id != school_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    # Check teacher quota
    current_teachers = db.query(SchoolMembership).filter(SchoolMembership.school_id == school_id).count()
    if current_teachers >= school.max_teachers:
        raise HTTPException(
            status_code=400,
            detail=f"School teacher limit reached ({current_teachers}/{school.max_teachers})"
        )

    invitation = Invitation(
        school_id=school_id,
        email=data.email,
        role=data.role,
        token=str(uuid.uuid4()),
        status="pending",
        invited_by_id=current_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation

@router.get("/{school_id}/billing-analytics")
def get_school_billing_analytics(
    school_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_school_admin_or_super),
):
    """Provides enterprise billing usage and quota analytics for the school."""
    if current_user.role not in (ROLE_SUPER_ADMIN, ROLE_SUPER_OWNER) and current_user.school_id != school_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    sub = db.query(SchoolSubscription).filter(SchoolSubscription.school_id == school_id).first()
    plan_name = sub.plan.name if (sub and sub.plan) else "Standard School Plan"
    plan_price = sub.plan.price_monthly if (sub and sub.plan) else 15000.0

    teacher_count = db.query(SchoolMembership).filter(SchoolMembership.school_id == school_id).count()
    paper_utilization_pct = round((school.papers_generated_this_month / max(1, school.max_monthly_papers)) * 100, 1)

    return {
        "school_id": school.id,
        "school_name": school.name,
        "subscription_tier": plan_name,
        "monthly_fee_pkr": plan_price,
        "subscription_status": sub.status if sub else "active",
        "quota_summary": {
            "papers_generated_this_month": school.papers_generated_this_month,
            "max_monthly_papers": school.max_monthly_papers,
            "paper_utilization_pct": paper_utilization_pct,
            "active_teachers": teacher_count,
            "max_teachers": school.max_teachers,
            "storage_used_mb": round((school.storage_used_bytes or 0) / (1024 * 1024), 2),
            "storage_quota_mb": school.storage_quota_mb or 1024,
        },
        "billing_cycle": {
            "renews_on": (sub.current_period_end.strftime("%B %d, %Y")) if sub else "Annual Renewal",
            "reset_day_of_month": 1,
        }
    }

@router.post("/{school_id}/reset-monthly-quota")
def reset_monthly_quota(
    school_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    """Super Admin / Automated Job endpoint to reset monthly paper count at cycle end."""
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    old_count = school.papers_generated_this_month
    school.papers_generated_this_month = 0

    audit = AuditLog(
        school_id=school.id,
        user_id=current_user.id,
        action="reset_monthly_paper_quota",
        resource_type="school",
        resource_id=school.id,
        details=f"Monthly paper generation quota reset from {old_count} to 0 by {current_user.email}"
    )
    db.add(audit)
    db.commit()

    return {"message": "Monthly quota reset successfully", "previous_papers_generated": old_count}

@router.get("/{school_id}/audit-logs")
def get_school_audit_logs(
    school_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_school_admin_or_super),
):
    """Chronological audit trail of high-security actions for the school."""
    if current_user.role not in (ROLE_SUPER_ADMIN, ROLE_SUPER_OWNER) and current_user.school_id != school_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.school_id == school_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": l.id,
            "action": l.action,
            "resource_type": l.resource_type,
            "resource_id": l.resource_id,
            "details": l.details,
            "timestamp": l.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        for l in logs
    ]

@router.post("/{school_id}/upgrade-subscription")
def upgrade_school_subscription(
    school_id: str,
    tier: str = "paid",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upgrades a school from free trial to paid subscription, allowing unlimited subject generation.
    Can be executed by Super Admin or the school administrator.
    """
    if current_user.role not in (ROLE_SUPER_ADMIN, ROLE_SUPER_OWNER) and current_user.school_id != school_id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot upgrade other schools' subscriptions")

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    school.subscription_tier = tier
    school.is_paid = True
    school.max_monthly_papers = 500

    audit = AuditLog(
        school_id=school.id,
        user_id=current_user.id,
        action="upgrade_subscription",
        resource_type="school",
        resource_id=school.id,
        details=f"Subscription upgraded to {tier} (Paid=True) by {current_user.email}"
    )
    db.add(audit)
    db.commit()
    db.refresh(school)

    return {
        "message": f"School '{school.name}' subscription successfully upgraded to '{tier}'. Unlimited subject generation is now active.",
        "school_id": school.id,
        "subscription_tier": school.subscription_tier,
        "is_paid": school.is_paid,
        "max_monthly_papers": school.max_monthly_papers,
    }
