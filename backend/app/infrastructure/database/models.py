from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.types import TZDateTime
from app.core.domain.enums import TicketStatus


class PriorityModel(Base):
    __tablename__ = "priorities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False, index=True)
    sort_order = Column(Integer, nullable=False, default=0)

    tickets = relationship("TicketModel", back_populates="priority")


class TicketModel(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text(1000), nullable=True)
    status = Column(String(20), default=TicketStatus.NEW, nullable=False)
    priority_id = Column(Integer, ForeignKey("priorities.id"), nullable=False, index=True)
    created_at = Column(TZDateTime(), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        TZDateTime(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    priority = relationship("PriorityModel", back_populates="tickets")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
