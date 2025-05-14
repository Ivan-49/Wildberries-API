import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from loguru import logger
import asyncio

@pytest.mark.asyncio
async def test_get_product_details():
    logger.info("Starting test_get_product_details")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/third-party/wildberries/get-product-details/235745003")
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}, body: {response.text}"
    logger.info("Finished test_get_product_details")

@pytest.mark.asyncio
async def test_create_user():
    payload = {
        "username": "IvanRemnev",
        "password": "331251314",
        "first_name":"Ivan",
        "last_name":"Remnev",
        "language":"ru",
        "is_bot":False,
        "premium_status":None,
        
        
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/register", json=payload)
        
        # Проверяем статус-код
        assert response.status_code == 201
        
        # Проверяем тело ответа
        data = response.json()
        assert data["username"] == "IvanRemnev"
        assert "user_id" in data