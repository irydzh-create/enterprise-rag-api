---
title: Enterprise RAG API
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Enterprise Document Intelligence & Hybrid RAG API 🛡️

[![CI Pipeline](https://github.com/irydzh-create/enterprise-rag-api/actions/workflows/ci.yml/badge.svg)](https://github.com/irydzh-create/enterprise-rag-api/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)](https://www.docker.com/)

A GDPR/DSGVO-compliant, privacy-first Retrieval-Augmented Generation (RAG) backend engineered for enterprise document management. It features a two-stage **Hybrid Retrieval Pipeline** (ChromaDB + BM25 with Cross-Encoder reranking), local LLM inference via **Ollama** (`llama3.2`), and dual interfaces: a RESTful API and an asynchronous Telegram Bot.

---

## Key Features

* **GDPR / DSGVO Compliant**: Fully on-premises pipeline using `paraphrase-multilingual-MiniLM-L12-v2` embeddings and local `llama3.2` execution via Ollama. Confidential documents never leave the internal perimeter.
* **Two-Stage Hybrid Retrieval**: Combines semantic vector similarity (ChromaDB) with lexical keyword matching (BM25) and re-ranks candidates using a Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) for high precision.
* **Semantic Chunking**: Structured parsing using `PyMuPDF` and `RecursiveCharacterTextSplitter` (800-character chunks with 150-character overlap) to prevent context loss at page boundaries.
* **Multi-Turn Conversational Memory**: Stateful dialog support for contextual follow-up questions.
* **Automated Code Review**: Dedicated `/code-review` endpoint and `/review` bot command leveraging low-temperature LLM prompts for static Python analysis and PEP 8 compliance checks.
* **Topic Summarization**: Automated extraction of structured executive summaries (`/summarize` and `/summary`) across indexed documents.
* **Enterprise CI/CD & Testing**: 100% test pass rate with `pytest` (mocked LLM/database layers) and multi-version matrix CI workflows via GitHub Actions (Python 3.11 & 3.14).

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