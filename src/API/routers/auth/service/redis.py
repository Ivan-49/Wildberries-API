from redis_client import RedisClient

redis = RedisClient()


async def check_token_in_blacklist(user_id: int) -> bool:
    return await redis.check_blacklist(user_id)


async def delete_token(user_id: int) -> None:
    await redis.delete_token_from_blacklist(user_id)
    await redis.delete_token(user_id)
    return None
