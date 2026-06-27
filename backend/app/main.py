import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.api.routes import auth, tickets
from app.config import settings
from app.core.domain.exceptions import (
    AuthenticationError,
    TicketDomainError,
    UnauthorizedError,
)
from app.core.logging import setup_logging
from app.infrastructure.database.base import Base
from app.infrastructure.database.engine import engine

logger = logging.getLogger(__name__)


async def _seed_admin() -> None:
    if not settings.admin_password:
        logger.warning("ADMIN_PASSWORD is empty — skipping admin seeding")
        return
    from app.core.domain.entities import User
    from app.infrastructure.database.session import async_session_factory
    from app.infrastructure.repositories.sql_user_repository import SQLUserRepository
    from app.infrastructure.services.password_service import PasswordService

    async with async_session_factory() as session:
        repo = SQLUserRepository(session)
        password_service = PasswordService()
        admin = await repo.get_by_username(settings.admin_username)
        if not admin:
            admin_user = User(
                username=settings.admin_username,
                hashed_password=password_service.hash(settings.admin_password),
            )
            await repo.create(admin_user)
            await session.commit()
            logger.info("Admin user seeded: %s", settings.admin_username)
        else:
            logger.debug("Admin user already exists: %s", settings.admin_username)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()

    if not settings.secret_key or settings.secret_key in ("CHANGE_ME", "super-secret-key-change-in-production", "change-this-in-production"):
        logger.error("SECRET_KEY is empty or set to a trivial placeholder!")
        logger.error("Set SECRET_KEY environment variable to a secure random value (e.g. 'python -c \"import secrets; print(secrets.token_urlsafe(32))\"').")
        logger.error("Application will not start until a secure SECRET_KEY is configured.")
        sys.exit(1)
    if not settings.admin_password or settings.admin_password in ("CHANGE_ME", "change-this-in-production"):
        logger.error("ADMIN_PASSWORD is empty or set to a trivial placeholder!")
        logger.error("Set ADMIN_PASSWORD environment variable to a strong password.")
        logger.error("Application will not start until a secure ADMIN_PASSWORD is configured.")
        sys.exit(1)

    logger.info("Starting ticket-system application")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    await _seed_admin()

    yield
    await engine.dispose()
    logger.info("Application shutdown")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Ticket Management System",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)
app.include_router(auth.router)


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(_request: Request, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
    )


@app.exception_handler(UnauthorizedError)
async def unauthorized_error_handler(_request: Request, exc: UnauthorizedError) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc)},
    )


@app.exception_handler(TicketDomainError)
async def domain_error_handler(_request: Request, exc: TicketDomainError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
