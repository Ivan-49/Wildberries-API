from fastapi import FastAPI
import logging
from logging.handlers import RotatingFileHandler

from routers.auth.router import router as auth_router
from routers.third_party_integrations.router import third_party_router
from database.main import init_models
from fastapi.openapi.utils import get_openapi

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()


app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(
    third_party_router, prefix="/api/v1/third-party", tags=["third-party"]
)


@app.on_event("startup")
async def startup_event():
    try:
        await init_models()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=80, reload=True)
