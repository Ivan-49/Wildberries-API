from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from logging import getLogger
from typing import Optional

from routers.auth.service.repository import UserRepository
from routers.auth.service.security import (
    verify_password,
    get_password_hash,
)
from routers.auth.service.redis import check_token_in_blacklist, delete_token
from schemas.user import UserShema
from models.user import UserModel

logger = getLogger(__name__)


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    async def register_user(self, user: UserShema, session: AsyncSession) -> UserModel:
        existing_user = await self.user_repo.get_user_by_username(
            user.username, session
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        return await self.user_repo.create_user(user, session)

    async def change_password(
        self,
        user: UserModel,
        old_password: str,
        new_password: str,
        session: AsyncSession,
    ) -> Optional[UserModel]:
        if not await verify_password(old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid old password")

        if await check_token_in_blacklist(user.user_id):
            raise HTTPException(status_code=401, detail="Account is blocked")

        user.hashed_password = await get_password_hash(new_password)
        return await self.user_repo.update_user(user, session)

    async def logout_user(
        self, user_id: int, session: AsyncSession
    ) -> Optional[UserModel]:
        user = await self.user_repo.get_user_by_user_id(user_id, session)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await delete_token(user.user_id)
        return user
