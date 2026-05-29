from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from fastapi import Depends, Header, HTTPException


class UserRole(StrEnum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


@dataclass(frozen=True)
class UserContext:
    role: UserRole
    user_id: UUID | None


def get_user_context(
    x_user_role: UserRole = Header(..., alias="X-User-Role"),
    x_user_id: UUID | None = Header(None, alias="X-User-Id"),
) -> UserContext:
    return UserContext(role=x_user_role, user_id=x_user_id)


def require_roles(*roles: UserRole):
    def dependency(context: UserContext = Depends(get_user_context)) -> UserContext:
        if context.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return context

    return dependency
