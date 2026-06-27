from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.infrastructure.database.base import Base
from app.core.domain.enums import TicketPriority, TicketStatus


class TicketModel(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text(1000), nullable=True)
    status = Column(String(20), default=TicketStatus.NEW, nullable=False)
    priority = Column(Integer, default=TicketPriority.NORMAL, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
