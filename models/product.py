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
    reviews = relationship(
    "Review",
    back_populates="product",
    cascade="all, delete-orphan"
    )

    @property
    def reviews_count(self):
        return len(self.reviews)

    @property
    def average_rating(self):
        if not self.reviews:
            return 0.0

        return round(
            sum(review.rating for review in self.reviews)
            / len(self.reviews),
            2
        )
    price_history = relationship(
    "PriceHistory",
    back_populates="product",
    cascade="all, delete-orphan"
    )
    price_drop_notifications = relationship(
    "PriceDropNotification",
    back_populates="product",
    cascade="all, delete-orphan"
)
    stock_movements = relationship(
    "StockMovement",
    back_populates="product",
    cascade="all, delete-orphan",
    order_by="StockMovement.created_at"
)