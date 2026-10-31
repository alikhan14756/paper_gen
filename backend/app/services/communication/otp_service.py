import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.core_entities import VerificationOTP, User, School
from app.services.email.mailer import EmailService
from app.services.communication.whatsapp import WhatsAppService

class OTPService:
    TTL_MINUTES = 5
    COOLDOWN_SECONDS = 60
    MAX_ATTEMPTS = 3
    LOCKOUT_MINUTES = 30

    @classmethod
    def generate_numeric_otp(cls, length: int = 6) -> str:
        """Generates a cryptographically secure numeric OTP."""
        return f"{secrets.randbelow(900000) + 100000}"

    @classmethod
    def hash_otp(cls, otp: str, identifier: str) -> str:
        """Hashes OTP using HMAC-SHA256 with server SECRET_KEY and identifier salt."""
        key = settings.SECRET_KEY.encode("utf-8")
        msg = f"{identifier.strip().lower()}:{otp.strip()}".encode("utf-8")
        return hmac.new(key, msg, hashlib.sha256).hexdigest()

    @classmethod
    def verify_otp_hash(cls, plain_otp: str, hashed_otp: str, identifier: str) -> bool:
        """Constant-time verification of OTP hash to prevent timing attacks."""
        expected_hash = cls.hash_otp(plain_otp, identifier)
        return hmac.compare_digest(expected_hash, hashed_otp)

    @classmethod
    def issue_and_dispatch_otp(
        cls,
        db: Session,
        identifier: str,
        delivery_channel: str,
        school_name: str,
        principal_name: str = "Principal / Administrator",
        user_id: Optional[str] = None,
        school_id: Optional[str] = None,
    ) -> Tuple[bool, str, int]:
        """
        Generates, hashes, stores, and dispatches an OTP.
        Enforces 60-second cooldown and 30-minute lockout rules.
        Returns: (success: bool, message: str, cooldown_remaining_seconds: int)
        """
        now = datetime.now(timezone.utc)
        clean_id = identifier.strip().lower()

        # Check existing OTP for lockout & cooldown
        existing = (
            db.query(VerificationOTP)
            .filter(VerificationOTP.identifier == clean_id)
            .order_by(VerificationOTP.created_at.desc())
            .first()
        )

        if existing:
            # Check lockout
            if existing.locked_until:
                locked_until = existing.locked_until
                if locked_until.tzinfo is None:
                    locked_until = locked_until.replace(tzinfo=timezone.utc)
                if locked_until > now:
                    remaining_mins = int((locked_until - now).total_seconds() / 60) + 1
                    return False, f"Account temporarily locked due to too many failed attempts. Try again in {remaining_mins} minutes.", 0

            # Check cooldown
            if existing.resend_available_at:
                resend_at = existing.resend_available_at
                if resend_at.tzinfo is None:
                    resend_at = resend_at.replace(tzinfo=timezone.utc)
                if resend_at > now:
                    wait_sec = int((resend_at - now).total_seconds())
                    return False, f"Please wait {wait_sec} seconds before requesting a new code.", wait_sec

        # Generate fresh OTP
        otp_code = cls.generate_numeric_otp(6)
        hashed = cls.hash_otp(otp_code, clean_id)
        expires_at = now + timedelta(minutes=cls.TTL_MINUTES)
        cooldown_at = now + timedelta(seconds=cls.COOLDOWN_SECONDS)

        # Create or update active OTP record
        otp_record = VerificationOTP(
            identifier=clean_id,
            otp_hash=hashed,
            attempts=0,
            expires_at=expires_at,
            delivery_channel=delivery_channel,
            status="pending",
            school_name=school_name,
            principal_name=principal_name,
            user_id=user_id,
            school_id=school_id,
            resend_available_at=cooldown_at,
            created_at=now,
        )
        db.add(otp_record)
        db.commit()
        db.refresh(otp_record)

        # Dispatch via specified channel
        if delivery_channel == "whatsapp":
            WhatsAppService.send_verification_whatsapp(
                recipient_phone=identifier,
                school_name=school_name,
                code=otp_code,
                principal_name=principal_name,
                expiry_minutes=cls.TTL_MINUTES,
            )
        else:
            EmailService.send_verification_email(
                recipient_email=identifier,
                school_name=school_name,
                code=otp_code,
                principal_name=principal_name,
                expiry_minutes=cls.TTL_MINUTES,
            )

        return True, "Verification code dispatched successfully", cls.COOLDOWN_SECONDS

    @classmethod
    def verify_otp_code(
        cls,
        db: Session,
        identifier: str,
        otp_code: str,
    ) -> Tuple[bool, str, Optional[VerificationOTP]]:
        """
        Verifies the user-submitted code against stored hash.
        Tracks attempts, handles expiry, and locks out if >= 3 failures.
        """
        now = datetime.now(timezone.utc)
        clean_id = identifier.strip().lower()

        record = (
            db.query(VerificationOTP)
            .filter(VerificationOTP.identifier == clean_id)
            .order_by(VerificationOTP.created_at.desc())
            .first()
        )

        if not record:
            return False, "No active verification request found. Please register or request a code.", None

        # 1. Check if locked out
        if record.locked_until:
            locked_until = record.locked_until
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)
            if locked_until > now:
                mins_left = int((locked_until - now).total_seconds() / 60) + 1
                return False, f"Maximum attempts exceeded. This identifier is locked for {mins_left} minutes.", record

        # 2. Check if expired
        expires = record.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < now:
            record.status = "expired"
            db.commit()
            return False, "Verification code has expired (5-minute limit). Please request a new code.", record

        # 3. Check code match
        is_match = cls.verify_otp_hash(otp_code, record.otp_hash, clean_id)
        if not is_match:
            record.attempts += 1
            if record.attempts >= cls.MAX_ATTEMPTS:
                record.locked_until = now + timedelta(minutes=cls.LOCKOUT_MINUTES)
                record.status = "locked"
                db.commit()
                return False, f"Too many incorrect attempts (3). Account locked for {cls.LOCKOUT_MINUTES} minutes.", record
            else:
                remaining = cls.MAX_ATTEMPTS - record.attempts
                db.commit()
                return False, f"Incorrect verification code. Attempts remaining: {remaining}.", record

        # 4. Success! Mark verified
        record.status = "verified"
        db.commit()
        return True, "Verification successful.", record
