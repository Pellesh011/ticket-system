from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.entities import Priority
from app.core.repositories.priority_repository import IPriorityRepository
from app.infrastructure.database.models import PriorityModel


def _to_entity(model: PriorityModel) -> Priority:
    return Priority(
        id=model.id,
        name=model.name,
        sort_order=model.sort_order,
    )


def _from_entity(entity: Priority) -> PriorityModel:
    model = PriorityModel(
        name=entity.name,
        sort_order=entity.sort_order,
    )
    if entity.id is not None:
        model.id = entity.id
    return model


class SQLPriorityRepository(IPriorityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: int) -> Priority | None:
        result = await self._session.execute(select(PriorityModel).where(PriorityModel.id == id))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Priority | None:
        result = await self._session.execute(select(PriorityModel).where(PriorityModel.name == name))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_all(self) -> list[Priority]:
        result = await self._session.execute(
            select(PriorityModel).order_by(PriorityModel.sort_order)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def create(self, entity: Priority) -> Priority:
        model = _from_entity(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, entity: Priority) -> Priority:
        if entity.id is None:
            return entity
        model = await self._session.get(PriorityModel, entity.id)
        if model is None:
            return entity
        model.name = entity.name
        model.sort_order = entity.sort_order
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, id: int) -> None:
        model = await self._session.get(PriorityModel, id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
