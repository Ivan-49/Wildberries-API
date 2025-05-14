from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from database import get_session

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/auth-by-username",
    scopes={
        "logout": "Log out of the application",
    },
)


# TODO: сделать роутер для обработки подписок пользоватлей на товары
@router.get()
async def get_all_user_subs(
    user_id=Depends(oauth2_scheme), session=Depends(get_session)
): ...
