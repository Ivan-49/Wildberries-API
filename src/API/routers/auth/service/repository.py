from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from logging import getLogger
from sqlalchemy.exc import IntegrityError
from typing import Optional

from models.user import UserModel
from routers.auth.schemas.user import UserShema
from database.main import get_session
logger = getLogger(__name__)



class UserRepository:
    async def create_user(self, user: UserShema, session: AsyncSession) -> UserModel:
        from routers.auth.service.security import get_password_hash

        logger.error("Начали создавать пользователя")
        try:
            if not user:
                logger.error("User is None")
                return None
            user = user.model_dump()
            if "password" in user:
                user["hashed_password"] = await get_password_hash(user["password"])
                del user["password"]
            user = UserModel(**user)

            session.add(user)
            await session.commit()
            logger.info("User created successfully")
            return user
        except IntegrityError as e:
            if "duplicate key" in str(e):
                logger.error("Пользователь с таким ID или username уже существует")
                return {"message": "User already existsx"}
            raise e
        except Exception as e:
            logger.error(f"Error create user: {e}")
            return None

    async def get_user_by_user_id(
        self, user_id: int, session: AsyncSession
    ) -> Optional[UserModel]:
        try:
            result = await session.execute(
                select(UserModel).where(UserModel.user_id == user_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error get user: {e}")
            return None

    async def get_user_by_username(
        self, username: str, session: AsyncSession
    ) -> Optional[UserModel]:
        try:

            result = await session.execute(
                select(UserModel).where(UserModel.username == username)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error get user: {e}")
            return None
    
    async def change_user_password(self, user: UserModel, old_password: str, new_password: str, session: AsyncSession) -> Optional[UserModel]:
        from routers.auth.service.security import verify_password
        from routers.auth.service.security import get_password_hash
        
        try:
            if not await verify_password(old_password, user.hashed_password):
                return None
            
            user.hashed_password = await get_password_hash(new_password)
            session.add(user)
            await session.commit()
            return user
        except Exception as e:
            logger.error(f"Error get user: {e}")
            return None