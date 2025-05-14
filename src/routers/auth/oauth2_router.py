from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from loguru import logger

from database import get_session
from routers.auth.service.security import (
    create_access_token,
    decode_token_to_user_id,
    verify_password,
)
from routers.auth.service.repository import UserRepository
from schemas.token import TokenSchema
from redis_client import RedisClient


router = APIRouter()
user_repository = UserRepository()
redis_client = RedisClient()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/auth-by-username",
    scopes={
        "logout": "Log out of the application",
    },
)


@router.post("/auth-by-username", response_model=TokenSchema)
async def login_by_username(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    try:
        user = await user_repository.get_user_by_username(form_data.username, session)
        if not user or not await verify_password(
            form_data.password, user.hashed_password
        ):
            logger.error(f"User {user.username} {user.user_id} sent wrong password")
            raise HTTPException(status_code=401, detail="Неправильный логин или пароль")

        access_token = await create_access_token(data={"sub": user.user_id})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        logger.error(f"Error in login_by_username: {e}")
        raise HTTPException(status_code=401, detail="Неправильный логин или пароль")


@router.post("/auth-by-user-id", response_model=TokenSchema)
async def login_by_user_id(
    user_id: int, password: str, session: AsyncSession = Depends(get_session)
):
    user = await user_repository.get_user_by_user_id(user_id, session)
    if not user or not await verify_password(password, user.hashed_password):
        logger.error(f"Incorrect user_id or password {user_id}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect user_id or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(data={"sub": int(user.user_id)})
    logger.info(f"access_token sent to user {user.username} - {user.user_id} ")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
):
    user_id = await decode_token_to_user_id(
        token, HTTPException(status_code=401, detail="Invalid token")
    )
    user = await user_repository.get_user_by_user_id(user_id, session)
    if not user:
        logger.error(f"User {user.username} {user.user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    await redis_client.add_to_blacklist(user.user_id)
    logger.info(f"User {user.username} {user.user_id} logged out successfully")
    return {"message": f"User {user.username} logged out successfully"}
