from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from database.main import get_session
from routers.auth.service.repository import UserRepository
from schemas.user import UserShema


router = APIRouter()
user_repository = UserRepository()


@router.post("/register", status_code=201)
async def register_user(user: UserShema, session: AsyncSession = Depends(get_session)):
    user_in_db = await user_repository.get_user_by_username(user.username, session)
    if user_in_db:
        logger.error("User already exists")
        raise HTTPException(status_code=400, detail="User already exists")

    user_in_db = await user_repository.create_user(user, session=session)
    return {
        "message": "User created successfully",
        "user_id": user_in_db.user_id,
        "username": user_in_db.username,
        "first_name": user_in_db.first_name,
        "last_name": user_in_db.last_name,
    }
