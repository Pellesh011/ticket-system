from httpx import AsyncClient


class TestPriorityAPI:
    async def test_list_priorities(self, async_client: AsyncClient):
        response = await async_client.get("/api/priorities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = {p["name"] for p in data}
        assert names == {"low", "normal", "high"}

    async def test_create_priority_as_admin(self, auth_client: AsyncClient):
        response = await auth_client.post("/api/priorities", json={
            "name": "critical",
            "sort_order": 10,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "critical"
        assert data["sort_order"] == 10
        assert data["id"] is not None

    async def test_create_priority_without_auth_returns_403(self, async_client: AsyncClient):
        response = await async_client.post("/api/priorities", json={
            "name": "critical",
            "sort_order": 10,
        })
        assert response.status_code == 403

    async def test_update_priority_as_admin(self, auth_client: AsyncClient):
        response = await auth_client.patch("/api/priorities/1", json={
            "name": "very_low",
            "sort_order": 0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "very_low"
        assert data["sort_order"] == 0

    async def test_update_priority_without_auth_returns_403(self, async_client: AsyncClient):
        response = await async_client.patch("/api/priorities/1", json={
            "name": "very_low",
        })
        assert response.status_code == 403

    async def test_update_priority_not_found(self, auth_client: AsyncClient):
        response = await auth_client.patch("/api/priorities/999", json={
            "name": "nonexistent",
        })
        assert response.status_code == 404

    async def test_delete_priority_as_admin(self, auth_client: AsyncClient):
        response = await auth_client.delete("/api/priorities/3")
        assert response.status_code == 204

        list_resp = await auth_client.get("/api/priorities")
        assert len(list_resp.json()) == 2

    async def test_delete_priority_without_auth_returns_403(self, async_client: AsyncClient):
        response = await async_client.delete("/api/priorities/1")
        assert response.status_code == 403

    async def test_delete_priority_not_found(self, auth_client: AsyncClient):
        response = await auth_client.delete("/api/priorities/999")
        assert response.status_code == 404
