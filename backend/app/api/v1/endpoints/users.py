from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_permission
from app.db.models import User
from app.services.user_service import UserService
from app.schemas.user import UserResponse

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("users:read_own"))],
)
def get_current_user_profile(
    db: DbSession,
    current_user: CurrentUser,
):
    return current_user


@router.get(
    "",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permission("users:list"))],
)
def list_users(
    db: DbSession,
    current_user: CurrentUser,
):
    return UserService.list_users(db)