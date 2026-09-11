from sqlalchemy.orm import Session

from models import ShipmentTrackingHistory


def get_shipment_tracking_history(
    db: Session,
    order_id: int
):
    return (
        db.query(ShipmentTrackingHistory)
        .filter(ShipmentTrackingHistory.order_id == order_id)
        .order_by(
            ShipmentTrackingHistory.created_at.asc(),
            ShipmentTrackingHistory.id.asc()
        )
        .all()
    )


def create_shipment_tracking_history(
    db: Session,
    order_id: int,
    shipping_carrier: str,
    tracking_number: str
):
    history = ShipmentTrackingHistory(
        order_id=order_id,
        shipping_carrier=shipping_carrier,
        tracking_number=tracking_number
    )

    db.add(history)

    return history