import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BASE_STORAGE_DIR

router = Router()

class QuestionStates(StatesGroup):
    choosing_context = State()
    asking_question = State()

# Получение списка контекстов пользователя
def get_user_contexts(user_id: int):
    user_dir = os.path.join(BASE_STORAGE_DIR, str(user_id))
    return [name for name in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, name))]

# Команда для начала процесса вопроса
@router.message(Command("ask_question"))
async def choose_context(message: Message, state: FSMContext):
    user_id = message.from_user.id
    contexts = get_user_contexts(user_id)

    if not contexts:
        await message.answer("У вас нет созданных контекстов!")
        return

    keyboard = InlineKeyboardBuilder()
    for context in contexts:
        keyboard.button(text=context, callback_data=f"choose_{context}")

    await message.answer("Выберите контекст для вопроса:", reply_markup=keyboard.as_markup())
    await state.set_state(QuestionStates.choosing_context)

@router.callback_query(F.data.startswith("choose_"))
async def ask_question(callback: CallbackQuery, state: FSMContext):
    context_name = callback.data.split("_",1)[1]
    await state.update_data(context=context_name)

    await callback.message.answer(f"Вы выбрали контекст '{context_name}'. Теперь задайте ваш вопрос.")
    await state.set_state(QuestionStates.asking_question)
    await callback.answer()

@router.message(QuestionStates.asking_question)
async def process_question(message: Message, state: FSMContext):
    user_data = await state.get_data()
    context_name = user_data.get("context")
    user_question = message.text

    # Имитация, заменить
    responce = f"ваш вопрос: {user_question}\nОтвет (заглушка): Данные будут обработаны системой LightRAG."

    await message.answer(responce)
    await state.clear()
