import pytest

from app.core.domain.enums import TicketPriority, TicketStatus
from app.core.domain.exceptions import (
    TicketDoneCannotChangeStatusError,
    TicketDoneCannotDeleteError,
    TicketDoneCannotEditError,
    TicketNotFoundError,
)
from app.core.domain.entities import Ticket
from app.core.domain.schemas import TicketCreate, TicketStatusUpdate, TicketUpdate
from app.services.ticket_service import TicketService


from datetime import datetime, timezone


class FakeTicketRepository:
    def __init__(self):
        self._storage: dict[int, Ticket] = {}
        self._next_id = 1

    async def get_by_id(self, id: int) -> Ticket | None:
        return self._storage.get(id)

    async def create(self, entity: Ticket) -> Ticket:
        entity.id = self._next_id
        self._next_id += 1
        entity.status = entity.status or TicketStatus.NEW
        entity.created_at = entity.created_at or datetime.now(timezone.utc)
        entity.updated_at = entity.updated_at or datetime.now(timezone.utc)
        self._storage[entity.id] = entity  # type: ignore[index]
        return entity

    async def update(self, entity: Ticket) -> Ticket:
        entity.updated_at = datetime.now(timezone.utc)
        self._storage[entity.id] = entity  # type: ignore[index]
        return entity

    async def delete(self, id: int) -> None:
        self._storage.pop(id, None)

    async def get_filtered(
        self,
        status=None,
        priority=None,
        search=None,
        sort_by="created_at",
        sort_order="desc",
        skip=0,
        limit=20,
    ):
        items = list(self._storage.values())
        total = len(items)
        return items[skip:skip + limit], total


@pytest.fixture
def service():
    return TicketService(FakeTicketRepository())


class TestTicketService:
    async def test_create_ticket(self, service: TicketService):
        data = TicketCreate(title="Test ticket", priority=TicketPriority.HIGH)
        result = await service.create_ticket(data)
        assert result.title == "Test ticket"
        assert result.priority == TicketPriority.HIGH
        assert result.status == TicketStatus.NEW
        assert result.id is not None

    async def test_create_ticket_default_priority(self, service: TicketService):
        data = TicketCreate(title="Test ticket")
        result = await service.create_ticket(data)
        assert result.priority == TicketPriority.NORMAL
        assert result.status == TicketStatus.NEW

    async def test_get_ticket_not_found(self, service: TicketService):
        with pytest.raises(TicketNotFoundError):
            await service.get_ticket(999)

    async def test_update_ticket(self, service: TicketService):
        created = await service.create_ticket(TicketCreate(title="Original"))
        updated = await service.update_ticket(
            created.id,
            TicketUpdate(title="Updated"),
        )
        assert updated.title == "Updated"
        assert updated.id == created.id

    async def test_update_done_ticket_raises_error(self, service: TicketService):
        created = await service.create_ticket(TicketCreate(title="Test"))
        await service.update_status(created.id, TicketStatusUpdate(status=TicketStatus.DONE))
        with pytest.raises(TicketDoneCannotEditError):
            await service.update_ticket(created.id, TicketUpdate(title="New"))

    async def test_change_status(self, service: TicketService):
        created = await service.create_ticket(TicketCreate(title="Test"))
        result = await service.update_status(
            created.id,
            TicketStatusUpdate(status=TicketStatus.IN_PROGRESS),
        )
        assert result.status == TicketStatus.IN_PROGRESS

    async def test_cannot_change_status_from_done(self, service: TicketService):
        created = await service.create_ticket(TicketCreate(title="Test"))
        await service.update_status(created.id, TicketStatusUpdate(status=TicketStatus.DONE))
        with pytest.raises(TicketDoneCannotChangeStatusError):
            await service.update_status(
                created.id,
                TicketStatusUpdate(status=TicketStatus.NEW),
            )

    async def test_delete_ticket(self, service: TicketService):
        created = await service.create_ticket(TicketCreate(title="Test"))
        await service.delete_ticket(created.id)
        with pytest.raises(TicketNotFoundError):
            await service.get_ticket(created.id)

    async def test_delete_done_ticket_raises_error(self, service: TicketService):
        created = await service.create_ticket(TicketCreate(title="Test"))
        await service.update_status(created.id, TicketStatusUpdate(status=TicketStatus.DONE))
        with pytest.raises(TicketDoneCannotDeleteError):
            await service.delete_ticket(created.id)

    async def test_delete_nonexistent_ticket(self, service: TicketService):
        with pytest.raises(TicketNotFoundError):
            await service.delete_ticket(999)

    async def test_list_tickets_pagination(self, service: TicketService):
        for i in range(25):
            await service.create_ticket(TicketCreate(title=f"Ticket {i}"))
        tickets, total = await service.get_tickets(page=1, page_size=10)
        assert len(tickets) == 10
        assert total == 25
        tickets_page2, _ = await service.get_tickets(page=2, page_size=10)
        assert len(tickets_page2) == 10
