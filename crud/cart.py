from sqlalchemy.orm import Session

from models import CartItem
from schemas import CartItemCreate, CartItemUpdate


def get_cart(db: Session, user_id: int):
    return (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .all()
    )


def get_cart_item(
    db: Session,
    item_id: int,
    user_id: int
):
    return (
        db.query(CartItem)
        .filter(
            CartItem.id == item_id,
            CartItem.user_id == user_id
        )
        .first()
    )

def get_cart_item_by_product(
    db: Session,
    user_id: int,
    product_id: int
):
    return (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id
        )
        .first()
    )

def add_cart_item(
    db: Session,
    user_id: int,
    item: CartItemCreate
):
    existing_item = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id,
            CartItem.product_id == item.product_id
        )
        .first()
    )

    if existing_item:
        existing_item.quantity += item.quantity

        db.commit()
        db.refresh(existing_item)

        return existing_item

    db_item = CartItem(
        user_id=user_id,
        product_id=item.product_id,
        quantity=item.quantity
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


def update_cart_item(
    db: Session,
    cart_item: CartItem,
    item: CartItemUpdate
):
    cart_item.quantity = item.quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item


def delete_cart_item(
    db: Session,
    cart_item: CartItem
):
    db.delete(cart_item)
    db.commit()