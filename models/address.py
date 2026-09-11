from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    city = Column(
        String(100),
        nullable=False
    )

    street = Column(
        String(200),
        nullable=False
    )

    postal_code = Column(
        String(30),
        nullable=False
    )

    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    user = relationship(
        "User",
        back_populates="addresses"
    )