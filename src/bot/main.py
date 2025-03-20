import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
import os
from dotenv import load_dotenv



load_dotenv()  # Загружаем переменные окружения

TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def process_start_command(message: types.Message):
    await message.answer("Hello!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
