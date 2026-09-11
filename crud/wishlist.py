from sqlalchemy.orm import Session

from models import WishlistItem


def get_wishlist(
    db: Session,
    user_id: int
):
    return (
        db.query(WishlistItem)
        .filter(WishlistItem.user_id == user_id)
        .order_by(WishlistItem.id.asc())
        .all()
    )


def get_wishlist_item(
    db: Session,
    user_id: int,
    product_id: int
):
    return (
        db.query(WishlistItem)
        .filter(
            WishlistItem.user_id == user_id,
            WishlistItem.product_id == product_id
        )
        .first()
    )


def add_wishlist_item(
    db: Session,
    user_id: int,
    product_id: int
):
    wishlist_item = WishlistItem(
        user_id=user_id,
        product_id=product_id
    )

    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)

    return wishlist_item


def delete_wishlist_item(
    db: Session,
    wishlist_item: WishlistItem
):
    db.delete(wishlist_item)
    db.commit()