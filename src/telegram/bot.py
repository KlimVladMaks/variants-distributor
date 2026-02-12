from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from ..config import TG_BOT_TOKEN
from .handlers.teacher import router as teacher_router
from .handlers.common import router as common_router

async def start_bot():
    """Функция для запуска Telegram-бота"""
    bot = Bot(token=TG_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(teacher_router)
    dp.include_router(common_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
