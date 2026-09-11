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

def revoke_all_user_refresh_tokens(
    db: Session,
    user_id: int
):
    sessions = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked.is_(False)
        )
        .all()
    )

    for session in sessions:
        session.revoked = True

    return len(sessions)

def get_user_refresh_sessions(
    db: Session,
    user_id: int
):
    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked.is_(False)
        )
        .order_by(
            RefreshToken.created_at.desc(),
            RefreshToken.id.desc()
        )
        .all()
    )


def get_user_refresh_session(
    db: Session,
    session_id: int,
    user_id: int
):
    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.id == session_id,
            RefreshToken.user_id == user_id
        )
        .first()
    )