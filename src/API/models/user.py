from sqlalchemy import Column, Integer, String, Boolean

from database.main import Base


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language = Column(String, nullable=True)
    is_bot = Column(Boolean, default=False, nullable=True)
    premium_status = Column(String, nullable=True)
