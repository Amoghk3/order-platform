from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_permission
from app.db.models import User
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from app.utils.exceptions import AppException

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("orders:create"))],
)
def create_order(
    payload: OrderCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    try:
        return OrderService.create_order(
            db=db,
            user_id=current_user.id,
            total_amount=payload.total_amount,
        )
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.detail)


@router.get(
    "/me",
    response_model=list[OrderResponse],
    dependencies=[Depends(require_permission("orders:read_own"))],
)
def list_my_orders(
    db: DbSession,
    current_user: CurrentUser,
):
    return OrderService.get_orders_for_user(db, current_user.id)


@router.get(
    "/all",
    response_model=list[OrderResponse],
    dependencies=[Depends(require_permission("orders:read_all"))],
    responses={403: {"description": "Admin/Manager access required"}},
)
def list_all_orders(
    db: DbSession,
    current_user: CurrentUser,
):
    return OrderService.get_all_orders(db)