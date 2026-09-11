from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, CheckConstraint, func
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel, Field, model_validator


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    total_price = Column(
        Integer,
        nullable=False
    )

    promo_code = Column(
    String(50),
    nullable=True
)

    discount_percent = Column(
    Integer,
    nullable=False,
    server_default="0"
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

    shipping_city = Column(
        String(100),
        nullable=True
    )

    shipping_street = Column(
        String(255),
        nullable=True
    )

    shipping_postal_code = Column(
        String(20),
        nullable=True
    )

    user = relationship(
            "User",
            back_populates="orders"
        )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'paid', 'shipped', 'completed', 'cancelled')",
            name="ck_orders_status"
        ),
    )
    payment = relationship(
    "Payment",
    back_populates="order",
    uselist=False,
    cascade="all, delete-orphan"
)
    status_history = relationship(
    "OrderStatusHistory",
    back_populates="order",
    cascade="all, delete-orphan",
    order_by="OrderStatusHistory.changed_at"
)
    delivery_method_id = Column(
    Integer,
    ForeignKey(
        "delivery_methods.id",
        ondelete="SET NULL"
    ),
    nullable=True
)

    delivery_method_code = Column(
    String(50),
    nullable=True
)

    delivery_method_name = Column(
    String(100),
    nullable=True
)

    delivery_price = Column(
    Integer,
    nullable=False,
    default=0,
    server_default="0"
)

    delivery_method_id = Column(
    Integer,
    ForeignKey(
        "delivery_methods.id",
        ondelete="SET NULL"
    ),
    nullable=True
)

    delivery_method = relationship(
    "DeliveryMethod"
)
    customer_note = Column(
    String(500),
    nullable=True
)