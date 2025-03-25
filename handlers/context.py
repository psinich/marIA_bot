import os
import shutil
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from keyboards.main_menu import main_menu

from config import BASE_STORAGE_DIR, MAX_CONTEXTS

router = Router()

class ContextStates(StatesGroup):
    naming = State()

# Проверка количества существующих контекстов
def get_user_contexts(user_id: int):
    user_dir = os.path.join(BASE_STORAGE_DIR, str(user_id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return [name for name in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, name))]

# Команда для создания нового контекста
@router.message(F.text.lower() == "📂 создать контекст")
async def create_context(message: Message, state: FSMContext):
    user_id = message.from_user.id
    context = get_user_contexts(user_id)

    if len(context) >= MAX_CONTEXTS:
        await message.answer("Вы достигли максимального количества контекстов")
        return

    await message.answer("Введите название нового контекста:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ContextStates.naming)

# Обработка ввода названия контекста
@router.message(ContextStates.naming)
async def save_context_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    context_name = message.text.strip()

    user_dir = os.path.join(BASE_STORAGE_DIR, str(user_id))
    context_path = os.path.join(user_dir, context_name)

    storage_path = os.path.join(context_path, "storage")
    documents_path = os.path.join(context_path, "documents")

    if os.path.exists(context_path):
        await message.answer("Контекст с таким названием уже существует. Попробуйте другое.")
        return

    os.makedirs(storage_path)
    os.makedirs(documents_path)
    await state.clear()

    await message.answer(f"Контекст '{context_name}' создан!", reply_markup=main_menu)


# Команда для отображения списка контекстов
@router.message(F.text.lower() == "📋 список контекстов")
async def list_contexts(message: Message):
    user_id = message.from_user.id
    contexts = get_user_contexts(user_id)
    if not contexts:
        await message.answer("У вас пока нет созданных контекстов.")
        return

    keyboard = InlineKeyboardBuilder()
    for context in contexts:
        keyboard.button(text=context, callback_data=f"select_{context}")

    await message.answer("Ваши контексты:", reply_markup=keyboard.as_markup())

@router.callback_query(F.data.startswith("select_"))
async def select_context(callback: CallbackQuery, state: FSMContext):
    context_name = callback.data.split("_", 1)[1]
    await state.update_data(current_context=context_name) # сохранение текущего контекста в состоянии

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Задать вопрос")],
                  [KeyboardButton(text="Загрузить документы")],
                  [KeyboardButton(text="Удалить документы")],
                  [KeyboardButton(text="Просмотреть документы")],
                  [KeyboardButton(text="Меню")]],
        resize_keyboard=True
    )

    await callback.message.answer(f"Вы выбрали контекст: {context_name}", reply_markup=keyboard)

# Удаление контекста
@router.message(F.text.lower() == "🗑 удалить контекст")
async def delete_context(message: Message, state: FSMContext):
    user_id = message.from_user.id
    contexts = get_user_contexts(user_id)

    if not contexts:
        await message.answer("У вас нет созданных контекстов.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=context, callback_data=f"delete_ctx_{context}")]
            for context in contexts
        ]
    )

    await message.answer("Выберите контекст, который хотите удалить:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("delete_ctx_"))
async def confirm_delete_context(callback: CallbackQuery, state: FSMContext):
    context_name = callback.data.replace("delete_ctx_", "", 1)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_ctx_{context_name}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")]
        ]
    )

    # Удаляем предыдущее сообщение с кнопкой (если возможно)
    try:
        await callback.message.delete()
    except Exception:
        pass  # Если сообщение нельзя удалить, просто игнорируем

    # Отправляем новое сообщение
    await callback.message.answer(
        f"Вы уверены, что хотите удалить контекст '{context_name}'? Это действие необратимо!",
        reply_markup=keyboard
    )


# Обработка подтверждения удаления
@router.callback_query(F.data.startswith("confirm_delete_ctx_"))
async def delete_context_confirmed(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    context_name = callback.data.split("_", 3)[3]
    context_path = os.path.join(BASE_STORAGE_DIR, str(user_id), context_name)

    try:
        await callback.message.delete()
    except Exception:
        pass  # Если сообщение нельзя удалить, просто игнорируем

    if os.path.exists(context_path):
        shutil.rmtree(context_path)  # Полностью удаляем папку контекста
        await callback.message.answer(f"✅ Контекст '{context_name}' был успешно удален.")
    else:
        await callback.message.answer(f"⚠ Контекст '{context_name}' уже не существует.")

    await callback.answer()  # Закрыть всплывающее уведомление


# Отмена удаления
@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    await callback.message.answer("Удаление контекста отменено.")
    await callback.answer()
