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


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    stmt = select(User).where(User.id == user_id)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


from app.services.rbac_service import RBACService


def require_permission(*permission_names: str):
    """
    Dependency factory to check if a user has one or more permissions.
    If multiple permissions are provided, the user must have ALL of them.
    """
    def _check(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ):
        for perm in permission_names:
            if not RBACService.has_permission(db, user.id, perm):
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Missing: {perm}"
                )
        return user
    return _check