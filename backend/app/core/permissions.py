from fastapi import Depends
from app.core.exceptions import ForbiddenException
from app.schemas.auth import UserResponse


def require_officer(current_user: UserResponse) -> UserResponse:
    if current_user.role not in ["OFFICER", "ADMIN"]:
        raise ForbiddenException("Access restricted to border officers and administrators.")
    return current_user


def require_admin(current_user: UserResponse) -> UserResponse:
    if current_user.role != "ADMIN":
        raise ForbiddenException("Administrator role required to access this resource.")
    return current_user
