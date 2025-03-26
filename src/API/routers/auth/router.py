from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from logging import getLogger

from database.main import get_session
from routers.auth.service.security import (
    create_access_token,
    verify_token,
    verify_password,
    delete_token,
    get_password_hash,
)
from routers.auth.service.repository import UserRepository

from schemas.token import TokenSchema
from schemas.user import (
    UserShema,
)

router = APIRouter()
user_repository = UserRepository()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/auth-by-username",
    scopes={
        "logout": "Log out of the application",
    },
)


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


@router.post("/auth-by-username", response_model=TokenSchema)
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

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    try:
        user_id = await verify_token(token, HTTPException(status_code=401, detail="Invalid token"))
        user = await user_repository.get_user_by_user_id(user_id, session)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Проверяем блокировку через репозиторий
        if await user_repository.is_user_blocked(user.user_id):
            raise HTTPException(status_code=401, detail="Account is blocked")

        updated_user = await user_repository.change_user_password(
            user, old_password, new_password, session
        )

        if not updated_user:
            raise HTTPException(
                status_code=400,
                detail="Failed to change password. Old password might be incorrect."
            )

        return {"message": "Password changed successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/user-info")
async def get_user_info(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    user_id = await verify_token(token, HTTPException(status_code=401, detail="Invalid token"))
    user = await user_repository.get_user_by_user_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user.user_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "language": user.language,
        "is_bot": user.is_bot,
        "premium_status": user.premium_status,}

@router.post("/logout")
async def logout_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    user_id = await verify_token(token, HTTPException(status_code=401, detail="Invalid token"))
    user = await user_repository.get_user_by_user_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await delete_token(user_id)
    return {"message": f"User {user.username} logged out successfully"}
