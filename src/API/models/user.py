from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

from database.main import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    user_id = Column(Integer, unique=True, index=True)
    language = Column(String, nullable=True)
    is_bot = Column(Boolean, default=False, nullable=True)
    premium_status = Column(String, nullable=True)
