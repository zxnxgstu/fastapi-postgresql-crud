from sqlalchemy.orm import Session

from models import Order, ShipmentEvent
from schemas import ShipmentEventCreate

from .order_status_history import create_order_status_history


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
    if order.status != "shipped":
        raise ValueError(
            "Shipment events can only be added to shipped orders"
        )

    last_event = (
        db.query(ShipmentEvent)
        .filter(ShipmentEvent.order_id == order.id)
        .order_by(
            ShipmentEvent.created_at.desc(),
            ShipmentEvent.id.desc()
        )
        .first()
    )

    allowed_transitions = {
        None: "picked_up",
        "picked_up": "in_transit",
        "in_transit": "out_for_delivery",
        "out_for_delivery": "delivered",
    }

    current_status = (
        last_event.status
        if last_event is not None
        else None
    )

    expected_status = allowed_transitions.get(current_status)

    if event_data.status != expected_status:
        raise ValueError(
            "Invalid shipment status transition"
        )

    event = ShipmentEvent(
        order_id=order.id,
        status=event_data.status,
        comment=event_data.comment
    )

    db.add(event)

    if event_data.status == "delivered":
        old_status = order.status
        order.status = "completed"

        create_order_status_history(
            db=db,
            order_id=order.id,
            old_status=old_status,
            new_status="completed"
        )

    db.commit()
    db.refresh(event)

    return event