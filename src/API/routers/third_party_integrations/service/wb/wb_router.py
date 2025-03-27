from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.product import ProductShema
from routers.third_party_integrations.service.wb.service.wildberries_api_client import (
    WildberriesAPIClient,
)

from routers.third_party_integrations.service.wb.service.product_repo import ProductRepository
from database import get_session
from logging import getLogger

logger = getLogger(__name__)

router = APIRouter()
wb_client = WildberriesAPIClient()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/auth/auth-by-username")
product_repository = ProductRepository()

@router.get("/get-product-details/{artikul}")
async def get_product_details(
    artikul: str,
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    product = await wb_client.fetch_product_details(artikul)
    await product_repository.add_product_to_subscribe(artikul, "wildberries", session)
    return product

@router.post("/add-product")
async def add_product_in_db(
    artikul: str,
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    product = await wb_client.fetch_product_details(artikul)
    product["marketplace"] = "wildberries"
    product = ProductShema(**product)
    try:
        await product_repository.add_product_to_subscribe(artikul, "wildberries", session)
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
    return await product_repository.add_product(product, session)

@router.get("/get-last-dataproduct-by-artikul/{artikul}")
async def get_last_dataproduct_by_artikul(
    artikul: str,
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    return await product_repository.get_last_product_by_artikul(artikul, session)

@router.get("/get-lasted-products-by-artikul/{artikul}")
async def get_lasted_products_by_artikul(
    artikul: str,
    count: int,
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    return await product_repository.get_latest_products_by_artikul(artikul, count, session)


@router.get("/get-all-products-paginated")
async def get_all_products_paginated(
    page: int,
    per_page: int,
    search_query: str | None = None,
    exclude_artikul: str | None = None,
    min_similarity: float = 0.3,
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    return await product_repository.get_products_paginated(
    page=page, per_page=per_page, session=session, search_query=search_query, min_similarity=min_similarity, exclude_artikul=exclude_artikul
)