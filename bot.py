import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers.start import router as start_router  # Импортируем router из start.py
from handlers.context import router as context_router  # Импортируем router из context.py
from handlers.document import router as document_router  # Импортируем router из document.py
from handlers.question import router as question_router  # Импортируем router из question.py
from handlers.main_menu import router as main_menu_router # Импортируем router из main_menu.py

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация диспетчера
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация обработчиков
    dp.include_routers(start_router,
                       context_router,
                       document_router,
                       question_router,
                       main_menu_router)

    # Установка команд для бота
    commands = [
        BotCommand(command="start", description="Запустить бота"),
    ]
    await bot.set_my_commands(commands)

    # Начало опроса
    await dp.start_polling(bot)

    # Закрытие сессии бота
    await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
