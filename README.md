---
title: Document RAG API
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---

# Document RAG API

A Python portfolio project for answering questions about local PDF documents.
It combines FastAPI, ChromaDB semantic search, BM25 keyword search,
Cross-Encoder reranking and Ollama generation. A Telegram bot exposes questions,
code review and topic summaries.

## What is implemented

- Recursive loading of text-based PDFs, including uppercase PDF extensions.
- Page-local splitting into 800-character chunks with 150-character overlap.
- Multilingual embeddings and hybrid retrieval from a single indexed corpus.
- Follow-up question rewriting using caller-provided conversation history.
- Local Ollama inference with configurable URL and model.
- Stable chunk IDs and removal of obsolete chunks after successful indexing.
- HTTP input validation and explicit model error statuses.
- Telegram commands `/start`, `/review <code>`, `/summary <topic>`.
- Chat-scoped, bounded in-memory bot history with a one-hour TTL.
- Tests and GitHub Actions for Python 3.11 and 3.14.

## Local setup

Requires Python 3.11 or a compatible version and Ollama.

1. Create a virtual environment: `python -m venv .venv`.
2. Activate it:
   - PowerShell: `.venv\\Scripts\\Activate.ps1`
   - Linux/macOS: `source .venv/bin/activate`
3. Install dependencies: `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`; enter a bot token only if using Telegram.
5. Start Ollama and download the model: `ollama pull llama3.2`.
6. Create `data/docs` and place text-based PDFs there, including subdirectories.
7. Run `python ingest.py`.
8. Start `uvicorn main:app --host 127.0.0.1 --port 8000`.
9. Open http://127.0.0.1:8000/docs.
10. Optionally run `python telegram_bot.py` in another terminal.

Embedding and reranking models download on first use. Scanned documents require
OCR before ingestion. The first model download and first query may be slow.

## Docker

Run Ollama on the host. Place PDFs in `data/docs`, then:

```sh
docker compose build
docker compose run --rm rag-api python ingest.py
docker compose up -d
```

Compose publishes the API on host loopback only. It reaches host Ollama through
`host.docker.internal`. Ollama must listen on an interface reachable from the
container; a host-only loopback listener is not reachable from a Linux container.
Restrict firewall access to the required Docker network.

## Updating documents

Stop the API and bot before ingestion. Keep the complete desired corpus in
`data/docs`, then run `python ingest.py` (or the Compose ingestion command).
All indexed chunks are managed by this corpus: obsolete chunks, including those
from deleted PDFs, are removed after the new chunks are written. Unchanged
chunks keep stable IDs. Do not mix independently managed documents into this collection.

An empty or unreadable corpus fails without intentionally clearing the existing
index. A failed run is not a database transaction: interrupted writes may require
rerunning ingestion. Back up private data before modifying the corpus.

## Configuration

| Variable | Default / purpose |
|---|---|
| OLLAMA_BASE_URL | http://127.0.0.1:11434; Compose uses the host gateway |
| OLLAMA_MODEL | llama3.2 |
| API_BASE_URL | http://127.0.0.1:8000; used by the bot |
| TELEGRAM_BOT_TOKEN | Required only for Telegram; never commit it |

## Checks

```sh
python -m pytest -v
docker compose config --quiet
```

CI runs API, retrieval, follow-up rewriting, bot and ingestion regression tests.
The PDF integration test parses a real temporary PDF and uses a real temporary
Chroma database with deterministic embeddings. It does not download models.
Direct dependency versions are pinned; transitive dependencies are not fully locked.

## Limits

This is a single-corpus prototype, not a multi-tenant production service.
There is no authentication or per-user document isolation. All bot users can
query the same corpus; do not give an unrestricted bot access to private PDFs.
The API root is a liveness check, not a readiness guarantee.

BM25 rebuilds when indexed content changes, but reads the corpus to check for
changes on each query. This is intended for small corpora. Source citations and
a validated relevance threshold are not implemented; model answers still need
human review. Prompt instructions reduce, but do not eliminate, hallucinations
or prompt injection. Local inference alone does not establish GDPR compliance.

Real Ollama inference, model quality and an actual Docker runtime deployment
must be smoke-tested separately. No deployment or main-branch merge is performed
by the test workflow.
