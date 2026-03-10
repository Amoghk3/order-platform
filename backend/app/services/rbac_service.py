from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.rbac_models import Role, Permission, RolePermission
from app.db.models import User
from app.utils.exceptions import (
    BadRequestException,
    NotFoundException,
)


class RBACService:
    """
    Database-driven RBAC service.
    All role/permission logic goes through the database — no hardcoded roles.
    """

    # ── Permission checking ─────────────────────────────────

    @staticmethod
    def has_permission(db: Session, user_id: int, permission_name: str) -> bool:
        """Check if a user's role grants a specific permission."""
        stmt = (
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(User, User.role_id == Role.id)
            .where(User.id == user_id, Permission.name == permission_name)
        )
        result = db.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    def get_user_permissions(db: Session, user_id: int) -> list[str]:
        """Return all permission names for a user's role."""
        stmt = (
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(User, User.role_id == Role.id)
            .where(User.id == user_id)
        )
        result = db.execute(stmt)
        return list(result.scalars().all())

    # ── Role CRUD ───────────────────────────────────────────

    @staticmethod
    def create_role(db: Session, name: str, description: str | None = None) -> Role:
        role = Role(name=name, description=description)
        db.add(role)
        try:
            db.commit()
            db.refresh(role)
        except IntegrityError:
            db.rollback()
            raise BadRequestException(f"Role '{name}' already exists")
        return role

    @staticmethod
    def list_roles(db: Session) -> list[Role]:
        stmt = select(Role).order_by(Role.id)
        result = db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Role:
        stmt = select(Role).where(Role.id == role_id)
        result = db.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            raise NotFoundException("Role not found")
        return role

    @staticmethod
    def delete_role(db: Session, role_id: int) -> None:
        role = RBACService.get_role_by_id(db, role_id)
        # Prevent deletion if users are assigned to this role
        stmt = select(User.id).where(User.role_id == role_id).limit(1)
        result = db.execute(stmt)
        if result.scalar_one_or_none() is not None:
            raise BadRequestException(
                "Cannot delete role that is assigned to users"
            )
        db.delete(role)
        db.commit()

    # ── Permission CRUD ─────────────────────────────────────

    @staticmethod
    def create_permission(
        db: Session,
        name: str,
        description: str | None = None,
    ) -> Permission:
        perm = Permission(name=name, description=description)
        db.add(perm)
        try:
            db.commit()
            db.refresh(perm)
        except IntegrityError:
            db.rollback()
            raise BadRequestException(f"Permission '{name}' already exists")
        return perm

    @staticmethod
    def list_permissions(db: Session) -> list[Permission]:
        stmt = select(Permission).order_by(Permission.id)
        result = db.execute(stmt)
        return list(result.scalars().all())

    # ── Role ↔ Permission mapping ───────────────────────────

    @staticmethod
    def get_role_permissions(db: Session, role_id: int) -> list[Permission]:
        role = RBACService.get_role_by_id(db, role_id)
        return role.permissions

    @staticmethod
    def assign_permission_to_role(
        db: Session,
        role_id: int,
        permission_id: int,
    ) -> None:
        # Validate both exist
        RBACService.get_role_by_id(db, role_id)

        stmt = select(Permission).where(Permission.id == permission_id)
        result = db.execute(stmt)
        if result.scalar_one_or_none() is None:
            raise NotFoundException("Permission not found")

        mapping = RolePermission(role_id=role_id, permission_id=permission_id)
        db.add(mapping)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise BadRequestException(
                "Permission already assigned to this role"
            )

    @staticmethod
    def remove_permission_from_role(
        db: Session,
        role_id: int,
        permission_id: int,
    ) -> None:
        stmt = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        result = db.execute(stmt)
        mapping = result.scalar_one_or_none()
        if not mapping:
            raise NotFoundException("Permission not assigned to this role")
        db.delete(mapping)
        db.commit()

    # ── User ↔ Role ─────────────────────────────────────────

    @staticmethod
    def assign_role_to_user(
        db: Session,
        user_id: int,
        role_id: int,
    ) -> User:
        # Validate role exists
        RBACService.get_role_by_id(db, role_id)

        stmt = select(User).where(User.id == user_id)
        result = db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User not found")

        user.role_id = role_id
        db.commit()
        db.refresh(user)
        return user
