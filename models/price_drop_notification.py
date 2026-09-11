from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


class PriceDropNotification(Base):
    __tablename__ = "price_drop_notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    old_price = Column(
        Integer,
        nullable=False
    )

    new_price = Column(
        Integer,
        nullable=False
    )

    is_read = Column(
        Boolean,
        nullable=False,
        server_default="false"
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="price_drop_notifications"
    )

    product = relationship(
        "Product",
        back_populates="price_drop_notifications"
    )