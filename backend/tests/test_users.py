"""Integration tests for the user profile endpoints."""
import pytest

pytestmark = pytest.mark.asyncio

VALID_PASSWORD = "StrongPass123"


async def _register_and_login(client, email="user@example.com"):
    payload = {
        "email": email,
        "password": VALID_PASSWORD,
        "full_name": "Original Name",
        "role": "STUDENT",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    return resp.json()["tokens"]["access_token"]


class TestUserProfile:
    async def test_get_my_profile(self, client):
        token = await _register_and_login(client)
        resp = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Original Name"

    async def test_update_my_profile(self, client):
        token = await _register_and_login(client)
        resp = await client.patch(
            "/api/v1/users/me",
            json={"full_name": "Updated Name"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Name"

    async def test_update_profile_requires_auth(self, client):
        resp = await client.patch("/api/v1/users/me", json={"full_name": "Nope"})
        assert resp.status_code == 401


class TestHealthCheck:
    async def test_health_check(self, client):
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
