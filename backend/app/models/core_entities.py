import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class School(Base):
    __tablename__ = "schools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    logo_url = Column(String(500), nullable=True)
    address = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    principal_name = Column(String(255), nullable=True)
    default_language = Column(String(10), default="en")  # "en", "ur", "bilingual"
    status = Column(String(50), default="active", index=True)  # active, suspended, archived
    is_active = Column(Boolean, default=True)
    
    # Quotas & Limits
    max_teachers = Column(Integer, default=20)
    max_monthly_papers = Column(Integer, default=100)
    papers_generated_this_month = Column(Integer, default=0)
    storage_quota_mb = Column(Integer, default=1024)  # 1GB default
    storage_used_bytes = Column(Integer, default=0)

    # Subscription & Free Trial
    subscription_tier = Column(String(50), default="free_trial", index=True)  # free_trial, paid, standard, premium
    is_paid = Column(Boolean, default=False, index=True)
    free_papers_per_subject = Column(Integer, default=2)

    @property
    def subscription_plan(self) -> str:
        return self.subscription_tier or "standard"

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    memberships = relationship("SchoolMembership", back_populates="school", cascade="all, delete-orphan")
    books = relationship("Book", back_populates="school", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="school", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="school", cascade="all, delete-orphan")
    subscriptions = relationship("SchoolSubscription", back_populates="school", cascade="all, delete-orphan")
    templates = relationship("ExamTemplate", back_populates="school", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="school", cascade="all, delete-orphan")
    usage_reservations = relationship("UsageReservation", back_populates="school", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="SET NULL"), nullable=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    principal_name = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True, index=True)
    role = Column(String(50), nullable=False, default="teacher")  # super_owner, super_admin, school_admin, teacher
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False, index=True)
    verification_method = Column(String(20), default="email")  # "email" | "whatsapp"
    verification_code = Column(String(32), nullable=True)
    verification_code_expires_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def is_verified(self) -> bool:
        return bool(self.is_email_verified)

    @is_verified.setter
    def is_verified(self, value: bool):
        self.is_email_verified = bool(value)

    # Relationships
    school = relationship("School", foreign_keys=[school_id])
    memberships = relationship("SchoolMembership", back_populates="user", cascade="all, delete-orphan")
    uploaded_books = relationship("Book", back_populates="uploader")
    created_papers = relationship("Paper", back_populates="creator")

class SchoolMembership(Base):
    __tablename__ = "school_memberships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False, default="teacher")  # school_admin, teacher
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("school_id", "user_id", name="uq_school_user_membership"),
    )

    school = relationship("School", back_populates="memberships")
    user = relationship("User", back_populates="memberships")

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False, default="teacher")
    token = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(String(50), default="pending")  # pending, accepted, expired, revoked
    invited_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    school = relationship("School", back_populates="invitations")

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    price_monthly = Column(Float, default=0.0)
    price_yearly = Column(Float, default=0.0)
    max_teachers = Column(Integer, default=10)
    max_monthly_papers = Column(Integer, default=50)
    max_file_size_mb = Column(Integer, default=50)
    features_json = Column(Text, default="{}")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    subscriptions = relationship("SchoolSubscription", back_populates="plan")

class SchoolSubscription(Base):
    __tablename__ = "school_subscriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(String(36), ForeignKey("subscription_plans.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String(50), default="active", index=True)  # trial, active, past_due, suspended, cancelled
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    trial_ends_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    school = relationship("School", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="PKR")
    status = Column(String(50), default="succeeded", index=True)  # pending, succeeded, failed, refunded
    payment_method = Column(String(50), default="manual")  # card, bank_transfer, jazzcash, easypaisa, manual
    transaction_id = Column(String(255), unique=True, index=True, nullable=True)
    receipt_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class VerificationOTP(Base):
    __tablename__ = "verification_otps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier = Column(String(255), index=True, nullable=False)  # email or phone
    otp_hash = Column(String(255), nullable=False)
    attempts = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=False)  # 5-minute TTL
    delivery_channel = Column(String(20), default="email")  # "email" | "whatsapp"
    status = Column(String(20), default="pending", index=True)  # pending, verified, expired, failed, locked, manual_verified
    school_name = Column(String(255), nullable=True)
    principal_name = Column(String(255), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    school_id = Column(String(36), ForeignKey("schools.id", ondelete="SET NULL"), nullable=True)
    locked_until = Column(DateTime, nullable=True)
    resend_available_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id])
    school = relationship("School", foreign_keys=[school_id])
