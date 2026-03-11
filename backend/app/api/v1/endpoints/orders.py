from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_permission
from app.db.models import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderUpdateStatus,
    OrderListResponse,
)
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
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    db: DbSession,
):
    return OrderService.get_order_by_id(db, order_id)


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    dependencies=[Depends(require_permission("orders:update"))],
)
def update_order_status(
    order_id: int,
    payload: OrderUpdateStatus,
    db: DbSession,
):
    return OrderService.update_order_status(
        db,
        order_id,
        payload.status,
    )


@router.post(
    "/{order_id}/cancel",
    dependencies=[Depends(require_permission("orders:update"))],
)
def cancel_order(
    order_id: int,
    db: DbSession,
):
    return OrderService.cancel_order(db, order_id)


@router.get(
    "",
    response_model=OrderListResponse,
    dependencies=[Depends(require_permission("orders:read_all"))],
)
def list_orders_paginated(
    db: DbSession,
    limit: Annotated[int, Query(le=100)] = 10,
    offset: int = 0,
    status: str | None = None,
):
    return OrderService.get_orders_paginated(
        db,
        limit=limit,
        offset=offset,
        status=status,
    )