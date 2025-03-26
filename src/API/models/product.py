from sqlalchemy import Column, Integer, String, Float, DateTime

from database.base import Base


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    marketplace = Column(String)
    artikul = Column(String)
    name = Column(String)
    standart_price = Column(Float)
    sell_price = Column(Float)
    total_quantity = Column(Integer)
    created_at = Column(DateTime)
    rating = Column(Float)
