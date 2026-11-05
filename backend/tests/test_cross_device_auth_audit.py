# -*- coding: utf-8 -*-
import pytest
import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.core_entities import User, School, SchoolMembership
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_scenario_a_and_b_owner_registration_and_cross_device_login(db_session):
    """
    Test A & B: Owner registers a school, assigns username and password.
    Then, an independent device/client (without owner session) authenticates successfully.
    """
    # 1. Login as Owner
    owner_login = client.post("/api/auth/login", json={
        "username_or_email": "alikhanwebdeveloper@gmail.com",
        "password": "OwnerPass2026!"
    })
    assert owner_login.status_code == 200, owner_login.text
    owner_token = owner_login.json()["access_token"]

    # 2. Owner registers new school
    unique_suffix = uuid.uuid4().hex[:6]
    school_username = f"iqra_{unique_suffix}"
    school_password = f"IqraPass_{unique_suffix}!"
    school_name = f"Iqra Education System {unique_suffix}"

    create_res = client.post("/api/auth/owner/create-school",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "school_name": school_name,
            "username": school_username,
            "password": school_password,
            "principal_name": "Dr. Muhammad Farooq",
            "phone_number": "+923215423874",
            "quota": "Unlimited"
        }
    )
    assert create_res.status_code == 200, create_res.text
    created_data = create_res.json()
    assert created_data["success"] is True
    assert created_data["username"] == school_username

    # Verify directly in Database
    db_user = db_session.query(User).filter(User.username == school_username).first()
    assert db_user is not None
    assert db_user.role == "school_admin"
    assert db_user.is_active is True
    assert db_user.is_email_verified is True
    assert verify_password(school_password, db_user.hashed_password) is True

    # 3. Simulate Device B (fresh independent client, no owner credentials, no shared cookies)
    device_b_client = TestClient(app)
    device_b_login = device_b_client.post("/api/auth/login", json={
        "username_or_email": school_username,
        "password": school_password
    })
    assert device_b_login.status_code == 200, device_b_login.text
    b_data = device_b_login.json()
    assert "access_token" in b_data
    assert b_data["user"]["school_name"] == school_name
    assert b_data["user"]["role"] == "school_admin"

    # Token inspection
    token_claims = decode_access_token(b_data["access_token"])
    assert token_claims is not None
    assert token_claims["sub"] == db_user.id
    assert token_claims["school_id"] == db_user.school_id
    assert token_claims["role"] == "school_admin"

def test_scenario_c_incognito_pure_credentials():
    """
    Test C: Verify authentication succeeds in a completely blank/incognito session
    using purely the assigned username and password (e.g. built-in school 'pms').
    """
    incognito_client = TestClient(app)
    res = incognito_client.post("/api/auth/login", json={
        "username_or_email": "pms",
        "password": "123"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["username"] == "pms"
    assert data["user"]["school_name"] == "Peshawar Model School"

def test_scenario_d_multi_school_tenant_isolation(db_session):
    """
    Test D: Register two schools, log in as both on separate sessions,
    verify that school A cannot access school B's administrative endpoints.
    """
    # Create School 1
    s1_id = str(uuid.uuid4())
    school1 = School(id=s1_id, name="Tenant School Alpha", slug=f"alpha-{s1_id[:6]}", status="active", is_active=True)
    u1 = User(id=str(uuid.uuid4()), school_id=s1_id, username=f"alpha_{s1_id[:4]}", email=f"alpha_{s1_id[:4]}@alpha.edu",
              hashed_password=hash_password("PassAlpha123!"), full_name="Alpha Admin", role="school_admin", is_active=True, is_email_verified=True)
    
    # Create School 2
    s2_id = str(uuid.uuid4())
    school2 = School(id=s2_id, name="Tenant School Beta", slug=f"beta-{s2_id[:6]}", status="active", is_active=True)
    u2 = User(id=str(uuid.uuid4()), school_id=s2_id, username=f"beta_{s2_id[:4]}", email=f"beta_{s2_id[:4]}@beta.edu",
              hashed_password=hash_password("PassBeta123!"), full_name="Beta Admin", role="school_admin", is_active=True, is_email_verified=True)
    
    db_session.add_all([school1, u1, school2, u2])
    db_session.commit()

    # Client Alpha logs in
    client_alpha = TestClient(app)
    res_alpha = client_alpha.post("/api/auth/login", json={"username_or_email": u1.username, "password": "PassAlpha123!"})
    assert res_alpha.status_code == 200
    token_alpha = res_alpha.json()["access_token"]

    # Client Beta logs in
    client_beta = TestClient(app)
    res_beta = client_beta.post("/api/auth/login", json={"username_or_email": u2.username, "password": "PassBeta123!"})
    assert res_beta.status_code == 200
    token_beta = res_beta.json()["access_token"]

    # Alpha accessing Alpha school -> 200 OK
    get_alpha = client_alpha.get(f"/api/v1/schools/{s1_id}", headers={"Authorization": f"Bearer {token_alpha}"})
    assert get_alpha.status_code == 200

    # Alpha attempting to access Beta school -> 403 Forbidden
    cross_access = client_alpha.get(f"/api/v1/schools/{s2_id}", headers={"Authorization": f"Bearer {token_alpha}"})
    assert cross_access.status_code == 403
    assert "Forbidden" in cross_access.text

    # Beta attempting to update Alpha school -> 403 Forbidden
    cross_update = client_beta.patch(f"/api/v1/schools/{s1_id}", headers={"Authorization": f"Bearer {token_beta}"}, json={"name": "Hacked Name"})
    assert cross_update.status_code == 403

def test_scenario_e_invalid_credentials_and_expired_tokens():
    """
    Test E: Non-existent users, incorrect passwords, and expired tokens receive secure error responses.
    """
    test_client = TestClient(app)

    # 1. Non-existent username
    res1 = test_client.post("/api/auth/login", json={"username_or_email": "nonexistent_user_9999", "password": "anypassword"})
    assert res1.status_code == 401
    assert "Incorrect username/email or password" in res1.json()["detail"]

    # 2. Correct username, wrong password
    res2 = test_client.post("/api/auth/login", json={"username_or_email": "pms", "password": "WrongPassword!"})
    assert res2.status_code == 401
    assert "Incorrect username/email or password" in res2.json()["detail"]

    # 3. Expired token rejection
    expired_token = create_access_token({"sub": "some_user_id"}, expires_delta=timedelta(minutes=-10))
    res3 = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res3.status_code == 401
    assert "Invalid or expired" in res3.json()["detail"]

def test_scenario_f_role_boundaries_school_admin_cannot_access_owner_console():
    """
    Test F: School administrators cannot access Owner/Super Admin management endpoints.
    """
    school_login = client.post("/api/auth/login", json={"username_or_email": "pms", "password": "123"})
    school_token = school_login.json()["access_token"]

    # School admin tries to call owner create-school endpoint
    res = client.post("/api/auth/owner/create-school",
        headers={"Authorization": f"Bearer {school_token}"},
        json={
            "school_name": "Rogue School",
            "username": "rogue",
            "password": "Password123!"
        }
    )
    assert res.status_code == 403
    assert "privileges required" in res.text.lower()

def test_scenario_g_change_password_endpoint(db_session):
    """
    Test G: Authenticated users (both schools and owner) can change their password securely.
    Uses an isolated test user to guarantee zero side-effects.
    """
    # 1. Create a dedicated test user
    uid = uuid.uuid4().hex[:6]
    test_user = User(
        email=f"pwdtest_{uid}@example.com",
        username=f"pwdtest_{uid}",
        hashed_password=hash_password("InitialPass123!"),
        full_name="Password Test Admin",
        role="school_admin",
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(test_user)
    db_session.commit()

    # 2. Login as the test user
    login_res = client.post("/api/auth/login", json={"username_or_email": f"pwdtest_{uid}", "password": "InitialPass123!"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 3. Try with wrong current password -> 400
    res_bad = client.post("/api/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "WrongPassword999!", "new_password": "NewSecretPassword2026!"}
    )
    assert res_bad.status_code == 400
    assert "Current password is incorrect" in res_bad.json()["detail"]

    # 4. Successful password change
    res_ok = client.post("/api/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "InitialPass123!", "new_password": "NewSecretPassword2026!"}
    )
    assert res_ok.status_code == 200
    assert res_ok.json()["success"] is True

    # 5. Old password fails
    old_login = client.post("/api/auth/login", json={"username_or_email": f"pwdtest_{uid}", "password": "InitialPass123!"})
    assert old_login.status_code == 401

    # 6. New password succeeds
    new_login = client.post("/api/auth/login", json={"username_or_email": f"pwdtest_{uid}", "password": "NewSecretPassword2026!"})
    assert new_login.status_code == 200

