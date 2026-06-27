from abc import abstractmethod
from typing import Protocol

from app.core.domain.enums import TicketPriority, TicketStatus
from app.core.domain.schemas import (
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate,
    TicketUpdate,
)


class ITicketService(Protocol):
    @abstractmethod
    async def create_ticket(self, data: TicketCreate) -> TicketResponse:
        ...

    @abstractmethod
    async def get_ticket(self, ticket_id: int) -> TicketResponse:
        ...

    @abstractmethod
    async def get_tickets(
        self,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[TicketResponse], int]:
        ...

    @abstractmethod
    async def update_ticket(self, ticket_id: int, data: TicketUpdate) -> TicketResponse:
        ...

    @abstractmethod
    async def update_status(self, ticket_id: int, data: TicketStatusUpdate) -> TicketResponse:
        ...

    @abstractmethod
    async def delete_ticket(self, ticket_id: int) -> None:
        ...
