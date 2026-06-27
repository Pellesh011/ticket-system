from abc import abstractmethod
from typing import Protocol


class IAuthService(Protocol):
    @abstractmethod
    async def login(self, username: str, password: str) -> str:
        ...

    @abstractmethod
    async def verify_admin(self, token: str) -> bool:
        ...
