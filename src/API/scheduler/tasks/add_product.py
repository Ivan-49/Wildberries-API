from routers.third_party_integrations.service.wb.service.product_repo import ProductRepository
from schemas.product import ProductShema
from database.main import async_session
from routers.third_party_integrations.service.wb.service.wildberries_api_client import WildberriesAPIClient

import logging


product_repository = ProductRepository()
logger = logging.getLogger(__name__)


wb_client = WildberriesAPIClient()

async def add_product_in_db():
    async with async_session() as session:
        try:
            subs = await product_repository.get_all_subscribes_from_marketplace("wildberries", session)
            for sub in subs:
                product = await wb_client.fetch_product_details(sub.artikul)
                product["marketplace"] = sub.marketplace
                product = ProductShema(**product)
                await product_repository.add_product(product, session)
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")
            session.rollback()

