import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from loguru import logger
from main import app

@pytest.fixture(scope='function')
@pytest.mark.asyncio
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

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Регистрируем пользователя
        response = await ac.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == payload["username"]
        assert "user_id" in data

        # Логинимся, чтобы получить JWT токен
        login_payload = {
            "username": payload["username"],
            "password": payload["password"]
        }
        login_response = await ac.post("/api/v1/auth/auth-by-username", data=login_payload)
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data

        # Возвращаем токен и, при необходимости, другие данные
        return {
            "token": login_data["access_token"],
            "user_id": data["user_id"],
            "username": data["username"]
        }

@pytest.mark.asyncio
async def test_get_user_info(create_user_with_token):
    token = create_user_with_token['token']

    headers = {
         "Authorization": f"Bearer {token}"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get('api/v1G/auth/user-info', headers = headers)
        assert response.status_code == 200
        data = response.json()
        assert data['username'] == "IvanRemnev"
        assert data['first_name'] == "Ivan"
        assert data['last_name'] == "Remnev"
        assert data['language'] == "ru"
        assert data['is_bot'] == False
        assert data['premium_status'] == None