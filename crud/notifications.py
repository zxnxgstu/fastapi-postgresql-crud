from sqlalchemy.orm import Session

from models import PriceDropNotification


def get_user_notifications(
    db: Session,
    user_id: int
):
    return (
        db.query(PriceDropNotification)
        .filter(
            PriceDropNotification.user_id == user_id
        )
        .order_by(
            PriceDropNotification.created_at.desc()
        )
        .all()
    )


def get_user_notification(
    db: Session,
    user_id: int,
    notification_id: int
):
    return (
        db.query(PriceDropNotification)
        .filter(
            PriceDropNotification.id == notification_id,
            PriceDropNotification.user_id == user_id
        )
        .first()
    )


def mark_notification_as_read(
    db: Session,
    notification: PriceDropNotification
):
    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification