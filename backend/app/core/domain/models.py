from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.infrastructure.database.base import Base
from app.core.domain.enums import TicketPriority, TicketStatus


class Ticket(Base):
    __tablename__ = "tickets"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(120), nullable=False)
    description: str | None = Column(Text(1000), nullable=True)
    status: TicketStatus = Column(String(20), default=TicketStatus.NEW, nullable=False)
    priority: TicketPriority = Column(String(10), default=TicketPriority.NORMAL, nullable=False)
    created_at: datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password: str = Column(String(128), nullable=False)
