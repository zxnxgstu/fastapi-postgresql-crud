from sqlalchemy.orm import Session

from models import DeliveryMethod
from schemas import (
    DeliveryMethodCreate,
    DeliveryMethodUpdate,
)


def get_active_delivery_methods(
    db: Session
):
    return (
        db.query(DeliveryMethod)
        .filter(DeliveryMethod.active.is_(True))
        .order_by(DeliveryMethod.id.asc())
        .all()
    )


def get_all_delivery_methods(
    db: Session
):
    return (
        db.query(DeliveryMethod)
        .order_by(DeliveryMethod.id.asc())
        .all()
    )


def get_delivery_method(
    db: Session,
    delivery_method_id: int
):
    return (
        db.query(DeliveryMethod)
        .filter(
            DeliveryMethod.id == delivery_method_id
        )
        .first()
    )


def get_delivery_method_by_code(
    db: Session,
    code: str
):
    return (
        db.query(DeliveryMethod)
        .filter(
            DeliveryMethod.code == code
        )
        .first()
    )


def create_delivery_method(
    db: Session,
    delivery_data: DeliveryMethodCreate
):
    delivery_method = DeliveryMethod(
        code=delivery_data.code,
        name=delivery_data.name,
        price=delivery_data.price,
        active=delivery_data.active
    )

    db.add(delivery_method)
    db.commit()
    db.refresh(delivery_method)

    return delivery_method


def update_delivery_method(
    db: Session,
    delivery_method: DeliveryMethod,
    delivery_data: DeliveryMethodUpdate
):
    if delivery_data.name is not None:
        delivery_method.name = delivery_data.name

    if delivery_data.price is not None:
        delivery_method.price = delivery_data.price

    if delivery_data.active is not None:
        delivery_method.active = delivery_data.active

    db.commit()
    db.refresh(delivery_method)

    return delivery_method