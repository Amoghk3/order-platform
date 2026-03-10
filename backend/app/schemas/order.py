from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime


class OrderCreate(BaseModel):
    total_amount: Decimal


class OrderResponse(BaseModel):
    id: int
    status: str
    total_amount: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)