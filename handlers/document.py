import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Document
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import datetime

from config import BASE_STORAGE_DIR

router = Router()

class DocumentStates(StatesGroup):
    waiting_for_document = State()
    choosing_document_to_delete = State()

# Получение списка документов в контексте
def get_documents_list(user_id: int, context_name: str):
    context_path = os.path.join(BASE_STORAGE_DIR, str(user_id), context_name)
    if not os.path.exists(context_path):
        return []

    documents = []
    for file_name in os.listdir(context_path):
        file_path = os.path.join(context_path, file_name)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path) // 1024 # Размер в КБ
            file_extension = os.path.splitext(file_name)[1]
            file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M")

            documents.append({
                "name": file_name,
                "extension": file_extension,
                "size_kb": file_size,
                "uploaded_at": file_mtime
            })

    return documents

# Команда для загрузки документа
@router.message(F.text.lower() == "загрузить документы")
async def upload_document_request(message: Message, state: FSMContext):
    user_data = await state.get_data()
    current_context = user_data.get("current_context")

    if not current_context:
        await message.answer("Сначала выберите контекст в разделе 'Список контекстов'.")
        return

    await message.answer("Отправьте документ, который хотите загрузить в контекст.")
    await state.set_state(DocumentStates.waiting_for_document)

# Хендлер обработки загруженного документа
@router.message(DocumentStates.waiting_for_document, F.document)
async def save_uploaded_document(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    current_context = user_data.get('current_context')

    if not current_context:
        await message.answer("Ошибка: не найден текущий контекст. Выберите контекст заново.")
        return

    document = message.document
    user_documents_path = os.path.join(BASE_STORAGE_DIR, str(user_id), current_context, "documents")

    if not os.path.exists(user_documents_path):
        os.makedirs(user_documents_path)

    sanitized_filename = document.file_name.replace(' ', '_')
    document_path = os.path.join(user_documents_path, sanitized_filename)

    # Загрузка документа в ФС
    file = await message.bot.get_file(document.file_id)
    await message.bot.download_file(file.file_path, document_path)

    await message.answer(f"✅ Документ '{sanitized_filename}' успешно загружен в контекст '{current_context}'!")

# Команда для выбора документа для удаления
@router.message(F.text.lower() == "удалить документы")
async def ask_document_for_deletion(message: Message, state: FSMContext):
    user_data = await state.get_data()
    current_context = user_data.get("current_context")

    if not current_context:
        await message.answer("Сначала выберите контекст в разделе 'Список контекстов'.")
        return

    user_id = message.from_user.id
    documents = get_documents_list(user_id, current_context)

    if not documents:
        await message.answer(f"В контексте '{current_context}' нет документов для удаления.")
        return

    keyboard = InlineKeyboardBuilder()
    for doc in documents:
        keyboard.button(text=doc['name'], callback_data=f"delete_{doc['name']}")
    keyboard.adjust(1)

    await message.answer("Выберите документ, для удаления:", reply_markup=keyboard.as_markup())

# Хендлер для подтверждения удаления
@router.callback_query(F.data.startswith("delete_"))
async def confirm_deletion(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    current_context = user_data.get("current_context")
    document_name = callback.data.split("_", 1)[1]

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Да, удалить", callback_data=f"confirm_delete_{document_name}")
    keyboard.button(text="❌ Отмена", callback_data="cancel_delete")

    await callback.message.answer(f"Вы уверены, что хотите удалить '{document_name}'?", reply_markup=keyboard.as_markup())

# Хендлер для удаления файла
@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_document(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    current_context = user_data.get("current_context")
    document_name = callback.data.split("_", 2)[2]

    user_id = callback.from_user.id
    document_path = os.path.join(BASE_STORAGE_DIR, str(user_id), current_context, document_name)

    if os.path.exists(document_path):
        os.remove(document_path)
        await callback.message.answer(f"✅ Файл '{document_name}' удалён.")
    else:
        await callback.message.answer(f"⚠ Файл '{document_name}' уже отсутствует.")

# Хендлер для отмены удаления
@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    await callback.message.answer("Удаление отменено.")

# Команда для просмотра загруженных документов
@router.message(F.text.lower() == "просмотреть документы")
async def list_documents(message: Message, state: FSMContext):
    user_data = await state.get_data()
    current_context = user_data.get("current_context")

    if not current_context:
        await message.answer("Сначала выберите контекст в разделе 'Список контекстов'.")
        return

    user_id = message.from_user.id
    documents = get_documents_list(user_id, current_context)

    if len(documents) == 0:
        await message.answer(f"В контексте '{current_context}' пока нет загруженных документов.")
        return

    doc_list_message = f"📂 **Документы в контексте '{current_context}':**\n\n"
    for doc in documents:
        doc_list_message += (f"📄 **{doc['name']}**\n"
                             f"  ├ 🗂 Формат: {doc['extension']}\n"
                             f"  ├ 📏 Размер: {doc['size_kb']} КБ\n"
                             f"  └ 🕒 Дата загрузки: {doc['uploaded_at']}\n\n")

    await message.answer(doc_list_message)
