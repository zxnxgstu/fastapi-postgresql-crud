from sqlalchemy.orm import Session

from models import CartItem, Order, OrderItem
from schemas import OrderCreate, OrderStatusUpdate


def create_order_from_cart(
    db: Session,
    user_id: int,
    order_data: OrderCreate
):
    cart_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .all()
    )

    if not cart_items:
        return None

    for cart_item in cart_items:
        product = cart_item.product

        if product.stock_quantity < cart_item.quantity:
            raise ValueError("Not enough stock")

    total_price = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    order = Order(
        user_id=user_id,
        total_price=total_price,
        shipping_city=order_data.shipping_city,
        shipping_street=order_data.shipping_street,
        shipping_postal_code=order_data.shipping_postal_code
    )

    db.add(order)
    db.flush()

    for cart_item in cart_items:
        product = cart_item.product

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            price=product.price,
            quantity=cart_item.quantity
        )

        db.add(order_item)

        product.stock_quantity -= cart_item.quantity
        product.in_stock = product.stock_quantity > 0

    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()
    db.refresh(order)

    return order

def get_user_orders(
    db: Session,
    user_id: int,
    status: str | None = None,
    skip: int = 0,
    limit: int = 10
):
    query = db.query(Order).filter(
        Order.user_id == user_id
    )

    if status is not None:
        query = query.filter(
            Order.status == status
        )

    return (
        query
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
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


def get_all_orders(
    db: Session,
    status: str | None = None,
    skip: int = 0,
    limit: int = 10
):
    query = db.query(Order)

    if status is not None:
        query = query.filter(
            Order.status == status
        )

    return (
        query
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
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