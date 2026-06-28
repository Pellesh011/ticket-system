from abc import abstractmethod

from app.core.domain.entities import Ticket
from app.core.domain.enums import TicketStatus
from app.core.repositories.base import BaseRepository


class ITicketRepository(BaseRepository[Ticket]):
    @abstractmethod
    async def get_filtered(
        self,
        status: TicketStatus | None = None,
        priority_id: int | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Ticket], int]:
        ...
