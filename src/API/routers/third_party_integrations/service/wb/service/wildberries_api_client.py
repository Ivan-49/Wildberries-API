import aiohttp
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class WildberriesAPIClient:
    def __init__(self):
        self.base_url = "https://card.wb.ru/cards/v1/detail"
        self.app_type = 1
        self.currency = "rub"
        self.destination = "-1257786"
        self.sp = 30

    async def fetch_product_details(self, artikul: str) -> Optional[Dict[str, Any]]:
        """
        возвращает словарь вида:{
                "artikul": str,
                "name": str,
                "standart_price": float,
                "sell_price": float,
                "total_quantity": int
                "rating": float(rating),
            }
        """
        url = f"{self.base_url}?appType={self.app_type}&curr={self.currency}&dest={self.destination}&sp={self.sp}&nm={artikul}"
        print(url)
        try:
            logger.info(f"Fetching product details for artikul: {artikul}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        products = data.get("data", {}).get("products", [])
                        if products:
                            product = products[0]
                            artikul = product.get("id")
                            name = product.get("name")
                            standart_price = product.get("priceU") / 100
                            sell_price = product.get("salePriceU") / 100
                            rating = product.get("reviewRating", 0.0)
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
                            f"Failed to fetch product details for artikul: {artikul}. Status code: {response.status}"
                        )
                        return None

        except aiohttp.ClientError as e:
            logger.exception(f"Aiohttp client error occurred: {e}")
            return None
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return None


if __name__ == "__main__":
    import asyncio
    client = WildberriesAPIClient()
    response = asyncio.run(client.fetch_product_details("74312538"))
    print(response)