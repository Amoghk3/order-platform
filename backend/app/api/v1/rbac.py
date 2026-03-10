from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.services.rbac_service import RBACService
from app.schemas.rbac import (
    RoleCreate,
    RoleResponse,
    PermissionCreate,
    PermissionResponse,
    AssignPermissionRequest,
    AssignRoleRequest,
)
from app.utils.exceptions import AppException


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()

# Temporary: Require user to be authenticated.
# Once RBAC is fully wired, this should use `require_permission("rbac:manage")`
def require_rbac_manager(user: CurrentUser, db: DbSession):
    if not RBACService.has_permission(db, user.id, "rbac:manage"):
        raise HTTPException(status_code=403, detail="Need rbac:manage permission")
    return user


Manager = Annotated[User, Depends(require_rbac_manager)]

# ── Roles ──────────────────────────────────────────────────

@router.get("/roles", response_model=list[RoleResponse])
def list_roles(db: DbSession, _: Manager):
    return RBACService.list_roles(db)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, db: DbSession, _: Manager):
    try:
        return RBACService.create_role(db, payload.name, payload.description)
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.detail)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: DbSession, _: Manager):
    try:
        RBACService.delete_role(db, role_id)
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.detail)


# ── Permissions ────────────────────────────────────────────

@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(db: DbSession, _: Manager):
    return RBACService.list_permissions(db)


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(payload: PermissionCreate, db: DbSession, _: Manager):
    try:
        return RBACService.create_permission(db, payload.name, payload.description)
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.detail)


# ── Mapping (Role ↔ Permission) ────────────────────────────

@router.get("/roles/{role_id}/permissions", response_model=list[PermissionResponse])
def get_role_permissions(role_id: int, db: DbSession, _: Manager):
    try:
        return RBACService.get_role_permissions(db, role_id)
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.detail)


@router.post("/roles/{role_id}/permissions", status_code=status.HTTP_204_NO_CONTENT)
def assign_permission_to_role(role_id: int, payload: AssignPermissionRequest, db: DbSession, _: Manager):
    try:
        RBACService.assign_permission_to_role(db, role_id, payload.permission_id)
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.detail)


@router.delete("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_permission_from_role(role_id: int, permission_id: int, db: DbSession, _: Manager):
    try:
        RBACService.remove_permission_from_role(db, role_id, permission_id)
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.detail)


# ── Mapping (User ↔ Role) ──────────────────────────────────

@router.put("/users/{user_id}/role", status_code=status.HTTP_200_OK)
def assign_role_to_user(user_id: int, payload: AssignRoleRequest, db: DbSession, _: Manager):
    try:
        # Return something to show success; in a real app, maybe return UserResponse
        RBACService.assign_role_to_user(db, user_id, payload.role_id)
        return {"detail": "Role assigned successfully"}
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.detail)
