import asyncio

from scheduler.tasks import add_product_in_db  

from dotenv import load_dotenv
import os
from logging import getLogger

logger = getLogger(__name__)

load_dotenv()
INTERVAL_IN_MINUTES = int(os.getenv("INTERVAL_IN_MINUTES"))


async def main_scheduler():
    while True:
        try:
            await add_product_in_db()
            await asyncio.sleep(INTERVAL_IN_MINUTES * 60) 
        except Exception as e:
            logger.error(f"Ошибка выполнения задачи: {str(e)}", exc_info=True)
