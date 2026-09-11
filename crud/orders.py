from sqlalchemy.orm import Session
from .order_status_history import create_order_status_history
from models import (
    Address,
    CartItem,
    DeliveryMethod,
    Order,
    OrderItem,
    Product,
    PromoCode,
)
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

    subtotal = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    promo_code = None
    discount_percent = 0
    discount_amount = 0

    if order_data.promo_code:
        promo = (
            db.query(PromoCode)
            .filter(PromoCode.code == order_data.promo_code)
            .first()
        )

        if promo is None or not promo.active:
            raise ValueError("Invalid promo code")

        promo_code = promo.code
        discount_percent = promo.discount_percent

        discount_amount = (
            subtotal * discount_percent // 100
        )

    total_price = subtotal - discount_amount

    shipping_city = order_data.shipping_city
    shipping_street = order_data.shipping_street
    shipping_postal_code = order_data.shipping_postal_code

    if order_data.address_id is not None:
        address = (
            db.query(Address)
            .filter(
                Address.id == order_data.address_id,
                Address.user_id == user_id
            )
            .first()
        )

        if address is None:
            raise ValueError("Address not found")

        shipping_city = address.city
        shipping_street = address.street
        shipping_postal_code = address.postal_code

    elif shipping_city is None:
        address = (
            db.query(Address)
            .filter(
                Address.user_id == user_id,
                Address.is_default.is_(True)
            )
            .first()
        )

        if address is None:
            raise ValueError("Default address not found")

        shipping_city = address.city
        shipping_street = address.street
        shipping_postal_code = address.postal_code

    delivery_method_id = None
    delivery_method_code = None
    delivery_method_name = None
    delivery_price = 0

    if order_data.delivery_method_id is not None:
        delivery_method = (
            db.query(DeliveryMethod)
            .filter(
                DeliveryMethod.id == order_data.delivery_method_id,
                DeliveryMethod.active.is_(True)
            )
            .first()
        )

        if delivery_method is None:
            raise ValueError("Delivery method not found")

        delivery_method_id = delivery_method.id
        delivery_method_code = delivery_method.code
        delivery_method_name = delivery_method.name
        delivery_price = delivery_method.price

        total_price += delivery_price

    order = Order(
        user_id=user_id,
        subtotal=subtotal,
        discount_amount=discount_amount,
        total_price=total_price,
        promo_code=promo_code,
        discount_percent=discount_percent,
        shipping_city=shipping_city,
        shipping_street=shipping_street,
        shipping_postal_code=shipping_postal_code,
        delivery_method_id=delivery_method_id,
        delivery_method_code=delivery_method_code,
        delivery_method_name=delivery_method_name,
        delivery_price=delivery_price,
        customer_note=order_data.customer_note
    )

    db.add(order)
    db.flush()

    create_order_status_history(
        db=db,
        order_id=order.id,
        old_status=None,
        new_status="pending"
    )

    for cart_item in cart_items:
        product = cart_item.product

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            price=product.price,
            quantity=cart_item.quantity,
            line_total=product.price * cart_item.quantity
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
    allowed_transitions = {
        "pending": set(),
        "paid": {"shipped"},
        "shipped": {"completed"},
        "completed": set(),
        "cancelled": set(),
    }

    new_status = status_data.status
    old_status = order.status

    if new_status not in allowed_transitions.get(
        old_status,
        set()
    ):
        raise ValueError(
            f"Cannot change order status from "
            f"{old_status} to {new_status}"
        )

    order.status = new_status

    create_order_status_history(
        db=db,
        order_id=order.id,
        old_status=old_status,
        new_status=new_status
    )

    db.commit()
    db.refresh(order)

    return order


def cancel_order(
    db: Session,
    order: Order
):
    if order.status == "cancelled":
        raise ValueError("Order already cancelled")

    if order.status == "paid":
        raise ValueError("Paid order must be refunded")

    if order.status == "completed":
        raise ValueError("Completed order cannot be cancelled")

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

    order.status = "cancelled"

    create_order_status_history(
        db=db,
        order_id=order.id,
        old_status=old_status,
        new_status="cancelled"
    )

    db.commit()
    db.refresh(order)

    return order

def update_shipment_tracking(
    db: Session,
    order: Order,
    shipping_carrier: str,
    tracking_number: str
):
    if order.status != "shipped":
        raise ValueError(
            "Tracking can only be added to shipped orders"
        )

    order.shipping_carrier = shipping_carrier
    order.tracking_number = tracking_number

    db.commit()
    db.refresh(order)

    return order