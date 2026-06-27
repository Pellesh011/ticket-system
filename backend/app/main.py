import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()

    if not settings.secret_key:
        logger.warning("SECRET_KEY is empty! JWT tokens are insecure.")
        logger.warning("Set SECRET_KEY environment variable to a secure random value.")
    if not settings.admin_password:
        logger.warning("ADMIN_PASSWORD is empty! Admin login is blocked.")
        logger.warning("Set ADMIN_PASSWORD environment variable.")

    logger.info("Starting ticket-system application")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")
    yield
    await engine.dispose()
    logger.info("Application shutdown")


app = FastAPI(
    title="Ticket Management System",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

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
