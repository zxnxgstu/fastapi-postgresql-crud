from datetime import datetime

from sqlalchemy.orm import Session

from models import RefreshToken


def create_refresh_token_session(
    db: Session,
    user_id: int,
    jti: str,
    expires_at: datetime
):
    session = RefreshToken(
        user_id=user_id,
        jti=jti,
        expires_at=expires_at,
        revoked=False
    )

    db.add(session)

    return session


def get_refresh_token_session(
    db: Session,
    jti: str
):
    return (
        db.query(RefreshToken)
        .filter(RefreshToken.jti == jti)
        .first()
    )


def revoke_refresh_token_session(
    session: RefreshToken
):
    session.revoked = True

    return session