from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Integer,
    String,
)

from database import Base


class DeliveryMethod(Base):
    __tablename__ = "delivery_methods"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    code = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    price = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="ck_delivery_methods_price_non_negative"
        ),
    )