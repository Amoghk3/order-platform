from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models import Order
from app.utils.exceptions import BadRequestException


class OrderService:

    @staticmethod
    def create_order(
        db: Session,
        user_id: int,
        total_amount,
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
    def get_orders_for_user(
        db: Session,
        user_id: int,
    ) -> list[Order]:

        stmt = select(Order).where(Order.user_id == user_id)

        result = db.execute(stmt)

        return result.scalars().all()

    @staticmethod
    def get_all_orders(
        db: Session,
    ) -> list[Order]:

        stmt = select(Order)

        result = db.execute(stmt)

        return result.scalars().all()