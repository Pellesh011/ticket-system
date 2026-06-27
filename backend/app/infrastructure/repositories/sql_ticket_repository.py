from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.enums import TicketPriority, TicketStatus
from app.core.domain.models import Ticket
from app.core.repositories.ticket_repository import ITicketRepository


class SQLTicketRepository(ITicketRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: int) -> Ticket | None:
        result = await self._session.execute(select(Ticket).where(Ticket.id == id))
        return result.scalar_one_or_none()

    async def create(self, entity: Ticket) -> Ticket:
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: Ticket) -> Ticket:
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def delete(self, id: int) -> None:
        ticket = await self.get_by_id(id)
        if ticket:
            await self._session.delete(ticket)
            await self._session.commit()

    async def get_filtered(
        self,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Ticket], int]:
        query = select(Ticket)
        count_query = select(func.count(Ticket.id))

        if status:
            query = query.where(Ticket.status == status)
            count_query = count_query.where(Ticket.status == status)

        if priority:
            query = query.where(Ticket.priority == priority)
            count_query = count_query.where(Ticket.priority == priority)

        if search:
            pattern = f"%{search}%"
            search_filter = Ticket.title.ilike(pattern) | Ticket.description.ilike(pattern)
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        sort_column = getattr(Ticket, sort_by, Ticket.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        result = await self._session.execute(query.offset(skip).limit(limit))
        tickets = list(result.scalars().all())

        return tickets, total
