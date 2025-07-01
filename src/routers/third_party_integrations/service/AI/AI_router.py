from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from loguru import logger

from routers.third_party_integrations.service.AI.service.chat_gpt_api_client import (
    GigaChatClient,
)
from routers.third_party_integrations.service.wb.service.product_repo import (
    ProductRepository,
)
from database import get_session
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/auth-by-username",
    scopes={
        "logout": "Log out of the application",
    },
)


# Инициализация клиентов
product_repository = ProductRepository()
giga_chat_client = GigaChatClient(os.getenv("GIGACHAT_API_KEY"))


@router.get("/analyze-current-product/{artikul}")
async def analyze_current_product(
    artikul: str,
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    """
    Анализирует текущее состояние товара
    """
    try:
        # Получаем текущий товар
        product = await product_repository.get_product_by_artikul(artikul, session)
        if product:
            product_data = await product_repository.get_last_product_history_by_artikul(
                artikul, session
            )

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if not product_data:
            raise HTTPException(
                status_code=404,
                detail="Product history not found, please wait until we add it.",
            )
        # Преобразуем модель в словарь
        product_dict = {
            "artikul": product.artikul,
            "standart_price": product_data.standart_price,
            "marketplace": product.marketplace,
            "total_quantity": product_data.total_quantity,
            "created_at": product_data.created_at.isoformat(),
            "name": product.name,
            "id": product.id,
            "sell_price": product_data.sell_price,
            "standart_price": product_data.standart_price,
            "rating": product_data.rating,
        }

        # Получаем анализ от ИИ
        analysis = await giga_chat_client.analyze_product(product_dict)
        return {"analysis": analysis}

    except Exception as e:
        logger.error(f"Error analyze current product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze-product-history/{artikul}")
async def analyze_product_history(
    artikul: str,
    count: int = 100,  # Количество последних записей для анализа
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    """
    Анализирует историю изменений товара
    """
    try:
        # Получаем историю товара
        if count > 100:
            raise HTTPException(
                status_code=400,
                detail="Превышено максимальное количество записей для анализа",
            )
        product = await product_repository.get_product_by_artikul(artikul, session)

        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")

        product_history = await product_repository.get_lasted_products_by_artikul(
            artikul, count, session
        )

        # Преобразуем модели в словари
        product = {
            "artikul": product.artikul,
            "name": product.name,
            "marketplace": product.marketplace,
        }
        product_data_history = [
            {
                "created_at": data.created_at.isoformat(),
                "total_quantity": data.total_quantity,
                "sell_price": data.sell_price,
                "standart_price": data.standart_price,
                "rating": data.rating,
            }
            for data in product_history
        ]

        # Получаем анализ от ИИ
        analysis = await giga_chat_client.analyze_products_batch(
            product=product, product_history=product_data_history
        )
        return {"analysis": analysis}

    except Exception as e:
        logger.error(f"Error analyze product history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-price-dynamics/{artikul}")
async def get_price_dynamics(
    artikul: str,
    count: int = 100,  # Количество последних записей для анализа
    user_id: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    """
    Получает динамику цен и других параметров товара
    """
    try:
        # Получаем историю товара
        products = await product_repository.get_lasted_products_by_artikul(
            artikul, count, session
        )
        if not products:
            raise HTTPException(status_code=404, detail="Товар не найден")
        product_data = await product_repository.get_product_by_artikul(
            artikul=artikul, session=session
        )
        if not product_data:
            raise HTTPException(status_code=404, detail="Товар не найден")
        # Преобразуем модели в словари
        products_dict = [
            {
                "artikul": product_data.artikul,
                "standart_price": product.standart_price,
                "marketplace": product_data.marketplace,
                "total_quantity": product.total_quantity,
                "created_at": product.created_at.isoformat(),
                "name": product_data.name,
                "id": product.id,
                "sell_price": product.sell_price,
                "rating": product.rating,
            }
            for product in products
        ]

        # Получаем динамику
        dynamics = await giga_chat_client._calculate_price_dynamics(products_dict)
        return dynamics

    except Exception as e:
        logger.exception(f"Error get price dynamics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
