import asyncio
import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def seed_admin() -> None:
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
                hashed_password=await password_service.hash(settings.admin_password),
            )
            await repo.create(admin_user)
            await session.commit()
            logger.info("Admin user seeded: %s", settings.admin_username)
        else:
            logger.debug("Admin user already exists: %s", settings.admin_username)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_admin())
