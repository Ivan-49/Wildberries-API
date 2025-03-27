from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func, text, desc
from schemas import ProductShema
from models import ProductModel, SubscribeModel
import logging

logger = logging.getLogger(__name__)

class ProductRepository:
    async def add_product(self, product: ProductShema, session: AsyncSession):
        try:
            product_dumb = product.model_dump()
            product = ProductModel(**product_dumb)
            session.add(product)
            await session.commit()
            return product
        except IntegrityError as e:
            raise e
        
    async def get_last_product_by_artikul(self, artikul: str, session: AsyncSession):
        result = await session.execute(
            select(ProductModel).where(ProductModel.artikul == artikul)
    ) 
        return result.scalars().first()
    
    async def get_all_products(self, session: AsyncSession) -> list[ProductModel]:
        result = await session.execute(select(ProductModel))
        return result.scalars().all() 
    
    async def get_latest_products_by_artikul (self, artikul: str, count: int, session: AsyncSession) :
        result = await session.execute(
            select(ProductModel).where(ProductModel.artikul == artikul).order_by(ProductModel.created_at).limit(count)
        )
        return result.scalars().all() 

    async def get_products_paginated(
        self,
        page: int,
        per_page: int,
        session: AsyncSession,
        search_query: str | None = None,
        min_similarity: float = 0.3,
        exclude_artikul: str | None = None
    ):
        base_query = select(ProductModel).distinct(ProductModel.artikul)
        
        if exclude_artikul:
            base_query = base_query.where(ProductModel.artikul != exclude_artikul)

        if search_query:
            similarity = func.similarity(ProductModel.name, search_query)
            base_query = base_query.add_columns(
                similarity.label('similarity')
            ).where(
                similarity >= min_similarity
            ).order_by(
                ProductModel.artikul,  # Первичный порядок по артикулу
                desc('similarity')     # Вторичный порядок по similarity
            )
        else:
            base_query = base_query.order_by(ProductModel.id)

        query = base_query.offset((page - 1) * per_page).limit(per_page)

        result = await session.execute(query)
        
        if search_query:
            return [
                {
                    "product": product,
                    "similarity": similarity
                } 
                for product, similarity in result.all()
            ]
        else:
            return result.scalars().all()


    
    async def add_product_to_subscribe(self, artikul: str,  marketplace: str, session: AsyncSession):
        existing = await session.execute(
        select(SubscribeModel).where(
                SubscribeModel.marketplace == marketplace,
                SubscribeModel.artikul == artikul
            )
        )
        
        if existing.scalars().first():
            logger.warning(f"Запись для marketplace={marketplace}, artikul={artikul} уже существует")
            return
        
        # Если записи нет — добавляем
        new_product = SubscribeModel(marketplace=marketplace, artikul=artikul)
        session.add(new_product)
        await session.commit()
    
    async def get_all_subscribes_from_marketplace(self, marketplace: str, session: AsyncSession) -> list[SubscribeModel]:
        result = await session.execute(select(SubscribeModel).where(SubscribeModel.marketplace == marketplace))
        return result.scalars().all()
