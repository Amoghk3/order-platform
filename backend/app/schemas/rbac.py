from pydantic import BaseModel, ConfigDict
from datetime import datetime


# ── Role schemas ────────────────────────────────────────

class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Permission schemas ──────────────────────────────────

class PermissionCreate(BaseModel):
    name: str
    description: str | None = None


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Assignment schemas ──────────────────────────────────

class AssignPermissionRequest(BaseModel):
    permission_id: int


class AssignRoleRequest(BaseModel):
    role_id: int
