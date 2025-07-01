"""
Планировщик задач для сбора данных о товарах.
Включает обработку ошибок и повторные попытки.
"""

from routers.third_party_integrations.service.wb.service.product_repo import (
    ProductRepository,
)
from schemas.product import ProductShema, ProductHistoryShema
from database.main import async_session
from routers.third_party_integrations.service.wb.service.wildberries_api_client import (
    WildberriesAPIClient,
)

from loguru import logger
import asyncio
from typing import List

product_repository = ProductRepository()

wb_client = WildberriesAPIClient()


async def process_product(sub) -> bool:
    """
    Обрабатывает один товар.

    Args:
        sub: Объект подписки

    Returns:
        bool: True если обработка успешна, False в противном случае
    """
    async with async_session() as session:
        try:
            product = await wb_client.fetch_product_details(sub.artikul)
            if product:
                product["marketplace"] = sub.marketplace
                product = ProductHistoryShema(**product)
                await product_repository.add_product_history(
                    sub.artikul, product, session
                )
                await session.commit()
                return True
            else:
                logger.warning(f"Не удалось получить данные для артикула {sub.artikul}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при обработке артикула {sub.artikul}: {str(e)}")
            await session.rollback()
            return False


async def process_batch(subs: List, batch_size: int = 5):
    """
    Обрабатывает пакет товаров параллельно.

    Args:
        subs: Список товаров для обработки
        batch_size: Размер пакета для параллельной обработки
    """
    for i in range(0, len(subs), batch_size):
        batch = subs[i : i + batch_size]
        tasks = [process_product(sub) for sub in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        yield results


async def add_product_in_db():
    """
    Основная функция сбора данных о товарах.
    Обрабатывает ошибки и ведет статистику.
    """
    async with async_session() as session:
        try:
            subs = await product_repository.get_all_products_from_marketplace(
                "wildberries", session
            )
            total_count = len(subs)
            processed_count = 0
            failed_count = 0

            logger.info(f"Начинаем обработку {total_count} товаров")

            # Обрабатываем товары пакетами
            async for results in process_batch(subs):
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Ошибка при обработке товара: {str(result)}")
                        failed_count += 1
                    elif result:
                        processed_count += 1
                    else:
                        failed_count += 1

                    # Логируем прогресс каждые 10 товаров
                    if (processed_count + failed_count) % 10 == 0:
                        logger.info(
                            f"Прогресс: {processed_count + failed_count}/{total_count} "
                            f"(успешно: {processed_count}, ошибок: {failed_count})"
                        )

            logger.info(
                f"Обработка завершена. Всего: {total_count}, "
                f"Успешно: {processed_count}, Ошибок: {failed_count}"
            )

        except Exception as e:
            logger.error(f"Критическая ошибка при сборе данных: {str(e)}")
            await session.rollback()
