import os
from typing import List

from config import BASE_STORAGE_DIR

class DocumentManager:
    @staticmethod
    def get_documents(user_id: int, context_name: str) -> List[str]:
        """
        Возвращает список документов в указанном контексте.
        """
        context_path = os.path.join(BASE_STORAGE_DIR, str(user_id), context_name)
        return os.listdir(context_path) if os.path.exists(context_path) else []

    @staticmethod
    def save_document(user_id: int, context_name: str, file_name: str, file_data: bytes) -> bool:
        """
        Сохраняет документ в указанном контексте.
        Возвращает True, если успешно сохранён, иначе False.
        """
        context_path = os.path.join(BASE_STORAGE_DIR, str(user_id), context_name)

        if not os.path.exists(context_path):
            return False  # Контекст не существует

        file_path = os.path.join(context_path, file_name)
        try:
            with open(file_path, "wb") as file:
                file.write(file_data)
            return True
        except Exception:
            return False

    @staticmethod
    def delete_document(user_id: int, context_name: str, file_name: str) -> bool:
        """
        Удаляет указанный документ из контекста.
        Возвращает True, если успешно удалён, иначе False.
        """
        file_path = os.path.join(BASE_STORAGE_DIR, str(user_id), context_name, file_name)

        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False  # Файл не найден
