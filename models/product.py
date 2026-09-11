from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    in_stock = Column(Boolean, nullable=False)
    stock_quantity = Column(
    Integer,
    nullable=False,
    server_default="0"
)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
        index=True
    )

    category = relationship(
        "Category",
        back_populates="products"
    )
    cart_items = relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    wishlist_items = relationship(
    "WishlistItem",
    back_populates="product",
    cascade="all, delete-orphan"
)