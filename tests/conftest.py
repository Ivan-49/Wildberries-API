import asyncio
import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from database.main import engine, Base
from main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def auth_user(async_client):
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpassword"
    payload = {
        "username": username,
        "password": password,
        "first_name": "Test",
        "last_name": "User",
        "language": "ru",
        "is_bot": False,
        "premium_status": None,
    }

    reg_response = await async_client.post("/api/v1/auth/register", json=payload)
    assert reg_response.status_code in (
        200,
        201,
    ), f"Registration failed: {reg_response.text}"
    reg_data = reg_response.json()

    login_response = await async_client.post(
        "/api/v1/auth/auth-by-username",
        data={"username": username, "password": password},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    login_data = login_response.json()
    assert (
        "access_token" in login_data
    ), f"No access_token in login response: {login_response.text}"

    return {
        "headers": {"Authorization": f"Bearer {login_data['access_token']}"},
        "user_id": reg_data["user_id"],
        "username": username,
        "password": password,
    }
