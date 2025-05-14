from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base


class UserSubsToProductModel(Base):
    __tablename__ = "user_subs_to_products"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    subscribed_at = Column(DateTime, server_default=func.now())

    # Связь с моделью пользователя
    user = relationship("UserModel", back_populates="subscriptions")

    # Связь с моделью продукта
    product = relationship("ProductModel", back_populates="subscriptions")
