from sqlalchemy.ext.asyncio import AsyncSession

from schemas import ProductShema
from models import ProductModel


class ProductRepository:
    async def add_product(self, product: ProductShema, session: AsyncSession) -> None:
        product_dumb = product.model_dump()
        product_dumb["created_at"] = ...
