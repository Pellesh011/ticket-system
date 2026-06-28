import logging
from datetime import datetime, timezone

from app.core.domain.action_matrix import can_perform, can_transition
from app.core.domain.entities import Ticket
from app.core.domain.enums import TicketStatus
from app.core.domain.exceptions import (
    TicketActionNotAllowedError,
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
        return TicketResponse(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            status=ticket.status,
            priority_id=ticket.priority_id,
            priority_name=ticket.priority_name or "",
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
        )

    async def create_ticket(self, data: TicketCreate) -> TicketResponse:
        logger.info("Creating ticket: title=%s, priority_id=%d", data.title, data.priority_id)
        ticket = Ticket(title=data.title, description=data.description, priority_id=data.priority_id)
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
        priority_id: int | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[TicketResponse], int]:
        skip = (page - 1) * page_size
        tickets, total = await self._repo.get_filtered(
            status=status,
            priority_id=priority_id,
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
        if not can_perform(ticket.status, "edit"):
            raise TicketActionNotAllowedError("edit", ticket.status)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return self._to_response(ticket)
        if "title" in update_data:
            ticket.title = update_data["title"]
        if "description" in update_data:
            ticket.description = update_data["description"]
        if "priority_id" in update_data:
            ticket.priority_id = update_data["priority_id"]
        ticket.updated_at = datetime.now(timezone.utc)
        updated = await self._repo.update(ticket)
        logger.info("Ticket updated: id=%d, fields=%s", ticket_id, list(update_data.keys()))
        return self._to_response(updated)

    async def update_status(self, ticket_id: int, data: TicketStatusUpdate) -> TicketResponse:
        ticket = await self._repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        if not can_perform(ticket.status, "transition"):
            raise TicketActionNotAllowedError("transition", ticket.status)
        if not can_transition(ticket.status, data.status):
            raise TicketActionNotAllowedError(f"transition from '{ticket.status}' to '{data.status}'", ticket.status)
        logger.info(
            "Ticket status change: id=%d, %s -> %s",
            ticket_id,
            ticket.status,
            data.status,
        )
        ticket.status = data.status
        ticket.updated_at = datetime.now(timezone.utc)
        updated = await self._repo.update(ticket)
        return self._to_response(updated)

    async def delete_ticket(self, ticket_id: int) -> None:
        ticket = await self._repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        if not can_perform(ticket.status, "delete"):
            raise TicketActionNotAllowedError("delete", ticket.status)
        await self._repo.delete(ticket_id)
        logger.info("Ticket deleted: id=%d", ticket_id)
