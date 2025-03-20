from fastapi import FastAPI
import logging

from routers.auth.router import router as auth_router
from database.main import init_models

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
app = FastAPI()

app.include_router(auth_router, prefix="/api/v1/auth")


@app.on_event("startup")
async def startup_event():
    await init_models()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=80, reload=True)
