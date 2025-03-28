import aiohttp
from typing import Dict, Any, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class WildberriesAPIClient:
    """
    Клиент для работы с API Wildberries.
    Обрабатывает запросы к API с повторными попытками и таймаутами.
    """
    def __init__(self):
        self.base_url = "https://card.wb.ru/cards/v1/detail"
        self.app_type = 1
        self.currency = "rub"
        self.destination = "-1257786"
        self.sp = 30
        self.max_retries = 3  # Максимальное количество попыток
        self.retry_delay = 2  # Задержка между попытками в секундах
        self.timeout = 30  # Таймаут запроса в секундах

    async def fetch_product_details(self, artikul: str) -> Optional[Dict[str, Any]]:
        """
        Получает детали товара с повторными попытками при ошибках.
        
        Args:
            artikul (str): Артикул товара
            
        Returns:
            Optional[Dict[str, Any]]: Данные о товаре или None при ошибке
        """
        url = f"{self.base_url}?appType={self.app_type}&curr={self.currency}&dest={self.destination}&sp={self.sp}&nm={artikul}"
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Запрос данных для артикула: {artikul} (попытка {attempt + 1}/{self.max_retries})")
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            products = data.get("data", {}).get("products", [])
                            if products:
                                product = products[0]
                                artikul = product.get("id")
                                name = product.get("name")
                                price_u = product.get("priceU")
                                sale_price_u = product.get("salePriceU")
                                rating = product.get("reviewRating", 0.0)

                                if price_u is None or sale_price_u is None:
                                    logger.debug(
                                        f"Missing price data for artikul {artikul}. "
                                        f"priceU: {price_u}, salePriceU: {sale_price_u}"
                                    )
                                
                                standart_price = (price_u / 100) if price_u is not None else 0.0
                                sell_price = (sale_price_u / 100) if sale_price_u is not None else 0.0

                                sizes = product.get("sizes", [])
                                total_quantity = 0
                                for size in sizes:
                                    total_quantity += sum(
                                        item.get("qty", 0)
                                        for item in size.get("stocks", [])
                                    )

                                return {
                                    "artikul": str(artikul),
                                    "name": str(name),
                                    "standart_price": float(standart_price),
                                    "sell_price": float(sell_price),
                                    "total_quantity": int(total_quantity),
                                    "rating": float(rating),
                                }
                        else:
                            logger.error(
                                f"Failed to fetch product details for artikul: {artikul}. "
                                f"Status code: {response.status}"
                            )
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(self.retry_delay)
                                continue
                            return None

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"Error fetching product {artikul} (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                return None
            except Exception as e:
                logger.exception(f"Unexpected error for product {artikul}: {str(e)}")
                return None
                
        return None


if __name__ == "__main__":
    client = WildberriesAPIClient()
    response = asyncio.run(client.fetch_product_details("177241487"))
    print(response)
    