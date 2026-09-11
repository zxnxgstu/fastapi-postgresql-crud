from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from database import Base


class ShipmentTrackingHistory(Base):
    __tablename__ = "shipment_tracking_history"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    shipping_carrier = Column(
        String(100),
        nullable=False
    )

    tracking_number = Column(
        String(100),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="tracking_history"
    )