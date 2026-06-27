import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ADMIN_PASSWORD", "admin")

from app.core.domain.entities import User  # noqa: E402
from app.infrastructure.database.base import Base  # noqa: E402
from app.infrastructure.database.session import get_session  # noqa: E402
from app.infrastructure.repositories.sql_user_repository import SQLUserRepository  # noqa: E402
from app.infrastructure.services.password_service import PasswordService  # noqa: E402
from app.main import app  # noqa: E402

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def _seed_test_admin(session: AsyncSession) -> None:
    repo = SQLUserRepository(session)
    password_service = PasswordService()
    admin = await repo.get_by_username("admin")
    if not admin:
        admin_user = User(
            username="admin",
            hashed_password=password_service.hash("admin"),
        )
        await repo.create(admin_user)
        await session.commit()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await _seed_test_admin(session)
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(async_client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    response = await async_client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin",
    })
    token = response.json()["access_token"]
    async_client.headers["Authorization"] = f"Bearer {token}"
    yield async_client
