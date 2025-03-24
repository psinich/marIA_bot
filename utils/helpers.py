import os
import logging

# Настройка логирования
logging.basicConfig(
    filename="data/logs/bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def format_documents_list(documents: list) -> str:
    """
    Форматирует список документов в строку для отправки пользователю.
    """
    if not documents:
        return "Документы в данном контексте отсутствуют."

    formatted_list = "\n".join([f"{i+1}. {doc}" for i, doc in enumerate(documents)])
    return f"📂 Список документов:\n\n{formatted_list}"

def is_valid_context_name(name: str) -> bool:
    """
    Проверяет, является ли название контекста допустимым.
    """
    return name.isalnum() and len(name) <= 20

def log_error(error: str):
    """
    Логирует ошибку в файл.
    """
    logging.error(error)
