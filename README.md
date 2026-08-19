# Enterprise Document Intelligence & Local RAG API 🛡️

A GDPR-compliant, privacy-first Retrieval-Augmented Generation (RAG) backend built with **FastAPI**, **LangChain**, **ChromaDB**, and local LLMs via **Ollama** (`llama3.2`). Designed for enterprise use cases where document security and data privacy are paramount.

## Key Features
- **GDPR / DSGVO Compliant:** Local embeddings (`all-MiniLM-L6-v2`) and local LLM execution via Ollama ensure confidential documents never leave the internal network.
- **RESTful API:** Clean interface powered by FastAPI with auto-generated Interactive OpenAPI (Swagger) documentation.
- **Document Processing:** Efficient PDF parsing, text chunking, and vector persistence using ChromaDB.
- **Contextual QA:** Semantic similarity search with precision-driven prompt templates for corporate document queries.

## Tech Stack
- **Framework:** Python 3.10+, FastAPI, Uvicorn
- **Orchestration:** LangChain
- **Vector Store:** ChromaDB
- **Embeddings:** HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
- **LLM Engine:** Ollama (`llama3.2`)

## Architecture & Data Flow
1. **Document Ingestion:** PDF files are loaded and split into semantic chunks.
2. **Vector Embedding:** Text chunks are vectorized locally using HuggingFace models.
3. **Storage:** Embeddings are persisted in a local ChromaDB instance.
4. **Retrieval & Generation:** User queries hit the `/ask` endpoint, trigger a similarity search in ChromaDB, and pass retrieved context to local `llama3.2` for response generation.

## Project Structure
```text
enterprise-rag-api/
├── app/
│   ├── api/          # API endpoints and route handlers
│   ├── core/         # Environment configurations & settings
│   └── services/     # RAG pipeline: document loader, vector store, retriever, generator
├── data/             # Local vector store & PDF inputs (git-ignored)
├── main.py           # FastAPI entrypoint
├── requirements.txt  # Project dependencies
└── .env              # Environment secrets (git-ignored)