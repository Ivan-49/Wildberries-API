import asyncio
import pytest
import pytest_asyncio
from database.main import engine, Base
from loguru import logger


@pytest.fixture(scope="session")
def event_loop():
    """Event loop с скоупом session для фикстур с скоупом session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    logger.info("===> START PREPARE DATABASE")
    async with engine.begin() as conn:
        logger.info("===> DROP ALL")
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("===> CREATE ALL")
        await conn.run_sync(Base.metadata.create_all)
    logger.info("===> END PREPARE DATABASE")
    yield
    async with engine.begin() as conn:
        logger.info("===> DROP ALL AFTER TESTS")
        await conn.run_sync(Base.metadata.drop_all)
