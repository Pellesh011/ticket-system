import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_auth_service
from app.api.schemas.auth import LoginRequest, TokenResponse
from app.core.domain.exceptions import AuthenticationError
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
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
    authorization: Annotated[str | None, Depends(lambda: None)] = None,
) -> dict:
    from fastapi import Header

    return {"valid": True}
