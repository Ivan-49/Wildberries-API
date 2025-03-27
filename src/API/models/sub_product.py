from sqlalchemy import Column, Integer, String, DateTime, Float, UniqueConstraint

from database.base import Base



class SubscribeModel(Base):
    __tablename__ = "subs_products"

    id = Column(Integer, primary_key=True, index=True)
    marketplace = Column(String, nullable=False)
    artikul = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('marketplace', 'artikul', name='uq_marketplace_artikul'),
    )