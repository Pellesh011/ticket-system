import logging
from math import ceil

from app.core.domain.entities import Ticket
from app.core.domain.enums import TicketPriority, TicketStatus
from app.core.domain.exceptions import (
    TicketDoneCannotChangeStatusError,
    TicketDoneCannotDeleteError,
    TicketDoneCannotEditError,
    TicketNotFoundError,
)
from app.core.domain.schemas import (
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.core.repositories.ticket_repository import ITicketRepository

logger = logging.getLogger(__name__)


class TicketService:
    def __init__(self, ticket_repository: ITicketRepository) -> None:
        self._repo = ticket_repository

    @staticmethod
    def _to_response(ticket: Ticket) -> TicketResponse:
        return TicketResponse.model_validate(ticket)

    async def create_ticket(self, data: TicketCreate) -> TicketResponse:
        logger.info("Creating ticket: title=%s, priority=%s", data.title, data.priority)
        ticket = Ticket(title=data.title, description=data.description, priority=data.priority)
        created = await self._repo.create(ticket)
        logger.info("Ticket created: id=%d", created.id)
        return self._to_response(created)

    async def get_ticket(self, ticket_id: int) -> TicketResponse:
        ticket = await self._repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        return self._to_response(ticket)

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
        skip = (page - 1) * page_size
        tickets, total = await self._repo.get_filtered(
            status=status,
            priority=priority,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=page_size,
        )
        return [self._to_response(t) for t in tickets], total

    async def update_ticket(self, ticket_id: int, data: TicketUpdate) -> TicketResponse:
        ticket = await self._repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        if ticket.status == TicketStatus.DONE:
            raise TicketDoneCannotEditError()
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return self._to_response(ticket)
        for field, value in update_data.items():
            setattr(ticket, field, value)
        updated = await self._repo.update(ticket)
        logger.info("Ticket updated: id=%d, fields=%s", ticket_id, list(update_data.keys()))
        return self._to_response(updated)

    async def update_status(self, ticket_id: int, data: TicketStatusUpdate) -> TicketResponse:
        ticket = await self._repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        if ticket.status == TicketStatus.DONE:
            raise TicketDoneCannotChangeStatusError()
        logger.info(
            "Ticket status change: id=%d, %s -> %s",
            ticket_id,
            ticket.status,
            data.status,
        )
        ticket.status = data.status
        updated = await self._repo.update(ticket)
        return self._to_response(updated)

    async def delete_ticket(self, ticket_id: int) -> None:
        ticket = await self._repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        if ticket.status == TicketStatus.DONE:
            raise TicketDoneCannotDeleteError()
        await self._repo.delete(ticket_id)
        logger.info("Ticket deleted: id=%d", ticket_id)

    async def get_total_pages(self, page_size: int = 20, **filters) -> int:
        _, total = await self._repo.get_filtered(**filters, limit=1)
        return max(1, ceil(total / page_size))
