import os
import sys

# Добавляем корневую папку проекта в пути Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.vector_store import get_vector_store


def search_documents(query: str, k: int = 3):
    """
    Ищет в базе данных фрагменты текста, которые больше всего похожи на запрос пользователя по смыслу.
    k - количество возвращаемых фрагментов.
    """
    # Подключаемся к нашей созданной базе данных
    vector_store = get_vector_store()

    if not vector_store:
        print("❌ База данных пуста или не найдена.")
        return None

    print(f"\n🔍 Ищу информацию по запросу: '{query}'...\n")

    # Делаем смысловой поиск (similarity search)
    results = vector_store.similarity_search(query, k=k)

    # Красиво выводим результаты на экран
    for i, doc in enumerate(results):
        print(f"--- Найденный фрагмент {i + 1} ---")
        # Выводим первые 300 символов найденного куска, чтобы не засорять экран
        print(f"{doc.page_content[:300]}...\n")

    return results


# Блок для самостоятельной проверки
if __name__ == "__main__":
    # Я взял вопрос из вашего текста "Conditional Statements"
    test_query = "Что такое Conditional Statements и основы программирования?"
    search_documents(test_query)