from sqlalchemy.orm import Session

from models import Order, ShipmentEvent
from schemas import ShipmentEventCreate


def get_order_shipment_events(
    db: Session,
    order_id: int
):
    return (
        db.query(ShipmentEvent)
        .filter(
            ShipmentEvent.order_id == order_id
        )
        .order_by(
            ShipmentEvent.created_at.asc(),
            ShipmentEvent.id.asc()
        )
        .all()
    )


def create_shipment_event(
    db: Session,
    order: Order,
    event_data: ShipmentEventCreate
):
    if order.status not in (
        "shipped",
        "completed",
    ):
        raise ValueError(
            "Shipment events can only be added to shipped orders"
        )

    event = ShipmentEvent(
        order_id=order.id,
        status=event_data.status,
        comment=event_data.comment
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event