from fastapi import APIRouter
from .oauth2_router import router as oauth2_router
from .register_router import router as register_router
from .change_password_router import router as change_password_router
from .user_info_router import router as user_info_router


router = APIRouter()
router.include_router(register_router, prefix="/auth", tags=["auth"])
router.include_router(oauth2_router, prefix="/auth", tags=["auth"])
router.include_router(change_password_router, prefix="/auth", tags=["auth"])
router.include_router(user_info_router, prefix="/auth", tags=["auth"])
