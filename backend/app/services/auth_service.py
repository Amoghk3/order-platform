from sqlalchemy.orm import Session

from app.db.models import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.utils.exceptions import BadRequestException, NotFoundException


class AuthService:
    @staticmethod
    def register(db: Session, email: str, password: str):
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise BadRequestException("Email already registered")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role="USER",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def login(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise NotFoundException("Invalid credentials")

        if not verify_password(password, user.hashed_password):
            raise BadRequestException("Invalid credentials")

        token = create_access_token(
            {"sub": str(user.id), "role": user.role}
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }
