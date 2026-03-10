from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.utils.exceptions import AppException

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.register(
            db, payload.email, payload.password
        )
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.detail)

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        return AuthService.login(
            db,
            form_data.username,
            form_data.password,
        )
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.detail)