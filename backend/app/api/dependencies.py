from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.exceptions import UnauthorizedError
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.sql_priority_repository import SQLPriorityRepository
from app.infrastructure.repositories.sql_ticket_repository import SQLTicketRepository
from app.infrastructure.repositories.sql_user_repository import SQLUserRepository
from app.infrastructure.services.password_service import PasswordService
from app.services.auth_service import AuthService
from app.services.priority_service import PriorityService
from app.services.ticket_service import TicketService


async def get_ticket_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AsyncGenerator[TicketService, None]:
    repository = SQLTicketRepository(session)
    yield TicketService(repository)


async def get_priority_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AsyncGenerator[PriorityService, None]:
    repository = SQLPriorityRepository(session)
    yield PriorityService(repository)


async def get_auth_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AsyncGenerator[AuthService, None]:
    repository = SQLUserRepository(session)
    password_service = PasswordService()
    yield AuthService(repository, password_service)


async def require_admin(
    authorization: Annotated[str | None, Header()] = None,
    auth_service: Annotated[AuthService, Depends(get_auth_service)] = None,  # type: ignore[assignment]
) -> None:
    if not authorization:
        raise HTTPException(status_code=403, detail="Требуется заголовок авторизации")
    token = authorization.removeprefix("Bearer ")
    if not token:
        raise HTTPException(status_code=403, detail="Неверный заголовок авторизации")
    try:
        await auth_service.verify_admin(token)
    except (UnauthorizedError, JWTError):
        raise HTTPException(status_code=403, detail="Требуется доступ администратора")
