"""Load PDF pages and split within pages; OCR is not performed."""
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_split_documents(directory_path: str):
    directory = Path(directory_path)
    if not directory.is_dir():
        raise FileNotFoundError(f"PDF directory does not exist: {directory}")
    pages = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() == ".pdf":
            for page in PyMuPDFLoader(str(path)).load():
                # Portable IDs when the project moves between host and container.
                page.metadata["source"] = path.relative_to(directory).as_posix()
                pages.append(page)
    return RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=150, separators=["\n\n", "\n", " ", ""],
    ).split_documents(pages)
