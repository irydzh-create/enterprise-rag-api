import os
import sys

# # Add root directory to Python path / Добавляем корневую папку проекта в пути Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.vector_store import get_vector_store

# # Function to search documents by similarity / Функция для поиска документов по смыслу
def search_documents(query: str, k: int = 3):
    # # Get vector store connection / Подключаемся к базе данных
    vector_store = get_vector_store()

    if not vector_store:
        print("❌ База данных пуста или не найдена. / Database is empty or not found.")
        return None

    print(f"\n🔍 Ищу информацию по запросу / Searching for: '{query}'...\n")

    # # Perform similarity search / Делаем смысловой поиск
    results = vector_store.similarity_search(query, k=k)

    # # Print results nicely / Выводим результаты на экран
    for i, doc in enumerate(results):
        print(f"--- Найденный фрагмент / Found chunk {i + 1} ---")
        print(f"{doc.page_content[:300]}...\n")

    return results

# # Verification block / Блок для самостоятельной проверки
if __name__ == "__main__":
    test_query = "Что такое Conditional Statements и основы программирования?"
    search_documents(test_query)