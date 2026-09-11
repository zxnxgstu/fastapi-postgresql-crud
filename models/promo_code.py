from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)

from database import Base


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    discount_percent = Column(
        Integer,
        nullable=False
    )

    active = Column(
        Boolean,
        nullable=False,
        server_default="true"
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    min_order_amount = Column(
        Integer,
        nullable=False,
        server_default="0"
    )

    max_uses = Column(
        Integer,
        nullable=True
    )

    used_count = Column(
        Integer,
        nullable=False,
        server_default="0"
    )