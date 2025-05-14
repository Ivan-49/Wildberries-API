import pytest
from loguru import logger


@pytest.mark.asyncio
async def test_get_product_details(async_client, auth_user):
    logger.info("Starting test_get_product_details")
    response = await async_client.get(
        "/api/v1/third-party/wildberries/get-product-details/235745003",
        headers=auth_user["headers"],
    )
    logger.info(f"Status code: {response.status_code}")
    logger.info(f"Response body: {response.text}")
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}, body: {response.text}"
    logger.info("Finished test_get_product_details")
