from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.services.user_service import UserService
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return current_user


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "ADMIN":
        return []

    return UserService.list_users(db)