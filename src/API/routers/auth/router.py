from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from logging import getLogger

from database.main import get_session
from routers.auth.service.security import (
    create_access_token,
    verify_token,
    verify_password,
)
from routers.auth.service.repository import UserRepository

from routers.auth.schemas.token import TokenSchema
from routers.auth.schemas.user import UserShema

router = APIRouter()
user_repository = UserRepository()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logger = getLogger(__name__)


@router.post("/register")
async def register_user(user: UserShema, session: AsyncSession = Depends(get_session)):
    user_in_db = await user_repository.get_user_by_username(user.username, session)
    if user_in_db:
        raise HTTPException(status_code=400, detail="User already exists")

    user_in_db = await user_repository.create_user(user, session=session)
    return {
        "message": "User created successfully",
        "user_id": user_in_db.user_id,
        "username": user_in_db.username,
        "first_name": user_in_db.first_name,
        "last_name": user_in_db.last_name,
    }


@router.post("/token/username", response_model=TokenSchema)
async def login_by_username(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await user_repository.get_user_by_username(form_data.username, session)
    if not user or not await verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(data={"sub": user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token/user-id", response_model=TokenSchema)
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
    access_token = await create_access_token(data={"sub": user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}



# @router.post("/change-password-by-username")
# async def change_password(
#     data: ChangePasswordbyUsernameSchema, session: AsyncSession = Depends(get_session)
# ):
#     user = await user_repository.get_user_by_username(data.user_name, session)
#     if not user:
#         raise HTTPException(status_code=400, detail="User not found")
#     await user_repository.change_user_password(
#         user, data.old_password, data.new_password, session
#     )
#     return {"message": "Password changed successfully"}

# @router.post("/logout")
# async def logout_user(username: str): ...


# @router.get("/me")
# async def get_user(user_id: int = Depends(get_current_user)): ...

