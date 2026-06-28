from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.infrastructure.database.types import TZDateTime


class TestTZDateTime:
    def test_bind_converts_to_naive_utc(self):
        tz = TZDateTime()
        moscow = timezone(timedelta(hours=3))
        dt = datetime(2026, 6, 28, 16, 53, 0, tzinfo=moscow)

        result = tz.process_bind_param(dt, None)

        assert result.tzinfo is None
        assert result == datetime(2026, 6, 28, 13, 53, 0)

    def test_bind_rejects_naive_datetime(self):
        tz = TZDateTime()
        dt = datetime(2026, 6, 28, 13, 53, 0)

        with pytest.raises(TypeError, match="tzinfo is required"):
            tz.process_bind_param(dt, None)

    def test_bind_converts_utc_to_naive(self):
        tz = TZDateTime()
        dt = datetime(2026, 6, 28, 13, 53, 0, tzinfo=timezone.utc)

        result = tz.process_bind_param(dt, None)

        assert result.tzinfo is None
        assert result == datetime(2026, 6, 28, 13, 53, 0)

    def test_result_attaches_utc_timezone(self):
        tz = TZDateTime()
        naive = datetime(2026, 6, 28, 13, 53, 0)

        result = tz.process_result_value(naive, None)

        assert result.tzinfo == timezone.utc
        assert result == datetime(2026, 6, 28, 13, 53, 0, tzinfo=timezone.utc)

    def test_result_handles_none(self):
        tz = TZDateTime()
        assert tz.process_result_value(None, None) is None

    async def test_roundtrip_through_database(self, db_session: AsyncSession):
        moscow = timezone(timedelta(hours=3))
        original = datetime(2026, 6, 28, 16, 53, 0, tzinfo=moscow)

        await db_session.execute(
            text("CREATE TABLE IF NOT EXISTS tz_test (ts DATETIME)")
        )
        await db_session.execute(
            text("INSERT INTO tz_test (ts) VALUES (:ts)"),
            {"ts": original.astimezone(timezone.utc).replace(tzinfo=None)},
        )
        await db_session.commit()

        row = await db_session.execute(text("SELECT ts FROM tz_test"))
        naive_from_db = row.scalar()

        if isinstance(naive_from_db, str):
            naive_from_db = datetime.fromisoformat(naive_from_db)

        result = TZDateTime().process_result_value(naive_from_db, None)

        assert result.tzinfo == timezone.utc
        assert result.hour == 13
        assert result == datetime(2026, 6, 28, 13, 53, 0, tzinfo=timezone.utc)

        await db_session.execute(text("DROP TABLE tz_test"))
        await db_session.commit()

    async def test_ticket_timestamps_are_timezone_aware(self, async_client):
        from httpx import AsyncClient
        response = await async_client.post("/api/tickets", json={
            "title": "Timezone test",
            "priority_id": 2,
        })
        assert response.status_code == 201
        data = response.json()

        assert "T" in data["created_at"]
        assert "+" in data["created_at"] or data["created_at"].endswith("Z")

        created = datetime.fromisoformat(data["created_at"])
        assert created.tzinfo is not None

    async def test_ticket_list_timestamps_are_timezone_aware(self, async_client):
        from httpx import AsyncClient
        await async_client.post("/api/tickets", json={"title": "List test"})
        response = await async_client.get("/api/tickets")
        assert response.status_code == 200
        item = response.json()["items"][0]

        created = datetime.fromisoformat(item["created_at"])
        updated = datetime.fromisoformat(item["updated_at"])
        assert created.tzinfo is not None
        assert updated.tzinfo is not None
