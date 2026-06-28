# ⚖️ Legal Aid AI v2.0

> RAG-powered multilingual legal assistant for low-income Indian citizens.  
> Supports English, Hindi, and Marathi. Works **without an API key** using local embeddings.

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## ✨ Features

- **Multilingual** — English, Hindi, Marathi (voice + text)
- **Free by default** — Uses local `all-MiniLM-L6-v2` embeddings (no API key needed)
- **Plug-in LLM** — Optional OpenAI GPT-4o-mini for richer answers; falls back gracefully
- **Admin upload** — Add new bare act PDFs via UI or API without restarting
- **16 legal domains** — Constitution, BNS, BNSS, BSA, RTI, Consumer, Labour, and more
- **Source citations** — Every answer cites the exact act and section
- **Nearby legal centers** — Locates nearest NALSA centers by GPS
- **Dark mode** — Toggle in the navbar
- **Docker-ready** — One command to run the full stack

---

## 🗂️ Project Structure

```
legal-aid-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── core/                      # config, logging
│   │   ├── models/                    # schemas, enums (16 legal domains)
│   │   ├── api/
│   │   │   ├── middleware/            # rate limiter
│   │   │   └── routes/               # chat, legal, location, health, admin
│   │   ├── services/
│   │   │   ├── rag/                   # pipeline, retriever, embeddings, chunker
│   │   │   ├── nlp/                   # classifier, translator, whisper STT
│   │   │   ├── geo/                   # NALSA center locator (built-in data)
│   │   │   └── admin/                 # PDF ingestion pipeline
│   │   └── utils/                     # pdf_parser, text_cleaner, logger
│   ├── data/
│   │   ├── raw/pdfs/                  # place downloaded bare act PDFs here
│   │   ├── processed/                 # auto-generated structured JSON
│   │   └── vectorstore/               # auto-generated FAISS index
│   ├── scripts/
│   │   ├── ingest_pdfs.py             # batch PDF → JSON pipeline
│   │   ├── build_vectorstore.py       # JSON → FAISS index
│   │   └── evaluate_rag.py            # accuracy benchmarks
│   ├── tests/                         # pytest suite
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── Procfile
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── chat/                  # ChatWindow, MessageBubble, VoiceInput
│       │   ├── legal/                 # DomainBadge, RightsCard, SourcesCitation
│       │   ├── shared/                # Navbar (dark mode), Footer
│       │   └── ui/                    # Button, Badge, Modal, Spinner
│       ├── pages/                     # Home, Chat, Upload, About
│       ├── hooks/                     # useChat (history-aware), useVoice, useLanguage
│       ├── store/                     # chatStore (Zustand + dark mode), languageStore
│       └── services/                  # api.js, whisper.js, geolocation.js
├── docker/
│   ├── docker-compose.yml
│   └── nginx.conf
├── docs/
├── notebooks/
├── render.yaml
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # Edit if you want OpenAI answers
```

### 2. Add Legal PDFs (one-time)

Download Indian bare acts from:
- https://indiacode.nic.in
- https://legislative.gov.in

Place them in `backend/data/raw/pdfs/` and create/edit the manifest:

```bash
python scripts/ingest_pdfs.py     # parse PDFs → JSON
python scripts/build_vectorstore.py  # JSON → FAISS index
```

Or skip this and upload PDFs directly via the UI at `/upload`.

### 3. Start API

```bash
uvicorn app.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 4. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
# App: http://localhost:5173
```

---

## 🐳 Docker (Full Stack)

```bash
cd docker
docker-compose up --build
# App: http://localhost
# API: http://localhost:8000
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_PROVIDER` | `sentence_transformers` | `sentence_transformers` / `baai_bge` / `openai` |
| `OPENAI_API_KEY` | *(empty)* | Optional — enables GPT answers and Whisper STT |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI model for generation |
| `RETRIEVAL_TOP_K` | `5` | Number of chunks to retrieve per query |
| `CHUNK_SIZE` | `900` | Characters per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between chunks |
| `RATE_LIMIT_PER_MINUTE` | `30` | Max chat requests per IP per minute |
| `MAX_UPLOAD_MB` | `50` | Maximum PDF upload size |

---

## 🌐 API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | System status + vectorstore stats |
| POST | `/chat/` | Main legal Q&A endpoint |
| POST | `/chat/transcribe` | Audio → text (requires OPENAI_API_KEY) |
| GET | `/legal/domains` | List all 16 legal domains |
| POST | `/legal/search` | Semantic search over the knowledge base |
| GET | `/location/centers` | Nearest NALSA legal aid centers |
| POST | `/admin/upload-law` | Upload PDF → auto-ingest |
| POST | `/admin/rebuild-vectorstore` | Rebuild FAISS from all processed JSON |
| GET | `/admin/list-laws` | List all indexed acts |
| GET | `/admin/status` | Detailed system status |

---

## 📊 Evaluation

```bash
cd backend
python scripts/evaluate_rag.py
```

Benchmarks domain classification accuracy and retrieval recall@5.

---

## 🗺️ Supported Legal Domains

Constitution · Criminal Law (BNS) · Criminal Procedure (BNSS) · Evidence (BSA) · Tenant Rights · Labour Law · Domestic Violence · RTI · Consumer Rights · Police Misconduct · Property Dispute · Family Law · Motor Vehicles · IT/Cyber Law · Environmental Law · General

---

## 🆘 Troubleshooting

**"Vector store not found"** — Run `python scripts/build_vectorstore.py` after ingesting PDFs.

**"No text extracted from PDF"** — Some PDFs are scanned images. Use an OCR tool (e.g. OCRmyPDF) first.

**Slow first response** — The embedding model downloads ~90 MB on first use. Subsequent requests are fast.

**CORS error in browser** — Add your frontend URL to `ALLOWED_ORIGINS` in `.env`.

---

## 📞 NALSA Helpline

**1800-11-0031** (Toll-free · 24×7 · National Legal Services Authority)

---

*This tool provides legal information, not legal advice. Always consult a licensed advocate for your specific case.*
