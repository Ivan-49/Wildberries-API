from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from logging import getLogger

from database.main import get_session
from routers.auth.service.repository import UserRepository
from routers.auth.service.security import (
    verify_password,
    get_password_hash,
    verify_token,
)

router = APIRouter()
user_repository = UserRepository()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/auth/auth-by-username")

logger = getLogger(__name__)


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    user_id = await verify_token(
        token, HTTPException(status_code=401, detail="Invalid token")
    )
    user = await user_repository.get_user_by_user_id(user_id, session)
    user = await user_repository.get_user_by_user_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not await verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid old password")

    user.hashed_password = await get_password_hash(new_password)
    await user_repository.update_user(user, session)
    return {"message": "Password changed successfully"}
