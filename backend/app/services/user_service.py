from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.core.security import hash_password
from app.utils.exceptions import BadRequestException, NotFoundException


class UserService:

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        role: str = "USER",
    ) -> User:

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role=role,
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
    def get_user_by_email(
        db: Session,
        email: str,
    ) -> User | None:

        stmt = select(User).where(User.email == email)

        result = db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int,
    ) -> User:

        stmt = select(User).where(User.id == user_id)

        result = db.execute(stmt)

        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User not found")

        return user

    @staticmethod
    def list_users(db: Session) -> list[User]:

        stmt = select(User)

        result = db.execute(stmt)

        return result.scalars().all()