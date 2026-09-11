from sqlalchemy import Boolean, Column, Integer, String

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