from sqlalchemy.orm import Session

from models import User
from schemas import UserProfileUpdate


def update_user_profile(
    db: Session,
    user: User,
    update_data: UserProfileUpdate
):
    changes = update_data.model_dump(
        exclude_unset=True
    )

    if "username" in changes:
        new_username = changes["username"]

        if new_username is None:
            raise ValueError(
                "Username cannot be null"
            )

        existing_user = (
            db.query(User)
            .filter(
                User.username == new_username,
                User.id != user.id
            )
            .first()
        )

        if existing_user is not None:
            raise ValueError(
                "Username already exists"
            )

    if "email" in changes:
        new_email = changes["email"]

        if new_email is None:
            raise ValueError(
                "Email cannot be null"
            )

        existing_user = (
            db.query(User)
            .filter(
                User.email == new_email,
                User.id != user.id
            )
            .first()
        )

        if existing_user is not None:
            raise ValueError(
                "Email already exists"
            )

    for field, value in changes.items():
        setattr(
            user,
            field,
            value
        )

    return user