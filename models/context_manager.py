import os
from config import BASE_STORAGE_DIR, MAX_CONTEXTS

class ContextManager:
    @staticmethod
    def get_user_contexts(user_id: int) -> list:
        """Возвращает список контекстов пользователя."""
        user_dir = os.path.join(BASE_STORAGE_DIR, str(user_id))
        return [name for name in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, name))] if os.path.exists(user_dir) else []

    @staticmethod
    def create_context(user_id: int, context_name: str) -> bool:
        """
        Создаёт новый контекст.
        Возвращает True, если успешно создан, иначе False.
        """
        user_dir = os.path.join(BASE_STORAGE_DIR, str(user_id))
        context_path = os.path.join(user_dir, context_name)

        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        if len(ContextManager.get_user_contexts(user_id)) >= MAX_CONTEXTS:
            return False  # Достигнут лимит контекстов

        if not os.path.exists(context_path):
            os.makedirs(context_path)
            return True
        return False  # Контекст уже существует

    @staticmethod
    def delete_context(user_id: int, context_name: str) -> bool:
        """
        Удаляет контекст.
        Возвращает True, если успешно удалён, иначе False.
        """
        context_path = os.path.join(BASE_STORAGE_DIR, str(user_id), context_name)

        if os.path.exists(context_path):
            for root, dirs, files in os.walk(context_path, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(context_path)
            return True
        return False  # Контекст не найден
