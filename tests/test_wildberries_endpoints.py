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

@pytest.mark.asyncio
async def test_add_product(async_client,auth_user):
    logger.info("Starting test_add_product")
    post_data = {
        "artikul":"235745003"
    }
    response = await async_client.post(
        "/api/v1/third-party/wildberries/add-product",
        headers = auth_user["headers"],
        json = post_data
        )
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}, body: {response.text}"
    logger.info("Finished test_add_product")

@pytest.mark.asyncio
async def test_get_last_dataproduct_by_artikul(async_client,auth_user):
    logger.info('Starting test_get_last_dataproduct_by_artikul')
    response = await async_client.get(
        "/api/v1/third-party/wildberries/get-last-dataproduct-by-artikul/235745003",
        headers = auth_user['headers'],
    )
    assert (
        response.status_code == 200
        ), f"Unexpected status code: {response.status_code}, body: {response.text}"
    logger.info("Finished test_get_last_dataproduct_by_artikul")


@pytest.mark.asyncio
async def test_get_lasted_products_by_artikul(async_client, auth_user):
    logger.info('Starting test_get_lasted_products_by_artikul')
    response = await async_client.get(
        "/api/v1/third-party/wildberries/get-lasted-products-by-artikul/235745003?100",
        headers = auth_user['headers'],
    )
    assert (
        response.status_code == 200
        ),f"Unexpected status code: {response.status_code}, body: {response.text}"
    json_response = response.json()
    assert json_response['count'] == len(json_response['result'])
    logger.info("Finished test_get_last_dataproduct_by_artikul")
