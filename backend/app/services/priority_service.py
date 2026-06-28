import logging

from app.core.domain.entities import Priority
from app.core.repositories.priority_repository import IPriorityRepository

logger = logging.getLogger(__name__)


class PriorityService:
    def __init__(self, priority_repository: IPriorityRepository) -> None:
        self._repo = priority_repository

    async def get_all(self) -> list[Priority]:
        return await self._repo.get_all()

    async def get_by_id(self, priority_id: int) -> Priority | None:
        return await self._repo.get_by_id(priority_id)

    async def create(self, name: str, sort_order: int = 0) -> Priority:
        logger.info("Creating priority: name=%s, sort_order=%d", name, sort_order)
        entity = Priority(name=name, sort_order=sort_order)
        created = await self._repo.create(entity)
        logger.info("Priority created: id=%d", created.id)
        return created

    async def update(self, priority_id: int, name: str | None = None, sort_order: int | None = None) -> Priority | None:
        entity = await self._repo.get_by_id(priority_id)
        if not entity:
            return None
        if name is not None:
            entity.name = name
        if sort_order is not None:
            entity.sort_order = sort_order
        updated = await self._repo.update(entity)
        logger.info("Priority updated: id=%d", priority_id)
        return updated

    async def delete(self, priority_id: int) -> bool:
        entity = await self._repo.get_by_id(priority_id)
        if not entity:
            return False
        await self._repo.delete(priority_id)
        logger.info("Priority deleted: id=%d", priority_id)
        return True
