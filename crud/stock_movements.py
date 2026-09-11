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