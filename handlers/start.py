from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📂 Создать контекст")]],
        resize_keyboard=True
    )
    await message.answer("Привет! Я ваш консультант. Давайте начнем с создания контекста!", reply_markup=keyboard)
