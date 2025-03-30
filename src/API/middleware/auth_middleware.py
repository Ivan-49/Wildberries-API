from fastapi import Request
from database import get_session
from logging import getLogger
from redis_client import RedisClient
from fastapi.responses import JSONResponse

logger = getLogger(__name__)
redis_client = RedisClient()


async def auth_middleware(request: Request, call_next):
    from routers.auth.service.security import decode_token_to_user_id
    from routers.auth.service.repository import UserRepository

    user_repo = UserRepository()
    excluded_urls = [
        "/api/v1/auth/auth-by-username",
        "/api/v1/auth/auth-by-user-id",
        "/api/v1/auth/register",
        "/docs",
        "/openapi.json",
    ]
    if request.url.path in excluded_urls:
        return await call_next(request)

    token = request.headers.get("Authorization")
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    try:
        # Проверяем формат токена
        scheme, token_value = token.split(" ", 1)
        if scheme.lower() != "bearer":
            return JSONResponse(
                status_code=401, content={"detail": "Invalid authorization scheme"}
            )
    except ValueError as e:
        return JSONResponse(status_code=401, content={"detail": str(e)})

    try:
        user_id = await decode_token_to_user_id(
            token_value, None
        )  # Не передаем HTTPException
    except Exception as e:
        return JSONResponse(
            status_code=401, content={"detail": f"Failed to decode token: {str(e)}"}
        )

    if not await redis_client.check_token(user_id):
        return JSONResponse(status_code=401, content={"detail": "Your token not found"})
    if await redis_client.check_blacklist(user_id):
        return JSONResponse(
            status_code=401, content={"detail": "Your token is revoked"}
        )

    async for session in get_session():
        user = await user_repo.get_user_by_user_id(user_id, session)
        if not user:
            return JSONResponse(status_code=401, content={"detail": "User not found"})

    request.state.user = user
    return await call_next(request)
