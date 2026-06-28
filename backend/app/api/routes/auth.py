import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.dependencies import get_auth_service
from app.api.schemas.auth import LoginRequest, TokenResponse
from app.core.domain.exceptions import AuthenticationError, UnauthorizedError
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    try:
        token = await auth_service.login(data.username, data.password)
        return TokenResponse(access_token=token)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/verify")
async def verify(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Требуется заголовок авторизации")
    token = authorization.removeprefix("Bearer ")
    if not token:
        raise HTTPException(status_code=401, detail="Неверный заголовок авторизации")
    try:
        await auth_service.verify_admin(token)
        return {"valid": True}
    except UnauthorizedError:
        raise HTTPException(status_code=401, detail="Неверный или истёкший токен")
