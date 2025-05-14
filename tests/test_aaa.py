import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from loguru import logger


@pytest.mark.asyncio
async def test_get_product_details():
    logger.info("Starting test_get_product_details")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/api/v1/third-party/wildberries/get-product-details/235745003"
        )
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        assert (
            response.status_code == 200
        ), f"Unexpected status code: {response.status_code}, body: {response.text}"
    logger.info("Finished test_get_product_details")
