from abc import abstractmethod

from app.core.domain.entities import Ticket
from app.core.domain.enums import TicketPriority, TicketStatus
from app.core.repositories.base import BaseRepository


class ITicketRepository(BaseRepository[Ticket]):
    @abstractmethod
    async def get_filtered(
        self,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        search: str | None = None,
        sort_by: list[str] | None = None,
        sort_order: list[str] | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Ticket], int]:
        ...
