from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.domain.entities import Ticket
from app.core.domain.enums import TicketStatus
from app.core.repositories.ticket_repository import ITicketRepository
from app.infrastructure.database.models import PriorityModel, TicketModel


def _to_entity(model: TicketModel) -> Ticket:
    priority_name = ""
    if model.priority is not None:
        priority_name = model.priority.name
    return Ticket(
        id=model.id,
        title=model.title,
        description=model.description,
        status=model.status,
        priority_id=model.priority_id,
        priority_name=priority_name,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _from_entity(entity: Ticket) -> TicketModel:
    model = TicketModel(
        title=entity.title,
        description=entity.description,
        status=entity.status,
        priority_id=entity.priority_id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
    if entity.id is not None:
        model.id = entity.id
    return model


def _apply_to_model(entity: Ticket, model: TicketModel) -> None:
    model.title = entity.title
    model.description = entity.description
    model.status = str(entity.status)
    model.priority_id = entity.priority_id
    model.updated_at = entity.updated_at


def _base_query():
    return select(TicketModel).options(joinedload(TicketModel.priority))


class SQLTicketRepository(ITicketRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: int) -> Ticket | None:
        result = await self._session.execute(
            _base_query().where(TicketModel.id == id)
        )
        model = result.unique().scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, entity: Ticket) -> Ticket:
        model = _from_entity(entity)
        self._session.add(model)
        await self._session.flush()
        result = await self._session.execute(
            _base_query().where(TicketModel.id == model.id)
        )
        model = result.unique().scalar_one_or_none()
        return _to_entity(model) if model else entity

    async def update(self, entity: Ticket) -> Ticket:
        if entity.id is None:
            return entity
        result = await self._session.execute(
            _base_query().where(TicketModel.id == entity.id)
        )
        model = result.unique().scalar_one_or_none()
        if model is None:
            return entity
        _apply_to_model(entity, model)
        await self._session.flush()
        result = await self._session.execute(
            _base_query()
            .where(TicketModel.id == entity.id)
            .execution_options(populate_existing=True)
        )
        model = result.unique().scalar_one_or_none()
        return _to_entity(model) if model else entity

    async def delete(self, id: int) -> None:
        model = await self._get_model_by_id(id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def _get_model_by_id(self, id: int) -> TicketModel | None:
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == id)
        )
        return result.scalar_one_or_none()

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
        query = _base_query()
        count_query = select(func.count(TicketModel.id))

        if status:
            query = query.where(TicketModel.status == status)
            count_query = count_query.where(TicketModel.status == status)

        if priority_id:
            query = query.where(TicketModel.priority_id == priority_id)
            count_query = count_query.where(TicketModel.priority_id == priority_id)

        if search:
            pattern = f"%{search}%"
            search_filter = TicketModel.title.ilike(pattern) | TicketModel.description.ilike(pattern)
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if sort_by == "priority":
            query = query.outerjoin(PriorityModel, TicketModel.priority_id == PriorityModel.id).order_by(
                PriorityModel.sort_order.desc() if sort_order == "desc" else PriorityModel.sort_order.asc()
            )
        else:
            sort_column = getattr(TicketModel, sort_by, TicketModel.created_at)
            query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())

        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        result = await self._session.execute(query.offset(skip).limit(limit))
        models = list(result.unique().scalars().all())

        return [_to_entity(m) for m in models], total
