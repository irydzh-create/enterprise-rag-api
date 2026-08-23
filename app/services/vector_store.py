import os
import sys

# # Add root directory to Python path / Добавляем корневую папку проекта в пути Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.services.document_loader import load_documents

# # Absolute path to project root and database / Абсолютные пути к проекту и базе данных
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# # Load free local embeddings model / Загружаем бесплатную локальную модель эмбеддингов
def get_huggingface_embeddings():
    return HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")

# # Create vectors from documents and save to Chroma DB / Создаем векторы из документов и сохраняем в БД Chroma
def create_vector_store(documents):
    embeddings = get_huggingface_embeddings()

    print("Создаю векторы локально и сохраняю в базу данных (Chroma)... / Creating local vectors and saving to Chroma...")

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )

    print(f" База данных успешно создана / Database successfully created: {CHROMA_PERSIST_DIR}")
    return vector_store

# # Load existing database for search / Загружаем существующую базу данных для поиска
def get_vector_store():
    if not os.path.exists(CHROMA_PERSIST_DIR):
        print(f" База данных не найдена / Database not found: {CHROMA_PERSIST_DIR}")
        return None

    embeddings = get_huggingface_embeddings()

    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    return vector_store

# # Execution block / Блок запуска
if __name__ == "__main__":
    docs_dir = os.path.join(BASE_DIR, "data", "docs")

    print("Начинаем обработку документов... / Starting document processing...")
    documents = load_documents(docs_dir)

    if documents:
        create_vector_store(documents)
    else:
        print("Внимание: Документы не найдены. Проверьте папку data/docs / Warning: Documents not found.")