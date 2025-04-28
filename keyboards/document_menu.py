from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

document_menu = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Задать вопрос")],
                  [KeyboardButton(text="Загрузить документы")],
                  [KeyboardButton(text="Удалить документы")],
                  [KeyboardButton(text="Просмотреть документы")],
                  [KeyboardButton(text="Меню")]],
        resize_keyboard=True
    )
