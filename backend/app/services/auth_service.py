import logging
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings
from app.core.domain.exceptions import AuthenticationError, UnauthorizedError
from app.core.repositories.user_repository import IUserRepository
from app.core.services.password_service import IPasswordService

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repository: IUserRepository, password_service: IPasswordService) -> None:
        self._repo = user_repository
        self._password_service = password_service

    async def login(self, username: str, password: str) -> str:
        user = await self._repo.get_by_username(username)
        if not user or not self._password_service.verify(password, user.hashed_password):
            raise AuthenticationError()
        token = self._create_token(username)
        logger.info("User logged in: %s", username)
        return token

    def _create_token(self, username: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.token_expire_hours)
        payload = {"sub": username, "exp": expire}
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    async def verify_admin(self, token: str) -> bool:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: str | None = payload.get("sub")
            if not username or username != settings.admin_username:
                raise UnauthorizedError()
            return True
        except JWTError:
            raise UnauthorizedError()
