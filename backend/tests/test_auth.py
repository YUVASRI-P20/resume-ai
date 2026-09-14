"""Integration tests for the authentication module."""
import pytest

pytestmark = pytest.mark.asyncio

VALID_PASSWORD = "StrongPass123"


def _register_payload(email="student@example.com", role="STUDENT"):
    return {
        "email": email,
        "password": VALID_PASSWORD,
        "full_name": "Test Student",
        "role": role,
    }


class TestRegistration:
    async def test_register_success(self, client):
        resp = await client.post("/api/v1/auth/register", json=_register_payload())
        assert resp.status_code == 201
        body = resp.json()
        assert body["user"]["email"] == "student@example.com"
        assert body["user"]["role"] == "STUDENT"
        assert body["user"]["is_email_verified"] is False
        assert "access_token" in body["tokens"]
        assert "refresh_token" in body["tokens"]

    async def test_register_duplicate_email_fails(self, client):
        await client.post("/api/v1/auth/register", json=_register_payload())
        resp = await client.post("/api/v1/auth/register", json=_register_payload())
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "already_exists"

    async def test_register_weak_password_fails(self, client):
        payload = _register_payload()
        payload["password"] = "weak"
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 422

    async def test_register_recruiter_role(self, client):
        resp = await client.post(
            "/api/v1/auth/register", json=_register_payload(email="recruiter@example.com", role="RECRUITER")
        )
        assert resp.status_code == 201
        assert resp.json()["user"]["role"] == "RECRUITER"

    async def test_register_cannot_self_assign_admin(self, client):
        payload = _register_payload(email="wannabe-admin@example.com")
        payload["role"] = "ADMIN"
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 422


class TestLogin:
    async def test_login_success(self, client):
        await client.post("/api/v1/auth/register", json=_register_payload())
        resp = await client.post(
            "/api/v1/auth/login", json={"email": "student@example.com", "password": VALID_PASSWORD}
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()["tokens"]

    async def test_login_invalid_credentials(self, client):
        await client.post("/api/v1/auth/register", json=_register_payload())
        resp = await client.post(
            "/api/v1/auth/login", json={"email": "student@example.com", "password": "WrongPass123"}
        )
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "invalid_credentials"

    async def test_login_unknown_email(self, client):
        resp = await client.post(
            "/api/v1/auth/login", json={"email": "nobody@example.com", "password": VALID_PASSWORD}
        )
        assert resp.status_code == 401


class TestTokenRefresh:
    async def test_refresh_success_rotates_token(self, client):
        register_resp = await client.post("/api/v1/auth/register", json=_register_payload())
        old_refresh = register_resp.json()["tokens"]["refresh_token"]

        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
        assert resp.status_code == 200
        new_tokens = resp.json()
        assert new_tokens["refresh_token"] != old_refresh

    async def test_reused_refresh_token_is_rejected(self, client):
        register_resp = await client.post("/api/v1/auth/register", json=_register_payload())
        old_refresh = register_resp.json()["tokens"]["refresh_token"]

        first = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
        assert first.status_code == 200

        # Reusing the now-rotated-out token must fail.
        second = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
        assert second.status_code == 401

    async def test_refresh_with_garbage_token_fails(self, client):
        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-real-token"})
        assert resp.status_code == 401


class TestProtectedRoutes:
    async def test_me_requires_auth(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_me_with_valid_token(self, client):
        register_resp = await client.post("/api/v1/auth/register", json=_register_payload())
        access_token = register_resp.json()["tokens"]["access_token"]

        resp = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == "student@example.com"

    async def test_me_with_garbage_token_fails(self, client):
        resp = await client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
        )
        assert resp.status_code == 401


class TestRoleAuthorization:
    async def test_non_admin_cannot_access_admin_route(self, client):
        register_resp = await client.post("/api/v1/auth/register", json=_register_payload())
        access_token = register_resp.json()["tokens"]["access_token"]

        resp = await client.get(
            "/api/v1/users/admin/ping", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "authorization_error"


class TestLogout:
    async def test_logout_revokes_refresh_token(self, client):
        register_resp = await client.post("/api/v1/auth/register", json=_register_payload())
        refresh_token = register_resp.json()["tokens"]["refresh_token"]

        logout_resp = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
        assert logout_resp.status_code == 200

        # The revoked token can no longer be used to refresh.
        refresh_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_resp.status_code == 401


class TestPasswordReset:
    async def test_forgot_password_always_returns_200(self, client):
        # Same response whether or not the email exists (no enumeration).
        resp1 = await client.post("/api/v1/auth/forgot-password", json={"email": "student@example.com"})
        resp2 = await client.post("/api/v1/auth/forgot-password", json={"email": "nobody@example.com"})
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json()["message"] == resp2.json()["message"]

    async def test_reset_password_with_invalid_token_fails(self, client):
        resp = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": "invalid-token", "new_password": "NewStrongPass123"},
        )
        assert resp.status_code == 401

    async def test_full_reset_flow(self, client, db_session):
        from app.security.jwt import create_password_reset_token
        from app.repositories.user_repository import UserRepository

        await client.post("/api/v1/auth/register", json=_register_payload())
        users = UserRepository(db_session)
        user = await users.get_by_email("student@example.com")
        token = create_password_reset_token(user.id)

        resp = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "NewStrongPass123"},
        )
        assert resp.status_code == 200

        # Old password no longer works; new one does.
        old_login = await client.post(
            "/api/v1/auth/login", json={"email": "student@example.com", "password": VALID_PASSWORD}
        )
        assert old_login.status_code == 401

        new_login = await client.post(
            "/api/v1/auth/login", json={"email": "student@example.com", "password": "NewStrongPass123"}
        )
        assert new_login.status_code == 200


class TestEmailVerification:
    async def test_verify_email_with_invalid_token_fails(self, client):
        resp = await client.post("/api/v1/auth/verify-email", json={"token": "invalid-token"})
        assert resp.status_code == 401

    async def test_verify_email_success(self, client, db_session):
        from app.security.jwt import create_email_verification_token
        from app.repositories.user_repository import UserRepository

        await client.post("/api/v1/auth/register", json=_register_payload())
        users = UserRepository(db_session)
        user = await users.get_by_email("student@example.com")
        token = create_email_verification_token(user.id)

        resp = await client.post("/api/v1/auth/verify-email", json={"token": token})
        assert resp.status_code == 200

        me_resp = await client.post(
            "/api/v1/auth/login", json={"email": "student@example.com", "password": VALID_PASSWORD}
        )
        access_token = me_resp.json()["tokens"]["access_token"]
        profile = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert profile.json()["is_email_verified"] is True
