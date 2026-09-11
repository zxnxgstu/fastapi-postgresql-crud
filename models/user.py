from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password = Column(String(255), nullable=False)

    role = Column(String(20), nullable=False, server_default="user")
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    cart_items = relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    wishlist_items = relationship(
    "WishlistItem",
    back_populates="user",
    cascade="all, delete-orphan"
    )
    reviews = relationship(
    "Review",
    back_populates="user",
    cascade="all, delete-orphan"
    )
    price_drop_notifications = relationship(
        "PriceDropNotification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    addresses = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )