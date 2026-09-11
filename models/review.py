from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


class Review(Base):
    __tablename__ = "reviews"

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

    rating = Column(
        Integer,
        nullable=False
    )

    comment = Column(
        String(1000),
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="reviews"
    )

    product = relationship(
        "Product",
        back_populates="reviews"
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_review_user_product"
        ),
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_reviews_rating"
        ),
    )