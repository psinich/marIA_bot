import os
import logging
from aiogram import Router, F 
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from lightrag import QueryParam

from moduls.lightrag_module import build_rag
from config import BASE_STORAGE_DIR
from keyboards.document_menu import document_menu
from keyboards.main_menu import main_menu

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

router = Router()

VALID_QUERY_MODES = ["naive", "local", "global", "hybrid", "mix"]

back_keyboard = ReplyKeyboardMarkup(
  keyboard=[[KeyboardButton(text="⬅️ Назад")]],
  resize_keyboard=True
)

class QuestionStates(StatesGroup):
  asking_questions_in_context = State()

@router.message(F.text.lower() == "задать вопрос")
async def ask_for_question(message: Message, state: FSMContext):
  user_data = await state.get_data()
  current_context = user_data.get("current_context")

  if not current_context:
    await message.answer("❗️ Сначала выберите контекст в разделе '📋 Список контекстов'.")
    return
  
  await message.answer(
    f"🔹 Вы находитесь в контексте: **{current_context}**\n\n"
    f"Введите ваш вопрос и режим через разделитель ' | '.\n\n"
    f"ВАЖНО: Пожалуйста, не используйте символ ' | ' в запросе, он используется ТОЛЬКО для разделения запроса и режима."
    f"**Формат:** `Ваш вопрос | режим`\n\n"
    f"**Доступные режимы:**\n"
    f" • `naive` - Простой поиск по релевантности (используется только векторное хранилище).\n"
    f" • `local` - Использует локальные сущности и связи графа знаний.\n"
    f" • `global` - Использует глобальные сущности и связи  графа знаний.\n"
    f" • `hybrid` - Комбинация local и global.\n\n"
    f" • `mix` - Комбинация векторного хранилища и графа знаний.\n\n"
    f"*Пример:* `Каковы основные выводы документа? | naive`",
    reply_markup=back_keyboard, # Убираем клавиатуру document_menu
    parse_mode="Markdown" # Используем Markdown для форматирования
  )
  await state.set_state(QuestionStates.asking_questions_in_context)


@router.message(QuestionStates.asking_questions_in_context)
async def process_rag_question(message: Message, state: FSMContext):
  user_data = await state.get_data()
  current_context = user_data.get("current_context")
  user_id = message.from_user.id
  if message.text == "⬅️ Назад":
         await handle_back_button(message, state) # Можно вызвать другой хендлер
         return

  if not current_context:
    await message.answer("❗️ Ошибка: не найден текущий контекст. Пожалуйста, выберите его снова.")
    await state.clear()
    await message.answer("Возврат в главное меню.", reply_markup=main_menu)
    return

  user_input = message.text.strip()
  parts = user_input.split("|", 1)

  if len(parts) != 2:
    await message.answer(
      f"❗️ **Ошибка формата.** Пожалуйста, введите вопрос и режим, разделенные ' | ', или нажмите кнопку '⬅️ Назад'\n\n"
      f"**Пример:** `Текст вашего вопроса | naive`"
    )
    return

  question_text = parts[0].strip()
  query_mode = parts[1].strip().lower()

  if not question_text:
    await message.answer("❗️ Пожалуйста, введите текст вопроса.")
    return

  if query_mode not in VALID_QUERY_MODES:
    await message.answer(
      f"❗️ **Неверный режим:** `{query_mode}`.\n\n"
      f"Допустимые режимы: {', '.join(VALID_QUERY_MODES)}."
    )
    return

  await message.answer("⏳ Обработка вашего запроса...")
  logging.info(f"User {user_id} asked in context '{current_context}': '{question_text}' with mode '{query_mode}'")

  storage_dir = os.path.join(BASE_STORAGE_DIR, str(user_id), current_context, "storage")
  rag = None
  try:
    rag = await build_rag(storage_dir)
    logging.info(f"RAG initialized seccessfuly for context '{current_context}' for user {user_id}")
  except Exception as e:
    logging.exception(f"Failed to initialize RAG for context '{current_context}' (User: {user_id}: {e})")
    await message.answer("❌ Не удалось инициализировать RAG для этого контекста. Попробуйте позже.")
    await state.clear()
    await message.answer("Запрос отменен.", reply_markup=document_menu)
    return

  try:
    response = await rag.aquery(question_text, param=QueryParam(mode=query_mode))
    if response:
      logging.info(f"Succsessfuly got answer for user {user_id} in context '{current_context}'")
      await message.answer(f"💡 **Ответ:**\n\n{response}")
    else:
      logging.warning(f"RAG returned no answer or unexpected structure for user {user_id} in context '{current_context}'. Response: {response}")
      await message.answer("😕 Не удалось получить структурированный ответ от системы. Возможно, информация отсутствует или произошла внутренняя ошибка.")

  except Exception as e:
    logging.exception(f"Error during RAG query for context '{current_context}' (User: {user_id}): {e}")
    await message.answer("❌ Произошла ошибка во время обработки вашего запроса к RAG.")
  
  finally:
    await message.answer("Введите следующий вопрос или нажмите '⬅️ Назад'.")

@router.message(QuestionStates.asking_questions_in_context, F.text.lower() == "⬅️ назад")
async def handle_back_button(message: Message, state: FSMContext):
    user_data = await state.get_data()
    current_context = user_data.get("current_context", "текущий") # Получаем контекст для сообщения

    logging.info(f"User {message.from_user.id} exited question mode for context '{current_context}'.")
    #await state.clear() # Очищаем состояние
    await message.answer(
        f"Вы вышли из режима задания вопросов для контекста '{current_context}'.",
        reply_markup=document_menu # Возвращаем клавиатуру меню документов
    )








