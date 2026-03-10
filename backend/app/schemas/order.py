from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class OrderCreate(BaseModel):
    total_amount: Decimal


class OrderResponse(BaseModel):
    id: int
    status: str
    total_amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True