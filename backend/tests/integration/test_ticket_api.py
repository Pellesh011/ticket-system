import pytest
from httpx import AsyncClient


class TestTicketAPI:
    async def test_health(self, async_client: AsyncClient):
        response = await async_client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    async def test_create_ticket(self, async_client: AsyncClient):
        response = await async_client.post("/api/tickets", json={
            "title": "Test ticket",
            "priority": "high",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test ticket"
        assert data["priority"] == "high"
        assert data["status"] == "new"
        assert data["id"] is not None

    async def test_create_ticket_validation_title_too_short(self, async_client: AsyncClient):
        response = await async_client.post("/api/tickets", json={
            "title": "ab",
        })
        assert response.status_code == 422

    async def test_create_ticket_validation_title_too_long(self, async_client: AsyncClient):
        response = await async_client.post("/api/tickets", json={
            "title": "x" * 121,
        })
        assert response.status_code == 422

    async def test_list_tickets_empty(self, async_client: AsyncClient):
        response = await async_client.get("/api/tickets")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_tickets_with_data(self, async_client: AsyncClient):
        await async_client.post("/api/tickets", json={"title": "Ticket 1"})
        await async_client.post("/api/tickets", json={"title": "Ticket 2"})
        response = await async_client.get("/api/tickets")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_filter_by_status(self, async_client: AsyncClient):
        await async_client.post("/api/tickets", json={"title": "Active"})
        resp = await async_client.post("/api/tickets", json={"title": "Done ticket"})
        ticket_id = resp.json()["id"]
        await async_client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "done"})
        response = await async_client.get("/api/tickets", params={"status": "done"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "done"

    async def test_filter_by_priority(self, async_client: AsyncClient):
        await async_client.post("/api/tickets", json={"title": "Normal"})
        await async_client.post("/api/tickets", json={"title": "High", "priority": "high"})
        response = await async_client.get("/api/tickets", params={"priority": "high"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["priority"] == "high"

    async def test_search_by_title(self, async_client: AsyncClient):
        await async_client.post("/api/tickets", json={"title": "Fix login bug"})
        await async_client.post("/api/tickets", json={"title": "Add new feature"})
        response = await async_client.get("/api/tickets", params={"search": "login"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "login" in data["items"][0]["title"]

    async def test_search_by_description(self, async_client: AsyncClient):
        await async_client.post("/api/tickets", json={
            "title": "Ticket A",
            "description": "Important bugfix needed",
        })
        response = await async_client.get("/api/tickets", params={"search": "bugfix"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    async def test_get_ticket_by_id(self, async_client: AsyncClient):
        resp = await async_client.post("/api/tickets", json={"title": "Get me"})
        ticket_id = resp.json()["id"]
        response = await async_client.get(f"/api/tickets/{ticket_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Get me"

    async def test_get_ticket_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/tickets/999")
        assert response.status_code == 404

    async def test_update_ticket(self, async_client: AsyncClient):
        resp = await async_client.post("/api/tickets", json={"title": "Original"})
        ticket_id = resp.json()["id"]
        response = await async_client.patch(f"/api/tickets/{ticket_id}", json={
            "title": "Updated",
            "priority": "high",
        })
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
        assert response.json()["priority"] == "high"

    async def test_update_done_ticket_returns_400(self, async_client: AsyncClient):
        resp = await async_client.post("/api/tickets", json={"title": "Test"})
        ticket_id = resp.json()["id"]
        await async_client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "done"})
        response = await async_client.patch(f"/api/tickets/{ticket_id}", json={"title": "New"})
        assert response.status_code == 400
        assert "done" in response.json()["detail"].lower()

    async def test_update_status_done(self, async_client: AsyncClient):
        resp = await async_client.post("/api/tickets", json={"title": "Finish me"})
        ticket_id = resp.json()["id"]
        response = await async_client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "done"})
        assert response.status_code == 200
        assert response.json()["status"] == "done"

    async def test_cannot_change_status_from_done(self, async_client: AsyncClient):
        resp = await async_client.post("/api/tickets", json={"title": "Done ticket"})
        ticket_id = resp.json()["id"]
        await async_client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "done"})
        response = await async_client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "new"})
        assert response.status_code == 400
        assert "done" in response.json()["detail"].lower()

    async def test_delete_ticket_as_admin(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/tickets", json={"title": "Delete me"})
        ticket_id = resp.json()["id"]
        response = await auth_client.delete(f"/api/tickets/{ticket_id}")
        assert response.status_code == 204

    async def test_delete_ticket_without_auth_returns_403(self, async_client: AsyncClient):
        resp = await async_client.post("/api/tickets", json={"title": "Test"})
        ticket_id = resp.json()["id"]
        response = await async_client.delete(f"/api/tickets/{ticket_id}")
        assert response.status_code == 403

    async def test_delete_done_ticket_returns_400(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/tickets", json={"title": "Done"})
        ticket_id = resp.json()["id"]
        await auth_client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "done"})
        response = await auth_client.delete(f"/api/tickets/{ticket_id}")
        assert response.status_code == 400

    async def test_pagination(self, async_client: AsyncClient):
        for i in range(25):
            await async_client.post("/api/tickets", json={"title": f"Ticket {i}"})
        response = await async_client.get("/api/tickets", params={"page": 1, "page_size": 10})
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["total_pages"] == 3

    async def test_login_success(self, async_client: AsyncClient):
        response = await async_client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin",
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_login_failure(self, async_client: AsyncClient):
        response = await async_client.post("/api/auth/login", json={
            "username": "admin",
            "password": "wrong",
        })
        assert response.status_code == 401
