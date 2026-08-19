import os
import sys

# Добавляем корневую папку проекта в пути Python, чтобы импорты из app работали при прямом запуске
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from langchain_community.document_loaders import PyPDFLoader
# Тот самый новый импорт, который мы добавили для работы с базой данных
from app.services.vector_store import create_vector_store


def load_and_split_pdf(file_path: str):
    """
    Загружает PDF-файл и разбивает его на страницы/блоки (chunks).
    Это необходимо, так как длинные документы не помещаются в контекст LLM целиком.
    """
    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден по пути: {file_path}")

    # Инициализируем загрузчик LangChain
    loader = PyPDFLoader(file_path)

    # Загружаем и разбиваем документ
    pages = loader.load_and_split()

    print(f"✅ Документ успешно загружен. Разбито на {len(pages)} фрагментов (страниц).")
    return pages


# Блок для проверки (работает только если запустить этот файл напрямую)
if __name__ == "__main__":
    # Укажите путь к вашему PDF-файлу в папке data/
    test_file_path = "../../data/sample.pdf"

    try:
        documents = load_and_split_pdf(test_file_path)
        if documents:
            print(f"Первые 200 символов текста:\n{documents[0].page_content[:200]}...")

            # --- НОВЫЙ ШАГ: Создаем векторы ---
            vector_store = create_vector_store(documents)
            print("Готово! Данные готовы к поиску.")

    except Exception as e:
        print(f"❌ Ошибка: {e}")