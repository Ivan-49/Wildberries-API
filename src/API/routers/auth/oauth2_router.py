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
    user = await user_repository.get_user_by_username(form_data.username, session)
    if not user or not await verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неправильный логин или пароль")

    access_token = await create_access_token(data={"sub": user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth-by-user-id", response_model=TokenSchema)
async def login_by_user_id(
    user_id: int, password: str, session: AsyncSession = Depends(get_session)
):
    user = await user_repository.get_user_by_user_id(user_id, session)
    if not user or not await verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect user_id or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
        

    logger.debug(f"""
    User {user.username} logged out successfully
    токен до удаления: {await verify_token(token, HTTPException(status_code=401, detail="Invalid token"))}
    удаление токена: {await delete_token(user_id)}
    токен после удаления: {await verify_token(token, HTTPException(status_code=401, detail="Invalid token"))}
    """)


    # await delete_token(user_id)
    return {"message": f"User {user.username} logged out successfully"}
