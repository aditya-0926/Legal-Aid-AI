# System Architecture

## Overview

Legal Aid AI is a RAG (Retrieval-Augmented Generation) system with three main layers:

1. **Ingestion Pipeline** — Scrapes and chunks Indian bare acts into a FAISS vector index
2. **Query Pipeline** — Classifies domain → retrieves chunks → generates response via LLM
3. **Presentation Layer** — React frontend with multilingual support and voice input

## Data Flow

```
1. scrape_bare_acts.py  →  data/raw/bare_acts.json
2. build_vectorstore.py →  data/vectorstore/ (FAISS index)
3. User query           →  classify_domain() → retrieve() → LLM → ChatResponse
```

## Key Design Decisions

- **FAISS over Pinecone**: Local, no cost, sufficient for <1M chunks
- **Keyword classifier**: Fast baseline; swap for zero-shot model in v2
- **Zustand over Redux**: Minimal overhead for small state
- **FastAPI async**: Allows concurrent LLM calls without blocking
