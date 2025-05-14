from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from loguru import logger

import os
from starlette.middleware.base import BaseHTTPMiddleware
from middleware.auth_middleware import auth_middleware
from routers.auth.router import router as auth_router

from routers.third_party_integrations.router import third_party_router
from database.main import init_models

from scheduler.main import main_scheduler
from dotenv import load_dotenv
load_dotenv()
# Настройка базового логгера
logger.add(
    "logs/app.log",
    format="{time} {level} {message}",
    level="INFO",
    rotation="00:00",
    compression="zip",
    enqueue=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # код, который выполняется при старте приложения
    for key, value in os.environ.items():
        logger.debug(f"{key}={value}")

    try:
        await init_models()
        logger.info("Database connection established")

        # Запускаем планировщик в отдельной задаче

        global scheduler_task
        scheduler_task = asyncio.create_task(main_scheduler())

    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise e
    print("Startup logic here")
    yield
    # код, который выполняется при завершении приложения
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
    print("Shutdown logic here")


app = FastAPI(debug=True, lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(third_party_router, prefix="/api/v1/third-party")
  


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=80, reload=True)
