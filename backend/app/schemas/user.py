from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


from app.schemas.rbac import RoleResponse

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: RoleResponse
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)