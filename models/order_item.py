from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey(
            "products.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    product_name = Column(
        String(100),
        nullable=False
    )

    price = Column(
        Integer,
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="items"
    )
    line_total = Column(
    Integer,
    nullable=False,
    default=0,
    server_default="0"
)