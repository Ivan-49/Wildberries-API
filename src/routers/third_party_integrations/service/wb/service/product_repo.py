from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func, text, desc
from schemas import ProductShema, ProductHistoryShema
from models import ProductModel, ProductHistoryModel
from loguru import logger


# class ProductRepository:
#     async def add_product(self, product: ProductShema, session: AsyncSession):
#         try:
#             product_dumb = product.model_dump()
#             product = ProductModel(**product_dumb)
#             session.add(product)
#             await session.commit()
#             return product
#         except IntegrityError as e:
#             logger.error(f"Error add product: {e}")
#             raise e

#     async def get_last_product_by_artikul(self, artikul: str, session: AsyncSession):

#         try:
#             result = await session.execute(
#                 select(ProductModel).where(ProductModel.artikul == artikul)
#             )
#             return result.scalars().first()
#         except Exception as e:
#             logger.error(f"Error get last product by artikul: {e}")
#             raise e

#     async def get_all_products(self, session: AsyncSession) -> list[ProductModel]:
#         try:
#             result = await session.execute(select(ProductModel))
#             return result.scalars().all()
#         except Exception as e:
#             logger.error(f"Error get all products: {e}")
#             raise e

#     async def get_latest_products_by_artikul(
#         self, artikul: str, count: int, session: AsyncSession
#     ):
#         try:
#             result = await session.execute(
#                 select(ProductModel)
#                 .where(ProductModel.artikul == artikul)
#                 .order_by(ProductModel.created_at)
#                 .limit(count)
#             )
#             return result.scalars().all()
#         except Exception as e:
#             logger.error(f"Error get latest products by artikul: {e}")
#             raise e

#     async def get_products_paginated(
#         self,
#         page: int,
#         per_page: int,
#         session: AsyncSession,
#         search_query: str | None = None,
#         min_similarity: float = 0.3,
#         exclude_artikul: str | None = None,
#     ):
#         try:
#             base_query = select(ProductModel).distinct(ProductModel.artikul)

#             if exclude_artikul:
#                 base_query = base_query.where(ProductModel.artikul != exclude_artikul)

#             if search_query:
#                 similarity = func.similarity(ProductModel.name, search_query)
#                 base_query = (
#                     base_query.add_columns(similarity.label("similarity"))
#                     .where(similarity >= min_similarity)
#                     .order_by(
#                         ProductModel.artikul,  # Первичный порядок по артикулу
#                         desc("similarity"),  # Вторичный порядок по similarity
#                     )
#                 )
#             else:
#                 base_query = base_query.order_by(ProductModel.id)

#             query = base_query.offset((page - 1) * per_page).limit(per_page)

#             result = await session.execute(query)

#             if search_query:
#                 return [
#                     {"product": product, "similarity": similarity}
#                     for product, similarity in result.all()
#                 ]
#             else:
#                 return result.scalars().all()
#         except Exception as e:
#             logger.error(f"Error get products paginated: {e}")
#             raise e

#     async def add_product_to_subscribe(
#         self, artikul: str, marketplace: str, session: AsyncSession
#     ):
#         try:
#             existing = await session.execute(
#                 select(SubscribeModel).where(
#                     SubscribeModel.marketplace == marketplace,
#                     SubscribeModel.artikul == artikul,
#                 )
#             )

#             if existing.scalars().first():
#                 logger.debug(
#                     f"Запись для marketplace={marketplace}, artikul={artikul} уже существует"
#                 )
#                 return

#             # Если записи нет — добавляем
#             new_product = SubscribeModel(marketplace=marketplace, artikul=artikul)
#             session.add(new_product)
#             await session.commit()

#         except Exception as e:
#             logger.error(f"Error add product to subscribe: {e}")
#             raise e

#     async def get_all_subscribes_from_marketplace(
#         self, marketplace: str, session: AsyncSession
#     ) -> list[SubscribeModel]:
#         try:
#             result = await session.execute(
#                 select(SubscribeModel).where(SubscribeModel.marketplace == marketplace)
#             )
#             return result.scalars().all()
#         except Exception as e:
#             logger.error(f"Error get all subscribes from marketplace: {e}")
#             raise e


class ProductRepository:
    async def add_product(
        self, product: ProductShema, session: AsyncSession
    ) -> ProductModel:
        try:
            product_dumb = product.model_dump()
            product = ProductModel(**product_dumb)
            session.add(product)
            await session.commit()
            return product
        except IntegrityError as e:
            logger.error(f"Error add product: {e}")
            raise e

    async def get_product_by_artikul(
        self, artikul: str, session: AsyncSession
    ) -> ProductModel:
        try:
            result = await session.execute(
                select(ProductModel).where(ProductModel.artikul == artikul)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error get product by artikul: {e}")
            raise e

    async def delete_product_by_artikul(
        self, artikul: str, session: AsyncSession
    ) -> ProductModel:
        try:
            result = await session.execute(
                select(ProductModel).where(ProductModel.artikul == artikul)
            )
            product = result.scalars().first()
            session.delete(product)
            await session.commit()
            return product
        except Exception as e:
            logger.error(f"Error delete product by artikul: {e}")
            raise e

    async def get_count_products(self, session: AsyncSession) -> int:
        try:
            result = await session.execute(select(func.count(ProductModel.id)))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error get count products: {e}")
            raise e

    async def add_product_history(
        self, artikul: str, product_history: ProductHistoryShema, session: AsyncSession
    ) -> ProductModel:
        try:
            product_id = (await self.get_product_by_artikul(artikul, session)).id
            product_history_dumb = product_history.model_dump()
            product_history_dumb["product_id"] = product_id
            product_history = ProductHistoryModel(**product_history_dumb)
            session.add(product_history)
            await session.commit()
            return product_history
        except IntegrityError as e:
            logger.error(f"Error add product history: {e}")
            raise e

    async def get_last_product_history_by_artikul(
        self, artikul: str, session: AsyncSession
    ) -> ProductHistoryModel:
        try:
            # result = await session.execute(
            #     select(ProductHistoryModel)
            #     .where(ProductHistoryModel.artikul == artikul)
            #     .order_by(ProductHistoryModel.created_at.desc())
            # )
            result = await session.execute(
            select(ProductHistoryModel)
            .join(ProductModel, ProductModel.id == ProductHistoryModel.product_id)
            .filter(ProductModel.artikul == artikul)
            .order_by(ProductHistoryModel.created_at.desc())
            )
            
            if not (result:=result.scalars().first()):
                logger.error(
                    f"Product history with artikul {artikul} not found in ProductHistory table"
                )
                return {
                    "message": f"Product history with artikul {artikul} not found in ProductHistory table"
                }
            return result
        except Exception as e:
            logger.error(f"Error get last product history by artikul: {e}")
            raise e

    async def get_lasted_products_by_artikul(
        self, artikul: str, count: int, session: AsyncSession
    ) -> list[ProductHistoryModel]:
        try:
            result = await session.execute(
                select(ProductHistoryModel)
                .join(ProductModel, ProductHistoryModel.product_id == ProductModel.id)
                .where(ProductModel.artikul == artikul)
                .order_by(ProductHistoryModel.created_at.desc())
                .limit(count)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error get lasted products by artikul: {e}")
            raise e

    async def get_products_paginated(
        self,
        session: AsyncSession,
        page: int = 1,
        per_page: int = 10,
        search_query: str | None = None,
        min_similarity: float = 0.3,
        exclude_artikul: str | None = None,
    ):

        try:
            base_query = select(ProductModel).distinct(ProductModel.artikul)

            if exclude_artikul:
                base_query = base_query.where(ProductModel.artikul != exclude_artikul)

            if search_query:
                similarity = func.similarity(ProductModel.name, search_query)
                base_query = (
                        base_query.add_columns(similarity.label("similarity"))
                        .where(similarity >= min_similarity)
                        .order_by(ProductModel.artikul, desc("similarity"))  # <-- Исправлено!
                        )
            else:
                base_query = base_query.order_by(ProductModel.id)  

            query = base_query.offset((page - 1) * per_page).limit(per_page)

            result = await session.execute(query)

            if search_query:
                rows = result.all()  # Получаем все строки один раз
                response = []
                for product, similarity in rows:
                    product_data = await self.get_last_product_history_by_artikul(
                        artikul=product.artikul, session=session
                    )
                    response.append({
                        "product": product,
                        "product_data": product_data,
                        "similarity": similarity
                    })
                return response
            else:
                return result.scalars().all()

        except Exception as e:
            logger.error(f"Error get products paginated: {e}")
            raise e
    async def get_all_products_from_marketplace(
        self, marketplace: str, session: AsyncSession
        ):
        try:
            result = await session.execute(
                select(ProductModel).where(ProductModel.marketplace == marketplace)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error get all subscribes from marketplace: {e}")
            raise e