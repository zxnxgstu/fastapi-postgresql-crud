from sqlalchemy.orm import Session
from .order_status_history import create_order_status_history
from models import Order, Payment, Product
from .stock_movements import create_stock_movement


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
    old_status = order.status

    payment = Payment(
        order_id=order.id,
        amount=order.total_price,
        status="paid"
    )

    order.status = "paid"

    db.add(payment)

    create_order_status_history(
        db=db,
        order_id=order.id,
        old_status=old_status,
        new_status="paid"
    )

    db.commit()
    db.refresh(payment)

    return payment

def refund_payment(
    db: Session,
    order: Order,
    payment: Payment
):
    if payment.status == "refunded":
        raise ValueError("Payment already refunded")

    if payment.status != "paid":
        raise ValueError("Only paid payment can be refunded")

    if order.status == "completed":
        raise ValueError("Completed order cannot be refunded")

    old_status = order.status

    for order_item in order.items:
        if order_item.product_id is None:
            continue

        product = (
            db.query(Product)
            .filter(Product.id == order_item.product_id)
            .first()
        )

        if product is not None:
            product.stock_quantity += order_item.quantity
            product.in_stock = True

            create_stock_movement(
                db=db,
                product_id=product.id,
                quantity_change=order_item.quantity,
                reason="refund"
            )
    payment.status = "refunded"
    order.status = "cancelled"

    create_order_status_history(
        db=db,
        order_id=order.id,
        old_status=old_status,
        new_status="cancelled"
    )

    db.commit()
    db.refresh(payment)

    return payment