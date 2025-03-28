from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from logging import getLogger
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from database.main import get_session
from routers.auth.service.security import (
    create_access_token,
    verify_token,
    verify_password,
)
from routers.auth.service.redis import delete_token
from routers.auth.service.repository import UserRepository
from schemas.token import TokenSchema

router = APIRouter()
user_repository = UserRepository()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/auth/auth-by-username")

logger = getLogger(__name__)


@router.post("/auth-by-username", response_model=TokenSchema)
async def login_by_username(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    logger.debug(f"Attempting login for username: {form_data.username}")
    user = await user_repository.get_user_by_username(form_data.username, session)
    
    if not user:
        logger.warning(f"User not found: {form_data.username}")
        raise HTTPException(status_code=401, detail="Неправильный логин или пароль")
    
    logger.debug(f"User found, verifying password for: {form_data.username}")
    if not await verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Invalid password for user: {form_data.username}")
        raise HTTPException(status_code=401, detail="Неправильный логин или пароль")

    logger.info(f"Successful login for user: {form_data.username}")
    access_token = await create_access_token(data={"sub": user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth-by-user-id", response_model=TokenSchema)
async def login_by_user_id(
    user_id: int, password: str, session: AsyncSession = Depends(get_session)
):
    logger.debug(f"Attempting login for user_id: {user_id}")
    user = await user_repository.get_user_by_user_id(user_id, session)
    
    if not user:
        logger.warning(f"User not found with ID: {user_id}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect user_id or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"User found, verifying password for ID: {user_id}")
    if not await verify_password(password, user.hashed_password):
        logger.warning(f"Invalid password for user ID: {user_id}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect user_id or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Successful login for user ID: {user_id}")
    access_token = await create_access_token(data={"sub": int(user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
):
    user_id = await verify_token(
        token, HTTPException(status_code=401, detail="Invalid token")
    )
    user = await user_repository.get_user_by_user_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await delete_token(user_id)
    return {"message": f"User {user.username} logged out successfully"}
