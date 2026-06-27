import logging
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings
from app.core.domain.entities import User
from app.core.domain.exceptions import AuthenticationError, UnauthorizedError
from app.core.repositories.user_repository import IUserRepository
from app.core.services.password_service import IPasswordService

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repository: IUserRepository, password_service: IPasswordService) -> None:
        self._repo = user_repository
        self._password_service = password_service

    async def _ensure_admin_exists(self) -> None:
        admin = await self._repo.get_by_username(settings.admin_username)
        if not admin:
            admin_user = User(
                username=settings.admin_username,
                hashed_password=self._password_service.hash(settings.admin_password),
            )
            await self._repo.create(admin_user)
            logger.info("Admin user created: %s", settings.admin_username)

    async def login(self, username: str, password: str) -> str:
        await self._ensure_admin_exists()
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
