from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    amount = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        server_default="pending"
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    order = relationship(
        "Order",
        back_populates="payment"
    )

    __table_args__ = (
        CheckConstraint(
        "status IN ('pending', 'paid', 'failed', 'refunded')",
        name="ck_payments_status"
),
    )