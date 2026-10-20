---
title: Enterprise RAG API
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---

# Enterprise Document Intelligence & Hybrid RAG API 🛡️

[![CI Pipeline](https://github.com/irydzh-create/enterprise-rag-api/actions/workflows/ci.yml/badge.svg)](https://github.com/irydzh-create/enterprise-rag-api/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)](https://www.docker.com/)

A locally operated Retrieval-Augmented Generation (RAG) backend engineered for enterprise document management. It features a two-stage **Hybrid Retrieval Pipeline** (ChromaDB + BM25 with Cross-Encoder reranking), local LLM inference via **Ollama** (`llama3.2`), and dual interfaces: a RESTful API and an asynchronous Telegram Bot.

---

## Key Features

* **Local Document Processing**: Fully on-premises pipeline using `paraphrase-multilingual-MiniLM-L12-v2` embeddings and local `llama3.2` execution via Ollama. Deployment configuration determines access and data protection; local inference alone does not establish GDPR compliance.
* **Two-Stage Hybrid Retrieval**: Combines semantic vector similarity (ChromaDB) with lexical keyword matching (BM25) and re-ranks candidates using a Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) for high precision.
* **Semantic Chunking**: Structured parsing using `PyMuPDF` and `RecursiveCharacterTextSplitter` (800-character chunks with 150-character overlap) within individual PDF pages.
* **Multi-Turn Conversational Memory**: Stateful dialog support for contextual follow-up questions.
* **Automated Code Review**: Dedicated `/code-review` endpoint and `/review` bot command leveraging low-temperature LLM prompts for static Python analysis and PEP 8 compliance checks.
* **Topic Summarization**: Automated extraction of structured executive summaries (`/summarize` ) across indexed documents.
* **Enterprise CI/CD & Testing**: API and ingestion regression tests with `pytest` (mocked LLM/database layers) and multi-version matrix CI workflows via GitHub Actions (Python 3.11 & 3.14).

---

## Architecture & Data Flow

```text
[ Document Store (PDF) ] ──> [ PyMuPDF Loader ] ──> [ Semantic Chunks (800/150) ]
                                                            │
                     ┌──────────────────────────────────────┴──────────────────────────────────────┐
                     ▼                                                                             ▼
          [ ChromaDB Vector Store ]                                                       [ BM25 Retriever ]
         (Semantic Embeddings: MiniLM)                                                   (Keyword Search)
                     │                                                                             │
                     └──────────────────────────────┬──────────────────────────────────────────────┘
                                                    ▼
                                    [ Candidate Pool (Top 6) ]
                                                    │
                                                    ▼
                                    [ Cross-Encoder Reranker ]
                                    (ms-marco-MiniLM-L-6-v2)
                                                    │
                                                    ▼
                                     [ Top 3 Verified Context ]
                                                    │
[ User Query / API / Telegram ] ───────────────────┼──> [ Ollama: llama3.2 ] ──> [ Structured Response ]

## Local setup

Requires Python 3.11 or a compatible version and a running Ollama installation.

1. Create a virtual environment: `python -m venv .venv`.
2. Activate it (Windows PowerShell: `.venv\\Scripts\\Activate.ps1`; Linux/macOS: `source .venv/bin/activate`).
3. Install dependencies: `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`; set the Telegram token only if using the bot.
5. Start Ollama and download the model: `ollama pull llama3.2`.
6. Create `data/docs`, place text-based PDF files there, then run `python ingest.py`.
7. Start the API: `uvicorn main:app --host 127.0.0.1 --port 8000`.
8. Open http://127.0.0.1:8000/docs. Optionally run `python telegram_bot.py` in another terminal.

Embedding and reranking models download on first use. Scanned PDFs require OCR before indexing.
Re-indexing unchanged PDFs reuses stable chunk IDs. Changed or deleted files are not automatically
removed from the index: for a full rebuild, stop API and bot, remove only `data/chroma_db`,
and run ingestion again. Keep the original PDFs.

## Docker

Run Ollama on the host. Then:

```sh
docker compose build
docker compose run --rm rag-api python ingest.py
docker compose up -d
```

PDFs belong in the host's `data/docs` directory, mounted into the container.
Compose connects to Ollama through `host.docker.internal`. Ollama must listen on an
interface reachable from the container; firewall access should be limited to the Docker
network. A host-only loopback listener is not reachable from a Linux container.

## Configuration

- `OLLAMA_BASE_URL`: Ollama URL for local execution; Compose supplies the host gateway URL.
- `OLLAMA_MODEL`: installed Ollama model name (default `llama3.2`).
- `API_BASE_URL`: API URL used by the separately started Telegram bot.
- `TELEGRAM_BOT_TOKEN`: bot token; never commit it.

## Verification and limitations

Run `python -m pytest -v`. CI also validates the Compose configuration.
Tests cover mocked API calls and ingestion/retrieval regressions; they do not establish
end-to-end model quality or successful deployment with real PDFs and Ollama.

The API has no authentication or per-user document isolation. Restrict network access
for private documents. Conversation history is provided by the caller; retrieval uses
the current question only, so follow-up questions should include the topic explicitly.
BM25 is rebuilt from indexed chunks on each query for consistency; large corpora will
need a versioned cache. Dependency versions are not locked yet.
