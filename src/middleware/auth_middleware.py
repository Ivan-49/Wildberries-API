from fastapi import Request
from database import get_session
from redis_client import RedisClient
from fastapi.responses import JSONResponse
from loguru import logger

redis_client = RedisClient()


@logger.catch
async def auth_middleware(request: Request, call_next):
    from routers.auth.service.security import decode_token_to_user_id
    from routers.auth.service.repository import UserRepository

    user_repo = UserRepository()
    excluded_urls = [
        "/",
        "/api/v1/third-party/wildberries/get-product-details",
        "/api/v1/auth/auth-by-username",
        "/api/v1/auth/auth-by-user-id",
        "/api/v1/auth/register",
        "/docs",
        "/openapi.json",
    ]
    if any(request.url.path.startswith(prefix) for prefix in excluded_urls):
        return await call_next(request)
    
    token = request.headers.get("Authorization")
    if not token:
        logger.error("Token not found")
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    try:
        # Проверяем формат токена
        scheme, token_value = token.split(" ", 1)
        if scheme.lower() != "bearer":
            logger.error("Invalid authorization scheme")
            return JSONResponse(
                status_code=401, content={"detail": "Invalid authorization scheme"}
            )
    except ValueError as e:
        logger.error(f"Invalid token format: {str(e)}")
        return JSONResponse(status_code=401, content={"detail": str(e)})

    try:
        user_id = await decode_token_to_user_id(
            token_value, None
        )  # Не передаем HTTPException
    except Exception as e:
        logger.error(f"Failed to decode token: {str(e)}")
        return JSONResponse(
            status_code=401, content={"detail": f"Failed to decode token: {str(e)}"}
        )

    if not await redis_client.check_token(user_id):
        logger.error(f"Token user {user_id} not found")
        return JSONResponse(status_code=401, content={"detail": "Your token not found"})
    if await redis_client.check_blacklist(user_id):
        logger.error(f"Token user {user_id} is revoked")
        return JSONResponse(
            status_code=401, content={"detail": "Your token is revoked"}
        )

    async for session in get_session():
        user = await user_repo.get_user_by_user_id(user_id, session)
        if not user:
            logger.error(f"User not {user_id} found")
            return JSONResponse(status_code=401, content={"detail": "User not found"})

    request.state.user = user
    logger.info(f"User {user_id} authorized")
    return await call_next(request)
