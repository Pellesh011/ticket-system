from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.entities import User
from app.core.repositories.user_repository import IUserRepository
from app.infrastructure.database.models import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,  # type: ignore[arg-type]
        username=model.username,  # type: ignore[arg-type]
        hashed_password=model.hashed_password,  # type: ignore[arg-type]
    )


def _from_entity(entity: User) -> UserModel:
    model = UserModel(
        username=entity.username,
        hashed_password=entity.hashed_password,
    )
    if entity.id is not None:
        model.id = entity.id  # type: ignore[assignment]
    return model


class SQLUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: int) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == id))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.username == username))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, entity: User) -> User:
        model = _from_entity(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, entity: User) -> User:
        if entity.id is None:
            return entity
        result = await self._session.execute(select(UserModel).where(UserModel.id == entity.id))
        model = result.scalar_one_or_none()
        if model is None:
            return entity
        model.username = entity.username  # type: ignore[assignment]
        model.hashed_password = entity.hashed_password  # type: ignore[assignment]
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, id: int) -> None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
