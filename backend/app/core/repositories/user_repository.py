from abc import abstractmethod

from app.core.domain.entities import User
from app.core.repositories.base import BaseRepository


class IUserRepository(BaseRepository[User]):
    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        ...
