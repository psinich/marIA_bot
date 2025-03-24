from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_context_menu(contexts: list) -> ReplyKeyboardMarkup:
    """
    Генерирует меню с контекстами.
    :param contexts: Список названий контекстов.
    :return: Клавиатура с кнопками контекстов.
    """
    buttons = [[KeyboardButton(text=context)] for context in contexts]
    buttons.append([KeyboardButton(text="🔙 В главное меню")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
