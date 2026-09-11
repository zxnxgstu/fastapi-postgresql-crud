from sqlalchemy.orm import Session

from models import StockMovement


def create_stock_movement(
    db: Session,
    product_id: int,
    quantity_change: int,
    reason: str
):
    movement = StockMovement(
        product_id=product_id,
        quantity_change=quantity_change,
        reason=reason
    )

    db.add(movement)

    return movement


def get_product_stock_movements(
    db: Session,
    product_id: int
):
    return (
        db.query(StockMovement)
        .filter(
            StockMovement.product_id == product_id
        )
        .order_by(
            StockMovement.created_at.asc(),
            StockMovement.id.asc()
        )
        .all()
    )

def get_stock_movements(
    db: Session,
    product_id: int | None = None,
    reason: str | None = None,
    skip: int = 0,
    limit: int = 20
):
    query = db.query(StockMovement)

    if product_id is not None:
        query = query.filter(
            StockMovement.product_id == product_id
        )

    if reason is not None:
        query = query.filter(
            StockMovement.reason == reason
        )

    return (
        query
        .order_by(
            StockMovement.created_at.desc(),
            StockMovement.id.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )