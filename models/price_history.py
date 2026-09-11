from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(
        Integer,
        primary_key=True,
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

    changed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    product = relationship(
        "Product",
        back_populates="price_history"
    )