from dotenv import load_dotenv
import os
import asyncio
import aioredis

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")


class RedisClient:
    def __init__(self, url=f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True):
        self.redis = aioredis.from_url(url, decode_responses=decode_responses)

    async def save_token(self, user_id, jwt_token, ttl):
        try:
            if type(ttl) != int:
                ttl = int(ttl)
            await self.redis.set(f"token-{user_id}", jwt_token, ex=ttl)
            print(f"Токен сохранён: {jwt_token} для пользователя {user_id} с TTL {ttl}")
        except TypeError as e:
            print(f"Ошибка сохранения токена: {e}")

    async def get_token(self, user_id):
        return await self.redis.get(f"token-{user_id}")

    async def check_token(self, user_id):
        return await self.redis.exists(f"token-{user_id}")

    async def delete_token(self, user_id):
        await self.redis.delete(f"token-{user_id}")

    async def add_to_blacklist(self, user_id, ttl: int = 3600):
        await self.redis.set(f"blacklist-{user_id}", "revoked", ex=ttl)

    async def delete_token_from_blacklist(self, user_id):
        await self.redis.delete(f"blacklist-{user_id}")

    async def check_blacklist(self, user_id):
        return await self.redis.exists(f"blacklist-{user_id}")

    async def close_connection(self):
        await self.redis.close()
        await self.redis.wait_closed()
