from sqlalchemy.orm import Session

from models import Order, Payment


def get_payment_by_order(
    db: Session,
    order_id: int
):
    return (
        db.query(Payment)
        .filter(Payment.order_id == order_id)
        .first()
    )


def create_payment(
    db: Session,
    order: Order
):
    payment = Payment(
        order_id=order.id,
        amount=order.total_price,
        status="paid"
    )

    order.status = "paid"

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment