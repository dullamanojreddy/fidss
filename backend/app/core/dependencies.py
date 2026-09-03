from typing import Generator
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.schemas.auth import UserResponse

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> UserResponse:
    from app.models.user import User

    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authorization token missing")

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedException("Invalid or expired session token")

    username: str = payload["sub"]
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise UnauthorizedException("User account not found")

    if not user.is_active:
        raise ForbiddenException("User account is deactivated")

    return UserResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


def require_officer_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if current_user.role not in ["OFFICER", "ADMIN"]:
        raise ForbiddenException("Officer clearance required")
    return current_user


def require_admin_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if current_user.role != "ADMIN":
        raise ForbiddenException("Admin clearance required")
    return current_user
