from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

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
        # Получаем последнее состояние товара
        product = await product_repository.get_last_product_by_artikul(artikul, session)
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")

        # Преобразуем модель в словарь
        product_dict = {
            "artikul": product.artikul,
            "standart_price": product.standart_price,
            "marketplace": product.marketplace,
            "total_quantity": product.total_quantity,
            "created_at": product.created_at.isoformat(),
            "name": product.name,
            "id": product.id,
            "sell_price": product.sell_price,
            "rating": product.rating,
        }

        # Получаем анализ от ИИ
        analysis = await giga_chat_client.analyze_product(product_dict)
        return {"analysis": analysis}

    except Exception as e:
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
        products = await product_repository.get_latest_products_by_artikul(
            artikul, count, session
        )
        if not products:
            raise HTTPException(status_code=404, detail="Товар не найден")

        # Преобразуем модели в словари
        products_dict = [
            {
                "artikul": product.artikul,
                "standart_price": product.standart_price,
                "marketplace": product.marketplace,
                "total_quantity": product.total_quantity,
                "created_at": product.created_at.isoformat(),
                "name": product.name,
                "id": product.id,
                "sell_price": product.sell_price,
                "rating": product.rating,
            }
            for product in products
        ]

        # Получаем анализ от ИИ
        analysis = await giga_chat_client.analyze_products_batch(products_dict)
        return {"analysis": analysis}

    except Exception as e:
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
        products = await product_repository.get_latest_products_by_artikul(
            artikul, count, session
        )
        if not products:
            raise HTTPException(status_code=404, detail="Товар не найден")

        # Преобразуем модели в словари
        products_dict = [
            {
                "artikul": product.artikul,
                "standart_price": product.standart_price,
                "marketplace": product.marketplace,
                "total_quantity": product.total_quantity,
                "created_at": product.created_at.isoformat(),
                "name": product.name,
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
        raise HTTPException(status_code=500, detail=str(e))
