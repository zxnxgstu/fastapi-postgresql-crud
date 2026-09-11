from sqlalchemy.orm import Session

from models import OrderStatusHistory


def create_order_status_history(
    db: Session,
    order_id: int,
    old_status: str | None,
    new_status: str
):
    history = OrderStatusHistory(
        order_id=order_id,
        old_status=old_status,
        new_status=new_status
    )

    db.add(history)

    return history
def get_order_status_history(
    db: Session,
    order_id: int
):
    return (
        db.query(OrderStatusHistory)
        .filter(OrderStatusHistory.order_id == order_id)
        .order_by(
            OrderStatusHistory.changed_at.asc(),
            OrderStatusHistory.id.asc()
        )
        .all()
    )