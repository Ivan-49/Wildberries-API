from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from dotenv import load_dotenv
import os
from models import ProductModel, UserModel, SubscribeModel
from database.base import Base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
ECHO_DB = True if os.getenv("ECHO_DB") == "1" else False
engine = create_async_engine(DATABASE_URL, echo=ECHO_DB)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session
