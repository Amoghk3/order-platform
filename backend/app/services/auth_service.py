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

        stmt = select(Role).where(Role.name == "user")
        result = db.execute(stmt)
        default_role = result.scalar_one_or_none()

        if not default_role:
            raise NotFoundException("Default role 'user' not found. Seed the roles table first.")

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
        # Eagerly join Role so user.role is always loaded in this session
        stmt = (
            select(User)
            .join(Role, User.role_id == Role.id)
            .where(User.email == email)
        )
        result = db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("Invalid credentials")

        if not verify_password(password, user.hashed_password):
            raise BadRequestException("Invalid credentials")

        if not user.is_active:
            raise BadRequestException("Account is inactive")

        # user.role is guaranteed loaded because of the join above
        token = create_access_token(
            {"sub": str(user.id), "role": user.role.name}
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }