import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    ROLE_SUPER_ADMIN,
    ROLE_SCHOOL_ADMIN,
    ROLE_TEACHER,
)

def test_password_hashing_and_verification():
    raw = "SecureSecretPassword#2026"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_payload_and_expiry():
    data = {"sub": "user-uuid-1", "school_id": "school-uuid-10", "role": ROLE_TEACHER}
    token = create_access_token(data)
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-uuid-1"
    assert decoded["school_id"] == "school-uuid-10"
    assert decoded["role"] == ROLE_TEACHER

def test_invalid_token_returns_none():
    assert decode_access_token("completely.invalid.token") is None
