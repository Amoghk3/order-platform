from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.db.rbac_models import Role
from app.core.security import hash_password
from app.utils.exceptions import BadRequestException, NotFoundException


class UserService:

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        role_id: int | None = None,
        role_name: str = "user",
    ) -> User:
        """
        Create a user and assign a role by ID (preferred) or by name fallback.
        Mirrors AuthService.register so both paths stay consistent.
        """
        resolved_role_id = role_id

        if resolved_role_id is None:
            stmt = select(Role).where(Role.name == role_name)
            result = db.execute(stmt)
            role = result.scalar_one_or_none()
            if not role:
                raise NotFoundException(
                    f"Role '{role_name}' not found. Seed the roles table first."
                )
            resolved_role_id = role.id

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role_id=resolved_role_id,
        )

        db.add(user)

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            raise BadRequestException("User with this email already exists")

        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        stmt = select(User).where(User.id == user_id)
        result = db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User not found")

        return user

    @staticmethod
    def list_users(db: Session) -> list[User]:
        stmt = select(User).order_by(User.id)
        result = db.execute(stmt)
        return list(result.scalars().all())