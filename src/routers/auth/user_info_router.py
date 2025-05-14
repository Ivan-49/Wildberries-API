from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from fastapi.security import OAuth2PasswordBearer

from database.main import get_session
from routers.auth.service.repository import UserRepository
from routers.auth.service.security import decode_token_to_user_id

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/auth-by-username",
    scopes={
        "logout": "Log out of the application",
    },
)


router = APIRouter()
user_repository = UserRepository()


@router.get("/user-info")
async def get_user_info(
    token: int = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
):
    user_id = await decode_token_to_user_id(
        token, HTTPException(status_code=401, detail="Invalid token")
    )
    user = await user_repository.get_user_by_user_id(user_id, session)
    if not user:
        logger.error(f"User {user.username} {user.user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user.user_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "language": user.language,
        "is_bot": user.is_bot,
        "premium_status": user.premium_status,
    }
