import pytest

from app.core.domain.entities import Priority
from app.services.priority_service import PriorityService


class FakePriorityRepository:
    def __init__(self):
        self._storage: dict[int, Priority] = {}
        self._next_id = 1

    async def get_all(self) -> list[Priority]:
        return list(self._storage.values())

    async def get_by_id(self, id: int) -> Priority | None:
        return self._storage.get(id)

    async def get_by_name(self, name: str) -> Priority | None:
        for p in self._storage.values():
            if p.name == name:
                return p
        return None

    async def create(self, entity: Priority) -> Priority:
        entity.id = self._next_id
        self._next_id += 1
        self._storage[entity.id] = entity
        return entity

    async def update(self, entity: Priority) -> Priority:
        self._storage[entity.id] = entity
        return entity

    async def delete(self, id: int) -> None:
        self._storage.pop(id, None)


@pytest.fixture
def service():
    return PriorityService(FakePriorityRepository())


class TestPriorityService:
    async def test_create_priority(self, service: PriorityService):
        result = await service.create("urgent", sort_order=5)
        assert result.name == "urgent"
        assert result.sort_order == 5
        assert result.id is not None

    async def test_get_all(self, service: PriorityService):
        await service.create("low")
        await service.create("high")
        priorities = await service.get_all()
        assert len(priorities) == 2

    async def test_get_by_id(self, service: PriorityService):
        created = await service.create("critical")
        result = await service.get_by_id(created.id)
        assert result is not None
        assert result.name == "critical"

    async def test_get_by_id_not_found(self, service: PriorityService):
        result = await service.get_by_id(999)
        assert result is None

    async def test_update_priority(self, service: PriorityService):
        created = await service.create("old")
        updated = await service.update(created.id, name="new", sort_order=10)
        assert updated is not None
        assert updated.name == "new"
        assert updated.sort_order == 10

    async def test_update_priority_not_found(self, service: PriorityService):
        result = await service.update(999, name="whatever")
        assert result is None

    async def test_delete_priority(self, service: PriorityService):
        created = await service.create("temp")
        result = await service.delete(created.id)
        assert result is True
        assert await service.get_by_id(created.id) is None

    async def test_delete_priority_not_found(self, service: PriorityService):
        result = await service.delete(999)
        assert result is False
