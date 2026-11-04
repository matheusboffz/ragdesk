import uuid

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppError
from app.core.security import decode_access_token
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validates Bearer JWT token and returns the authenticated User entity."""
    if credentials is None or not credentials.credentials:
        raise AppError(
            message="Missing authentication token.",
            code="AUTHENTICATION_REQUIRED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    payload = decode_access_token(credentials.credentials)
    sub = payload.get("sub")
    if not isinstance(sub, str):
        raise AppError(
            message="Invalid token subject.",
            code="INVALID_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        user_id = uuid.UUID(sub)
    except ValueError as exc:
        raise AppError(
            message="Malformed user identifier in token.",
            code="INVALID_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from exc

    user = db.get(User, user_id)
    if user is None:
        raise AppError(
            message="Authenticated user no longer exists.",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensures the authenticated user holds the 'admin' role."""
    if current_user.role != UserRole.ADMIN.value:
        raise AppError(
            message="Administrator privileges are required for this resource.",
            code="FORBIDDEN_ADMIN_ONLY",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return current_user
