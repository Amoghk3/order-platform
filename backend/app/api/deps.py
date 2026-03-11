from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from jose import JWTError

from app.db.session import SessionLocal
from app.db.models import User
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    """
    Decode the JWT and load the user from DB.
    The same `db` session injected here is reused by downstream
    dependencies (require_permission) — no second session is opened.
    """
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")

    stmt = select(User).where(User.id == user_id)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


from app.services.rbac_service import RBACService  # noqa: E402 (avoid circular at top)


def require_permission(*permission_names: str):
    """
    Dependency factory — checks that the current user holds ALL of the
    listed permissions.  Reuses the *same* DB session as get_current_user
    so that no extra session is opened and no ORM objects are detached.
    """
    def _check(
        user: CurrentUser,
        db: DbSession,
    ) -> User:
        for perm in permission_names:
            if not RBACService.has_permission(db, user.id, perm):
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Missing: '{perm}'",
                )
        return user

    return _check