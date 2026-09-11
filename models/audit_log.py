from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    actor_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    action = Column(
        String(100),
        nullable=False,
        index=True
    )

    entity_type = Column(
        String(50),
        nullable=False,
        index=True
    )

    entity_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    details = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )