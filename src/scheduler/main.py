"""
Основной модуль планировщика задач.
Обрабатывает периодический сбор данных о товарах.
"""

import asyncio
from loguru import logger
from datetime import datetime, timedelta
from scheduler.tasks import add_product_in_db
import os
from dotenv import load_dotenv

INTERVAL_IN_MINUTES = int(os.getenv("INTERVAL_IN_MINUTES"))


async def update_timer(minutes: int):
    """
    Обновляет таймер и выводит оставшееся время.

    Args:
        minutes: Количество минут до следующего запуска
    """
    remaining_seconds = minutes * 60
    while remaining_seconds > 0:
        if remaining_seconds > 0:
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            logger.debug(
                f"До следующего сбора данных осталось: {minutes} мин {seconds} сек"
            )

        await asyncio.sleep(min(10, remaining_seconds))
        remaining_seconds -= 10

        if remaining_seconds <= 0:
            logger.debug("Начинаем новый сбор данных...")


async def main_scheduler():
    """
    Основная функция планировщика.
    Запускает периодический сбор данных.
    """
    while True:
        try:
            # Рассчитываем время следующего запуска
            next_run = datetime.now() + timedelta(minutes=INTERVAL_IN_MINUTES)
            logger.info(
                f"Следующий сбор данных в {next_run.strftime('%H:%M:%S')} "
                f"(через {INTERVAL_IN_MINUTES} минут)"
            )

            # Проверяем, нужно ли ждать таймер (если текущее время не кратно интервалу)
            current_minute = datetime.now().minute
            if current_minute % INTERVAL_IN_MINUTES != 0:
                # При первом запуске сначала ждем таймер
                await update_timer(INTERVAL_IN_MINUTES)
                await add_product_in_db()
            else:
                # При последующих запусках работаем параллельно
                timer_task = asyncio.create_task(update_timer(INTERVAL_IN_MINUTES))
                data_task = asyncio.create_task(add_product_in_db())
                await asyncio.gather(timer_task, data_task)

        except Exception as e:
            logger.error(f"Ошибка в планировщике: {str(e)}")
            # Ждем 5 минут перед повторной попыткой
            await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(main_scheduler())
