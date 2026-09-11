from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
from dependencies import get_current_user, get_db
from models import User
from schemas import PriceDropNotificationResponse


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get(
    "",
    response_model=list[PriceDropNotificationResponse]
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_user_notifications(
        db,
        current_user.id
    )


@router.patch(
    "/{notification_id}/read",
    response_model=PriceDropNotificationResponse
)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = crud.get_user_notification(
        db,
        current_user.id,
        notification_id
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return crud.mark_notification_as_read(
        db,
        notification
    )