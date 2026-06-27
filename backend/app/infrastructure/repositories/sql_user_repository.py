from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.models import User
from app.core.repositories.user_repository import IUserRepository


class SQLUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: int) -> User | None:
        result = await self._session.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, entity: User) -> User:
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: User) -> User:
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def delete(self, id: int) -> None:
        user = await self.get_by_id(id)
        if user:
            await self._session.delete(user)
            await self._session.commit()
