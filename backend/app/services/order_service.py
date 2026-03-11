from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.models import Order
from app.utils.exceptions import NotFoundException, BadRequestException


class OrderService:

    @staticmethod
    def create_order(
        db: Session,
        user_id: int,
        total_amount: Decimal,
    ) -> Order:

        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status="PENDING",
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def get_order_by_id(
        db: Session,
        order_id: int,
        user_id: int | None = None,
    ) -> Order:

        stmt = select(Order).where(Order.id == order_id)
        order = db.execute(stmt).scalar_one_or_none()

        if not order:
            raise NotFoundException("Order not found")

        # Prevent IDOR attacks
        if user_id and order.user_id != user_id:
            raise BadRequestException("Access denied")

        return order

    @staticmethod
    def get_orders_for_user(
        db: Session,
        user_id: int,
    ):
        stmt = select(Order).where(Order.user_id == user_id)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_all_orders(db: Session):
        stmt = select(Order)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_orders_paginated(
        db: Session,
        limit: int,
        offset: int,
        status: str | None = None,
    ):

        stmt = select(Order)

        if status:
            stmt = stmt.where(Order.status == status)

        stmt = stmt.limit(limit).offset(offset)

        items = db.execute(stmt).scalars().all()

        total_stmt = select(func.count()).select_from(Order)

        if status:
            total_stmt = total_stmt.where(Order.status == status)

        total = db.execute(total_stmt).scalar()

        return {
            "items": items,
            "total": total,
        }

    @staticmethod
    def update_order_status(
        db: Session,
        order_id: int,
        status: str,
        user_id: int | None = None,
    ):

        order = OrderService.get_order_by_id(db, order_id, user_id)

        if order.status == "CANCELLED":
            raise BadRequestException("Cannot modify cancelled order")

        order.status = status

        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def cancel_order(
        db: Session,
        order_id: int,
        user_id: int | None = None,
    ):

        order = OrderService.get_order_by_id(db, order_id, user_id)

        if order.status == "COMPLETED":
            raise BadRequestException("Completed order cannot be cancelled")

        order.status = "CANCELLED"

        db.commit()

        return order