import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.core_entities import User, School, VerificationOTP
from app.core.security import hash_password, create_access_token, ROLE_SUPER_OWNER, ROLE_TEACHER
from app.services.communication.otp_service import OTPService
from app.services.communication.whatsapp import WhatsAppService

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_pakistan_phone_formatting():
    assert WhatsAppService.format_pakistan_phone("03215423874") == "+923215423874"
    assert WhatsAppService.format_pakistan_phone("0321-5423874") == "+923215423874"
    assert WhatsAppService.format_pakistan_phone("923215423874") == "+923215423874"
    assert WhatsAppService.format_pakistan_phone("+923215423874") == "+923215423874"

def test_register_initiate_via_email(db_session):
    test_email = f"principal_{int(datetime.now().timestamp())}@edupeshawar.edu.pk"
    payload = {
        "school_name": "Peshawar Cambridge Academy",
        "principal_name": "Principal Zahid Khan",
        "email": test_email,
        "phone_number": "03215423874",
        "password": "SchoolPass2026!",
        "verification_method": "email"
    }

    res = client.post("/api/auth/register-initiate", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["identifier"] == test_email
    assert data["school_name"] == "Peshawar Cambridge Academy"
    assert data["verification_method"] == "email"
    assert data["resend_cooldown_seconds"] == 60
    assert data["expires_in_seconds"] == 300

    # Check OTP record created in database
    otp = db_session.query(VerificationOTP).filter(VerificationOTP.identifier == test_email).first()
    assert otp is not None
    assert otp.status == "pending"
    assert otp.attempts == 0
    assert otp.delivery_channel == "email"

def test_register_initiate_via_whatsapp(db_session):
    test_email = f"admin_{int(datetime.now().timestamp())}@islamia.edu.pk"
    phone_input = f"0321{datetime.now().microsecond:06d}"
    normalized_phone = f"+92321{datetime.now().microsecond:06d}"

    payload = {
        "school_name": "Islamia Collegiate School",
        "principal_name": "Prof. Tariq Mahmud",
        "email": test_email,
        "phone_number": phone_input,
        "password": "SecurePass2026!",
        "verification_method": "whatsapp"
    }

    res = client.post("/api/auth/register-initiate", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["identifier"].startswith("+92321")
    assert data["verification_method"] == "whatsapp"

    # Verify cooldown blocks immediate re-request
    res_cooldown = client.post("/api/auth/register-initiate", json=payload)
    assert res_cooldown.status_code == 429
    assert "Please wait" in res_cooldown.json()["detail"]

def test_otp_verification_attempts_and_lockout(db_session):
    test_id = f"test_lockout_{int(datetime.now().timestamp())}@test.com"
    school_name = "Lockout Test High School"
    principal = "Dr. Lockout"

    # Issue OTP directly
    ok, msg, cooldown = OTPService.issue_and_dispatch_otp(
        db=db_session,
        identifier=test_id,
        delivery_channel="email",
        school_name=school_name,
        principal_name=principal,
    )
    assert ok is True

    # 1. First wrong attempt
    ok1, msg1, rec1 = OTPService.verify_otp_code(db_session, test_id, "000000")
    assert ok1 is False
    assert "Attempts remaining: 2" in msg1

    # 2. Second wrong attempt
    ok2, msg2, rec2 = OTPService.verify_otp_code(db_session, test_id, "111111")
    assert ok2 is False
    assert "Attempts remaining: 1" in msg2

    # 3. Third wrong attempt -> Triggers 30-min lockout
    ok3, msg3, rec3 = OTPService.verify_otp_code(db_session, test_id, "222222")
    assert ok3 is False
    assert "locked for 30 minutes" in msg3
    assert rec3.status == "locked"
    assert rec3.locked_until is not None

def test_otp_verification_expiry(db_session):
    test_id = f"test_expired_{int(datetime.now().timestamp())}@test.com"
    OTPService.issue_and_dispatch_otp(
        db=db_session,
        identifier=test_id,
        delivery_channel="email",
        school_name="Expired School",
        principal_name="Test Principal",
    )

    # Manually expire the record
    rec = db_session.query(VerificationOTP).filter(VerificationOTP.identifier == test_id).first()
    rec.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    ok, msg, _ = OTPService.verify_otp_code(db_session, test_id, "123456")
    assert ok is False
    assert "expired" in msg.lower()

def test_complete_verify_otp_endpoint_activates_school(db_session):
    test_email = f"verified_{int(datetime.now().timestamp())}@kpkboard.edu.pk"
    payload = {
        "school_name": "Edwardes College School",
        "principal_name": "Principal Edwardes",
        "email": test_email,
        "phone_number": "03215423874",
        "password": "Edwardes2026!",
        "verification_method": "email"
    }
    init_res = client.post("/api/auth/register-initiate", json=payload)
    assert init_res.status_code == 200

    # Obtain the active OTP code for this test from the deterministic mock/record
    otp_record = db_session.query(VerificationOTP).filter(VerificationOTP.identifier == test_email).first()
    # Find matching code by checking 100000..999999 or by calculating hash
    # To test verify endpoint cleanly, set a known hash
    test_code = "842915"
    otp_record.otp_hash = OTPService.hash_otp(test_code, test_email)
    db_session.commit()

    # Submit verification code
    verify_res = client.post("/api/auth/verify-otp", json={
        "identifier": test_email,
        "otp_code": test_code
    })
    assert verify_res.status_code == 200, verify_res.text
    token_data = verify_res.json()
    assert "access_token" in token_data
    assert token_data["user"]["is_email_verified"] is True
    assert token_data["user"]["is_verified"] is True
    assert token_data["user"]["email"] == test_email

    # Confirm user in DB is active and verified
    user = db_session.query(User).filter(User.email == test_email).first()
    assert user.is_email_verified is True
    assert user.is_active is True

def test_owner_console_management_interface(db_session):
    # 1. Create Super Owner user
    owner_email = f"owner_{int(datetime.now().timestamp())}@alibuild.site"
    owner_user = User(
        email=owner_email,
        hashed_password=hash_password("OwnerSecure!"),
        full_name="Muhammad Ali (Owner)",
        role=ROLE_SUPER_OWNER,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(owner_user)
    db_session.commit()

    owner_token = create_access_token({"sub": owner_user.id, "role": ROLE_SUPER_OWNER, "email": owner_email})
    headers = {"Authorization": f"Bearer {owner_token}"}

    # 2. Query Owner Verifications
    list_res = client.get("/api/v1/auth/owner/verifications", headers=headers)
    assert list_res.status_code == 200, list_res.text
    data = list_res.json()
    assert "items" in data
    assert "total_schools" in data
    assert "verified_schools" in data
    assert "pending_verifications" in data

    # 3. Test Manual Verify by Owner
    # Create a pending school
    pending_email = f"pending_telecom_fail_{int(datetime.now().timestamp())}@school.pk"
    client.post("/api/auth/register-initiate", json={
        "school_name": "Frontier Model School",
        "principal_name": "Sir Ayub",
        "email": pending_email,
        "phone_number": "03215423874",
        "password": "Pass1234!",
        "verification_method": "email"
    })
    pending_otp = db_session.query(VerificationOTP).filter(VerificationOTP.identifier == pending_email).first()
    assert pending_otp.status == "pending"

    # Owner performs one-click manual verification
    manual_res = client.post(f"/api/v1/auth/owner/verify-manual/{pending_otp.id}", headers=headers)
    assert manual_res.status_code == 200
    assert "Successfully approved and verified" in manual_res.json()["message"]

    # Confirm user is now activated
    approved_user = db_session.query(User).filter(User.email == pending_email).first()
    assert approved_user.is_email_verified is True

    # 4. Verify unauthorized user (e.g. Teacher) is rejected with 403 Forbidden
    teacher_user = User(
        email=f"teacher_{int(datetime.now().timestamp())}@school.pk",
        hashed_password=hash_password("Teacher123!"),
        full_name="Teacher User",
        role=ROLE_TEACHER,
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(teacher_user)
    db_session.commit()

    teacher_token = create_access_token({"sub": teacher_user.id, "role": ROLE_TEACHER, "email": teacher_user.email})
    unauth_res = client.get("/api/v1/auth/owner/verifications", headers={"Authorization": f"Bearer {teacher_token}"})
    assert unauth_res.status_code == 403
