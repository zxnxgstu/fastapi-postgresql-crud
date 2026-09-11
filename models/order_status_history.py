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


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey(
            "orders.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    old_status = Column(
        String(20),
        nullable=True
    )

    new_status = Column(
        String(20),
        nullable=False
    )

    changed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    order = relationship(
        "Order",
        back_populates="status_history"
    )

    __table_args__ = (
        CheckConstraint(
            """
            old_status IS NULL OR
            old_status IN (
                'pending',
                'paid',
                'shipped',
                'completed',
                'cancelled'
            )
            """,
            name="ck_order_status_history_old_status"
        ),
        CheckConstraint(
            """
            new_status IN (
                'pending',
                'paid',
                'shipped',
                'completed',
                'cancelled'
            )
            """,
            name="ck_order_status_history_new_status"
        ),
    )