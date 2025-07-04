from fastapi import APIRouter
from loguru import logger

from .oauth2_router import router as oauth2_router
from .register_router import router as register_router
from .change_password_router import router as change_password_router
from .user_info_router import router as user_info_router


router = APIRouter()
try:
    router.include_router(register_router, tags=["auth"])
    router.include_router(oauth2_router, tags=["auth"])
    router.include_router(change_password_router, tags=["auth"])
    router.include_router(user_info_router, tags=["auth"])
    logger.info("Auth Router included successfully")

except Exception as e:
    logger.error(f"Error including Auth Router: {str(e)}")
