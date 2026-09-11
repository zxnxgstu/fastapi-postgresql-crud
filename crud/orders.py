from sqlalchemy.orm import Session

from models import CartItem, Order, OrderItem
from schemas import OrderStatusUpdate


def create_order_from_cart(
    db: Session,
    user_id: int
):
    cart_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .all()
    )

    if not cart_items:
        return None

    total_price = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    order = Order(
        user_id=user_id,
        total_price=total_price
    )

    db.add(order)
    db.flush()

    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product.id,
            product_name=cart_item.product.name,
            price=cart_item.product.price,
            quantity=cart_item.quantity
        )

        db.add(order_item)

    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()
    db.refresh(order)

    return order


def get_user_orders(
    db: Session,
    user_id: int
):
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_user_order(
    db: Session,
    order_id: int,
    user_id: int
):
    return (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == user_id
        )
        .first()
    )


def get_order(
    db: Session,
    order_id: int
):
    return (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )


def get_all_orders(db: Session):
    return (
        db.query(Order)
        .order_by(Order.created_at.desc())
        .all()
    )


def update_order_status(
    db: Session,
    order: Order,
    status_data: OrderStatusUpdate
):
    order.status = status_data.status

    db.commit()
    db.refresh(order)

    return order