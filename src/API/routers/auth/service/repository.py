from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from logging import getLogger
from sqlalchemy.exc import IntegrityError
from typing import Optional

from models.user import UserModel
from schemas.user import UserShema
from routers.auth.service.security import get_password_hash

logger = getLogger(__name__)


class UserRepository:
    async def create_user(self, user: UserShema, session: AsyncSession) -> UserModel:
        try:
            user = user.model_dump()
            user["hashed_password"] = await get_password_hash(user["password"])
            del user["password"]
            user = UserModel(**user)

            session.add(user)
            await session.commit()
            return user
        except IntegrityError as e:
            raise e

    async def get_user_by_user_id(
        self, user_id: int, session: AsyncSession
    ) -> Optional[UserModel]:
        result = await session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        return result.scalars().first()

    async def get_user_by_username(
        self, username: str, session: AsyncSession
    ) -> Optional[UserModel]:
        result = await session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalars().first()

    async def update_user(
        self, user: UserModel, session: AsyncSession
    ) -> Optional[UserModel]:
        session.add(user)
        await session.commit()
        return user
