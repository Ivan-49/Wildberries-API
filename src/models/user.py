from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.base import Base


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language = Column(String, nullable=True)
    is_bot = Column(Boolean, default=False, nullable=True)
    premium_status = Column(String, nullable=True)

    # Связь с таблицей подписок
    subscriptions = relationship("UserSubsToProductModel", back_populates="user")
