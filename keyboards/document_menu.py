from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

document_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Загрузить документы")],
        [KeyboardButton(text="Удалить документ")],
        [KeyboardButton(text="Просмотреть базу знаний")],
        [KeyboardButton(text="🔙 Вернуться к выбору контекста")]
    ],
    resize_keyboard=True
)
