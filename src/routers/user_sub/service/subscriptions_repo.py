from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func, text, desc
from schemas import ProductShema
from models import ProductModel, SubscribeModel
from loguru import logger


# TODO: сделать репозиторий для обработки подписок пользователей на товары
class SubscriptionsRepository: ...
