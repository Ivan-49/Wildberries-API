import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from loguru import logger
from main import app


@pytest.fixture(scope="session")
async def create_user_with_token():
    payload = {
        "username": "IvanRemnev",
        "password": "331251314",
        "first_name": "Ivan",
        "last_name": "Remnev",
        "language": "ru",
        "is_bot": False,
        "premium_status": None,
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Регистрируем пользователя
        response = await ac.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == payload["username"]
        assert "user_id" in data

        # Логинимся, чтобы получить JWT токен
        login_payload_by_username = {
            "username": payload["username"],
            "password": payload["password"],
        }
        login_payload_by_user_id = {
            "user_id": data["user_id"],
            "password": payload["password"],
        }

        login_response_by_username = await ac.post(
            "/api/v1/auth/auth-by-username", data=login_payload_by_username
        )
        login_response_by_user_id = await ac.post(
            "/api/v1/auth/auth-by-user-id", params=login_payload_by_user_id
        )

        assert login_response_by_user_id.status_code == 200
        assert login_response_by_username.status_code == 200

        login_data_by_user_id = login_response_by_user_id.json()
        login_data_by_username = login_response_by_username.json()
        assert "access_token" in login_data_by_user_id
        assert "access_token" in login_data_by_username

        # Возвращаем токен и, при необходимости, другие данные
        return {
            "token": login_data_by_username["access_token"],
            "user_id": data["user_id"],
            "username": data["username"],
            "headers_jwt": {
                "Authorization": f"Bearer {login_data_by_username['access_token']}"
            },
        }


@pytest.mark.asyncio
async def test_get_user_info(create_user_with_token):

    headers = create_user_with_token["headers_jwt"]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("api/v1/auth/user-info", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "IvanRemnev"
        assert data["first_name"] == "Ivan"
        assert data["last_name"] == "Remnev"
        assert data["language"] == "ru"
        assert data["is_bot"] == False
        assert data["premium_status"] == None


@pytest.mark.asyncio
async def test_change_password(create_user_with_token):
    token = create_user_with_token["token"]
    old_password = "331251314"
    new_password = "3312513141"
    for _ in range(2):
        if _ == 1:
            old_password, new_password = new_password, old_password
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {
                "old_password": old_password,
                "new_password": new_password,
            }
            response = await ac.post(
                "/api/v1/auth/change-password",
                params=payload,
                headers=create_user_with_token["headers_jwt"],
            )
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Password changed successfully"


@pytest.mark.asyncio
async def test_logout_user(create_user_with_token):
    headers = create_user_with_token["headers_jwt"]
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", headers=headers
    ) as ac:
        response = await ac.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert (
            response.json()["message"]
            == f"User {create_user_with_token['username']} logged out successfully"
        )
