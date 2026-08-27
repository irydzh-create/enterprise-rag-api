# Enterprise Document Intelligence & Local RAG API 🛡️
# Корпоративная система интеллектуальной работы с документами и локальный RAG API

A GDPR-compliant, privacy-first Retrieval-Augmented Generation (RAG) backend built with **FastAPI**, **LangChain**, **ChromaDB**, and local LLMs via **Ollama** (`llama3.2`). Designed for enterprise use cases where document security and data privacy are paramount.
## Key Features / Основные возможности
- **GDPR / DSGVO Compliant / Соответствие GDPR:** Local embeddings (`all-MiniLM-L6-v2`) and local LLM execution via Ollama ensure confidential documents never leave the internal network.
- **RESTful API:** Clean interface powered by FastAPI with auto-generated Interactive OpenAPI (Swagger) documentation.
- **Document Processing / Обработка документов:** Efficient PDF parsing, text chunking, and vector persistence using ChromaDB.
- **Contextual QA / Контекстный поиск:** Semantic similarity search with precision-driven prompt templates for corporate document queries.
- **Telegram Bot Integration / Интеграция с Telegram-ботом:** Asynchronous bot (`aiogram 3.x`) acting as a conversational interface for both document Q&A and AI-powered code reviews (`/review`).
- **AI Code Review / ИИ Код-ревью:** Specialized endpoint analyzing Python code snippets via local `llama3.2` for potential bugs, PEP 8 compliance, and optimizations.

## Tech Stack / Технологический стек
- **Framework / Фреймворк:** Python 3.10+, FastAPI, Uvicorn
- **Orchestration / Оркестрация:** LangChain
- **Vector Store / Векторная база:** ChromaDB
- **Embeddings / Эмбеддинги:** HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
- **LLM Engine / Модель LLM:** Ollama (`llama3.2`)
- **Bot Interface / Интерфейс бота:** aiogram 3.x

## Architecture & Data Flow / Архитектура и поток данных
1. **Document Ingestion / Загрузка документов:** PDF files are loaded and split into semantic chunks.
2. **Vector Embedding / Векторизация:** Text chunks are vectorized locally using HuggingFace models.
3. **Storage / Хранение:** Embeddings are persisted in a local ChromaDB instance.
4. **Retrieval & Generation / Поиск и генерация:** User queries hit the `/ask` endpoint, trigger a similarity search in ChromaDB, and pass retrieved context to local `llama3.2` for response generation.

## Project Structure / Структура проекта
```text
enterprise-rag-api/
├── app/
│   ├── api/          # API endpoints and route handlers / Эндпоинты и обработчики
│   ├── core/         # Environment configurations & settings / Конфигурация и настройки
│   └── services/     # RAG pipeline & generators / Конвейер RAG и генераторы
├── data/             # Local vector store & PDF inputs (git-ignored) / База векторов и документы
├── main.py           # FastAPI entrypoint / Точка входа FastAPI
├── telegram_bot.py   # Asynchronous Telegram bot interface / Асинхронный Telegram-бот
├── requirements.txt  # Project dependencies / Зависимости проекта
└── .env              # Environment secrets (git-ignored) / Секретные ключи