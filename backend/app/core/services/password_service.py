from typing import Protocol


class IPasswordService(Protocol):
    async def hash(self, password: str) -> str: ...

    async def verify(self, plain_password: str, hashed_password: str) -> bool: ...
