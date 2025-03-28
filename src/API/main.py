from fastapi import FastAPI
import logging
from logging.handlers import RotatingFileHandler
import asyncio

from routers.auth.router import router as auth_router
from routers.third_party_integrations.router import third_party_router
from database.main import init_models
from scheduler.main import main_scheduler

# Настройка базового логгера
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(
    third_party_router, prefix="/api/v1/third-party"
)

@app.on_event("startup")
async def startup_event():
    try:
        await init_models()
        logger.info("Database connection established")
        
        # Запускаем планировщик в отдельной задаче
        global scheduler_task
        scheduler_task = asyncio.create_task(main_scheduler())
        
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
    if scheduler_task:
        # Отменяем задачу планировщика
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            logger.info("Scheduler task cancelled successfully")
        except Exception as e:
            logger.error(f"Error while cancelling scheduler task: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=80, reload=True)
