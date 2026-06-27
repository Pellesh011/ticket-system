from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.entities import Ticket
from app.core.domain.enums import TicketPriority, TicketStatus
from app.core.repositories.ticket_repository import ITicketRepository
from app.infrastructure.database.models import TicketModel


def _to_entity(model: TicketModel) -> Ticket:
    return Ticket(
        id=model.id,  # type: ignore[arg-type]
        title=model.title,  # type: ignore[arg-type]
        description=model.description,  # type: ignore[arg-type]
        status=model.status,  # type: ignore[arg-type]
        priority=model.priority,  # type: ignore[arg-type]
        created_at=model.created_at,  # type: ignore[arg-type]
        updated_at=model.updated_at,  # type: ignore[arg-type]
    )


def _from_entity(entity: Ticket) -> TicketModel:
    model = TicketModel(
        title=entity.title,
        description=entity.description,
        status=entity.status,
        priority=entity.priority,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
    if entity.id is not None:
        model.id = entity.id  # type: ignore[assignment]
    return model


def _apply_to_model(entity: Ticket, model: TicketModel) -> None:
    model.title = entity.title  # type: ignore[assignment]
    model.description = entity.description  # type: ignore[assignment]
    model.status = str(entity.status)  # type: ignore[assignment]
    model.priority = str(entity.priority)  # type: ignore[assignment]
    model.updated_at = entity.updated_at  # type: ignore[assignment]


class SQLTicketRepository(ITicketRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: int) -> Ticket | None:
        result = await self._session.execute(select(TicketModel).where(TicketModel.id == id))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, entity: Ticket) -> Ticket:
        model = _from_entity(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, entity: Ticket) -> Ticket:
        if entity.id is None:
            return entity
        model = await self._get_model_by_id(entity.id)
        if model is None:
            return entity
        _apply_to_model(entity, model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, id: int) -> None:
        model = await self._get_model_by_id(id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def _get_model_by_id(self, id: int) -> TicketModel | None:
        result = await self._session.execute(select(TicketModel).where(TicketModel.id == id))
        return result.scalar_one_or_none()

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
        """Get filtered, sorted, paginated tickets.

        Note: `search` uses `ILIKE %pattern%` which causes full table scans.
        For production use with large datasets, consider FTS5 (SQLite) or
        a dedicated search engine.
        """
        query = select(TicketModel)
        count_query = select(func.count(TicketModel.id))

        if status:
            query = query.where(TicketModel.status == status)
            count_query = count_query.where(TicketModel.status == status)

        if priority:
            query = query.where(TicketModel.priority == priority)
            count_query = count_query.where(TicketModel.priority == priority)

        if search:
            pattern = f"%{search}%"
            search_filter = TicketModel.title.ilike(pattern) | TicketModel.description.ilike(pattern)
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if sort_by == "priority":
            sort_column = case(
                (TicketModel.priority == "high", 0),
                (TicketModel.priority == "normal", 1),
                (TicketModel.priority == "low", 2),
                else_=3,
            )
        else:
            sort_column = getattr(TicketModel, sort_by, TicketModel.created_at)
        query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())

        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        result = await self._session.execute(query.offset(skip).limit(limit))
        models = list(result.scalars().all())

        return [_to_entity(m) for m in models], total
