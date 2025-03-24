from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📂 Создать контекст")],
        [KeyboardButton(text="📋 Список контекстов")],
        [KeyboardButton(text="🗑 Удалить контекст")],
        [KeyboardButton(text="ℹ О боте")]
    ],
    resize_keyboard=True
)
