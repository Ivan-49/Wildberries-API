from fastapi import APIRouter

from routers.third_party_integrations.service.wb.wb_router import router as wb_router
from routers.third_party_integrations.service.AI.AI_router import (
    router as giga_chat_router,
)

third_party_router = APIRouter()
try:
    third_party_router.include_router(
        router=wb_router, prefix="/wildberries", tags=["wildberries"]
    )
    third_party_router.include_router(
        router=giga_chat_router, prefix="/ai-analyze", tags=["ai-analyze"]
    )
except Exception as e:
    print(f"Error including third-party router: {str(e)}")
