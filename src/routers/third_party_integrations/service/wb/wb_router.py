from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from schemas.product import ProductShema, ProductHistoryShema, ProductRequest
from routers.third_party_integrations.service.wb.service.wildberries_api_client import (
    WildberriesAPIClient,
)

from routers.third_party_integrations.service.wb.service.product_repo import (
    ProductRepository,
)
from database import get_session
from loguru import logger

router = APIRouter()
wb_client = WildberriesAPIClient()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/auth-by-username",
    scopes={
        "logout": "Log out of the application",
    },
)

product_repository = ProductRepository()


@router.get("/get-product-details/{artikul}")
async def get_product_details(
    artikul: str,
    # user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):

    product = await wb_client.fetch_product_details(artikul)
    result = product.copy()
    product["marketplace"] = "wildberries"
    product = ProductShema(**product)
    if not (await product_repository.get_product_by_artikul(artikul, session=session)):
        await product_repository.add_product(product, session=session)

    logger.info(f"Product {artikul} added to subscribe")
    return result

@router.post("/add-product")
async def add_product_in_db(
    request: ProductRequest,
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    try:
        artikul = request.artikul
        
        # 1. Получаем данные товара
        product = await wb_client.fetch_product_details(artikul)
        if not product:
            return JSONResponse(
                content={"error": f"Товар {artikul} не найден на Wildberries"},
                status_code=404
            )
        
        # 2. Добавляем маркетплейс и валидируем
        product["marketplace"] = "wildberries"
        
        try:
            product_model = ProductShema(**product)
            product_history = ProductHistoryShema(**product)
        except ValidationError as e:
            logger.error(f"Ошибка валидации: {str(e)}")
            return JSONResponse(
                content={"error": "Некорректные данные от Wildberries API"},
                status_code=422
            )

        # 3. Работа с БД
        try:
            # Проверяем существование товара
            existing_product = await product_repository.get_product_by_artikul(
                artikul=artikul, 
                session=session  # Явно передаем сессию
            )
            
            if not existing_product:
                await product_repository.add_product(
                    product=product_model, 
                    session=session  # Явно передаем сессию
                )
            
            # Получаем продукт с ID из БД
            product_db = await product_repository.get_product_by_artikul(
                artikul=artikul, 
                session=session  # Явно передаем сессию
            )
            
            if not product_db:
                raise ValueError("Товар не найден после добавления")
            
            # Добавляем историю (с явным указанием аргументов)
            await product_repository.add_product_history(
                artikul=artikul,
                product_history=product_history,  # Модель истории
                session=session  # Явно передаем сессию
            )
            
            await session.commit()
            
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Конфликт данных: {str(e)}")
            return JSONResponse(
                content={"error": "Ошибка дублирования данных"},
                status_code=409
            )
        except ValueError as e:
            await session.rollback()
            return JSONResponse(
                content={"error": str(e)},
                status_code=400
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка БД: {str(e)}")
            return JSONResponse(
                content={"error": "Ошибка базы данных"},
                status_code=500
            )
            
        return product_model
        
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}")
        return JSONResponse(
            content={"error": "Внутренняя ошибка сервера"},
            status_code=500
        )

@router.get("/get-last-dataproduct-by-artikul/{artikul}")
async def get_last_dataproduct_by_artikul(
    artikul: str,
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    try:
        result = await product_repository.get_last_product_history_by_artikul(artikul, session)
        result = ProductHistoryShema(
            standart_price=result.standart_price,
            sell_price=result.sell_price,
            total_quantity=result.total_quantity,
            rating=result.rating,
            )
        return result
    except Exception as e:
        logger.error(f"Error get last product by artikul: {str(e)}")


@router.get("/get-lasted-products-by-artikul/{artikul}")
async def get_lasted_products_by_artikul(
    artikul: str,
    count: int = 100,
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    try:
        if count > 100:
            raise HTTPException(
                status_code=400,
                detail="Превышено максимальное количество записей для анализа",
            )
        return await product_repository.get_lasted_products_by_artikul(
            artikul, count, session
        )
    except Exception as e:
        logger.error(f"Error get latest products by artikul: {str(e)}")
        raise e

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
    try:
        return await product_repository.get_products_paginated(
            session=session,
            page=page,
            per_page=per_page,
            search_query=search_query,
            min_similarity=min_similarity,
            exclude_artikul=exclude_artikul,
        )
    except Exception as e:
        logger.error(f"Error get all products paginated: {str(e)}")
        raise HTTPException(500, 'Internal server error')