from typing import Optional
from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token, ROLE_SUPER_OWNER, ROLE_SUPER_ADMIN, ROLE_SCHOOL_ADMIN, ROLE_TEACHER
from app.models.core_entities import User, School

security = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> User:
    raw_token = None
    if credentials and credentials.credentials:
        raw_token = credentials.credentials
    elif token:
        raw_token = token
    elif "authorization" in request.headers:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            raw_token = auth_header[7:].strip()

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(raw_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    # Enforce School Suspension boundary
    if user.school_id and user.role not in (ROLE_SUPER_ADMIN, ROLE_SUPER_OWNER):
        school = db.query(School).filter(School.id == user.school_id).first()
        if school and (school.status == "suspended" or not school.is_active):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="School account has been suspended"
            )

    return user

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (ROLE_SUPER_ADMIN, ROLE_SUPER_OWNER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin or Owner privileges required"
        )
    return current_user

def require_super_owner_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (ROLE_SUPER_OWNER, ROLE_SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Site Owner or Super Admin privileges required"
        )
    return current_user

def require_school_admin_or_super(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [ROLE_SUPER_ADMIN, ROLE_SCHOOL_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School Admin privileges required"
        )
    return current_user
