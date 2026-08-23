import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader


def load_documents(directory_path: str):
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Папка {directory_path} не найдена.")

    print(f"Загружаю PDF-файлы из: {directory_path}")

    loader = DirectoryLoader(
        directory_path,
        glob="*.pdf",
        loader_cls=PyMuPDFLoader
    )

    documents = loader.load()
    print(f"Загружено страниц: {len(documents)}")

    return documents


if __name__ == "__main__":
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/docs'))
    docs = load_documents(docs_dir)

    if docs:
        print(f"Пример текста: {docs[0].page_content[:150]}...")