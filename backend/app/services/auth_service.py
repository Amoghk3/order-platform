from sqlalchemy.orm import Session

from sqlalchemy import select

from app.db.models import User
from app.db.rbac_models import Role
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.utils.exceptions import BadRequestException, NotFoundException


class AuthService:
    @staticmethod
    def register(db: Session, email: str, password: str) -> User:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise BadRequestException("Email already registered")

        # Get default user role
        stmt = select(Role).where(Role.name == "user")
        result = db.execute(stmt)
        default_role = result.scalar_one_or_none()

        if not default_role:
            # Fallback if DB isn't seeded properly
            raise NotFoundException("Default role 'user' not found in system")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role_id=default_role.id,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def login(db: Session, email: str, password: str) -> dict:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise NotFoundException("Invalid credentials")

        if not verify_password(password, user.hashed_password):
            raise BadRequestException("Invalid credentials")

        token = create_access_token(
            {"sub": str(user.id), "role": user.role.name}
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }
