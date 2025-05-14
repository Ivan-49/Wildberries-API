from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    marketplace = Column(String, nullable=False)
    artikul = Column(String, nullable=False)
    name = Column(String, nullable=False)

    # Уникальное ограничение для комбинации marketplace и artikul
    __table_args__ = (
        UniqueConstraint("marketplace", "artikul", name="uq_marketplace_artikul"),
        # Уникальный индекс для всей строки
        UniqueConstraint("marketplace", "artikul", "name", name="uq_product_full_row"),
    )

    # Связь с историей продукта
    history = relationship("ProductHistoryModel", back_populates="product")

    # Связь с таблицей подписок
    subscriptions = relationship("UserSubsToProductModel", back_populates="product")


class ProductHistoryModel(Base):
    __tablename__ = "product_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    sell_price = Column(Float, nullable=False)
    standart_price = Column(Float, nullable=False)

    total_quantity = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime, server_default=func.now())

    # Обратная ссылка на продукт
    product = relationship("ProductModel", back_populates="history")
