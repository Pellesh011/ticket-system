from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.core.domain.enums import TicketStatus


@dataclass
class Priority:
    name: str
    sort_order: int = 0
    id: int | None = None


@dataclass
class Ticket:
    title: str
    description: str | None = None
    status: TicketStatus = TicketStatus.NEW
    priority_id: int = 2
    priority_name: str = ""
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class User:
    username: str
    hashed_password: str
    id: int | None = None
