import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import PriorityModel

logger = logging.getLogger(__name__)

SEED_PRIORITIES = [
    {"name": "low", "sort_order": 0},
    {"name": "normal", "sort_order": 1},
    {"name": "high", "sort_order": 2},
]


async def seed_priorities(session: AsyncSession) -> None:
    result = await session.execute(select(PriorityModel).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    for data in SEED_PRIORITIES:
        model = PriorityModel(name=data["name"], sort_order=data["sort_order"])
        session.add(model)

    await session.flush()
    logger.info("Seeded %d priorities", len(SEED_PRIORITIES))
