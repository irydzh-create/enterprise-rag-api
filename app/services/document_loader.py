import os
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader


def load_documents(directory_path: str):
    """
    Загружает все PDF-документы из указанной папки с помощью продвинутого парсера PyMuPDF.
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Папка {directory_path} не найдена.")

    print(f"📂 Сканирую папку: {directory_path} (использую продвинутый парсер PyMuPDF)")

    # Используем DirectoryLoader, который сам найдет все .pdf файлы и применит к ним PyMuPDFLoader
    loader = DirectoryLoader(
        directory_path,
        glob="*.pdf",  # Ищем только PDF-файлы, игнорируем системные и скрытые
        loader_cls=PyMuPDFLoader
    )

    documents = loader.load()

    print(f"✅ Успешно загружено страниц из всех PDF: {len(documents)}")
    return documents


# Блок для проверки
if __name__ == "__main__":
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/docs'))
    docs = load_documents(docs_dir)
    if docs:
        print(f"Пример текста из первого документа:\n{docs[0].page_content[:200]}...")