from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from logging import getLogger

from database.main import get_session
from routers.auth.service.repository import UserRepository
from schemas.user import UserShema


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/auth-by-username",
    scopes={
        "logout": "Log out of the application",
    },
)

router = APIRouter()
user_repository = UserRepository()

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
