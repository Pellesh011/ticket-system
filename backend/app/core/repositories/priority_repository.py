from abc import abstractmethod

from app.core.domain.entities import Priority
from app.core.repositories.base import BaseRepository


class IPriorityRepository(BaseRepository[Priority]):
    @abstractmethod
    async def get_all(self) -> list[Priority]:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Priority | None:
        ...
