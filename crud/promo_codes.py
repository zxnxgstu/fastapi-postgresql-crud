from sqlalchemy.orm import Session

from models import PromoCode
from schemas import PromoCodeCreate, PromoCodeUpdate


def get_promo_codes(
    db: Session,
    active: bool | None = None,
    skip: int = 0,
    limit: int = 20
):
    query = db.query(PromoCode)

    if active is not None:
        query = query.filter(
            PromoCode.active == active
        )

    return (
        query
        .order_by(PromoCode.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_promo_code_by_id(
    db: Session,
    promo_code_id: int
):
    return (
        db.query(PromoCode)
        .filter(PromoCode.id == promo_code_id)
        .first()
    )


def get_promo_code_by_code(
    db: Session,
    code: str
):
    return (
        db.query(PromoCode)
        .filter(PromoCode.code == code)
        .first()
    )


def create_promo_code(
    db: Session,
    promo_code: PromoCodeCreate
):
    db_promo_code = PromoCode(
        code=promo_code.code,
        discount_percent=promo_code.discount_percent,
        active=promo_code.active,
        expires_at=promo_code.expires_at,
        min_order_amount=promo_code.min_order_amount,
        max_uses=promo_code.max_uses,
        used_count=0
    )

    db.add(db_promo_code)
    db.commit()
    db.refresh(db_promo_code)

    return db_promo_code


def update_promo_code(
    db: Session,
    promo_code: PromoCode,
    update_data: PromoCodeUpdate
):
    changes = update_data.model_dump(
        exclude_unset=True
    )

    for field, value in changes.items():
        setattr(
            promo_code,
            field,
            value
        )

    return promo_code