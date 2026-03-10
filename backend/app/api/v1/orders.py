from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from app.utils.exceptions import AppException

router = APIRouter()


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return OrderService.create_order(
            db=db,
            current_user=current_user,
            total_amount=payload.total_amount,
        )
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.detail)


@router.get(
    "/me",
    response_model=list[OrderResponse],
)
def list_my_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return OrderService.list_my_orders(db, current_user)


@router.get(
    "/all",
    response_model=list[OrderResponse],
)
def list_all_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return OrderService.list_all_orders(db, current_user)
    except AppException as e:
        raise HTTPException(status_code=403, detail=e.detail)