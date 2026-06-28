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
from app.infrastructure.database.engine import engine, async_session_factory
from app.infrastructure.database.seed import seed_priorities

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()

    if not settings.secret_key:
        logger.error("SECRET_KEY is not set!")
        logger.error("Set SECRET_KEY environment variable to a secure random value.")
        sys.exit(1)
    if not settings.admin_password or settings.admin_password in ("CHANGE_ME", "change-this-in-production"):
        logger.error("ADMIN_PASSWORD is empty or set to a trivial placeholder!")
        logger.error("Set ADMIN_PASSWORD environment variable to a strong password.")
        logger.error("Application will not start until a secure ADMIN_PASSWORD is configured.")
        sys.exit(1)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        await seed_priorities(session)
        await session.commit()

    logger.info("Starting ticket-system application")

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

app.include_router(tickets.ticket_router)
app.include_router(tickets.priority_router)
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
