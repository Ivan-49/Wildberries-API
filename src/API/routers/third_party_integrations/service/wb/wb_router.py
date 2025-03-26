from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from routers.third_party_integrations.service.wb.wildberries_api_client import (
    WildberriesAPIClient,
)


router = APIRouter()
wb_client = WildberriesAPIClient()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/auth/auth-by-username")


@router.get("/get-product-details/{artikul}")
async def get_product_details(
    artikul: str,
    user_id: str = Depends(oauth2_scheme),
):
    product = await wb_client.fetch_product_details(artikul)
    return product
