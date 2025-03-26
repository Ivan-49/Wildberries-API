from datetime import datetime, timedelta
from jose import JWTError, jwt
from argon2 import PasswordHasher
from dotenv import load_dotenv
import os
from redis_client import RedisClient
import logging

redis = RedisClient()

logger = logging.getLogger(__name__)

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

argon2 = PasswordHasher(memory_cost=2**16, parallelism=4, hash_len=32, salt_len=16)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        argon2.verify(hashed_password, plain_password)
        return True
    except:
        return False


async def get_password_hash(password: str) -> str:
    return argon2.hash(password)


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    if await redis.check_blacklist(data["sub"]):
        redis.delete_token_from_blacklist(data["sub"])
    if await redis.check_token(data["sub"]):
        return await redis.get_token(data["sub"])

    if not data or not JWT_SECRET_KEY:
        raise ValueError("Некорректные данные для создания токена")

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": int(expire.timestamp()), "sub": str(data["sub"])})

    jwt_token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    await redis.save_token(
        data["sub"],
        jwt_token,
        (
            ACCESS_TOKEN_EXPIRE_MINUTES
            if expires_delta is None
            else expires_delta.total_seconds()
        ),
    )

    return jwt_token

async def verify_token(token: str, credentials_exception) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_id = int(user_id)

        # Проверяем Redis
        if not await redis.check_token(user_id):
            logger.error("Token not found in Redis")
            raise credentials_exception

        # Проверяем черный список
        if await redis.check_blacklist(user_id):
            raise credentials_exception

        return user_id
    except JWTError as e:
        raise credentials_exception

async def check_token_in_blacklist(user_id: int) -> bool:
    return await redis.check_blacklist(user_id)

async def delete_token(user_id: int) -> None:
    await redis.delete_token_from_blacklist(user_id)
    await redis.delete_token(user_id)
    return None

