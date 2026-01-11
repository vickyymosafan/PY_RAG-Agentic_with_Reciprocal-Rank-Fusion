# RAG Chatbot Production-Ready

Aplikasi RAG (Retrieval Augmented Generation) Chatbot berbasis FastAPI dengan Clean Architecture.

## Fitur

- ✅ Upload dokumen JSON
- ✅ Hybrid retrieval (BM25 + Vector + RRF fusion)
- ✅ Chat dengan konteks dokumen
- ✅ Response caching dengan Redis
- ✅ Session-based chat history
- ✅ Frontend sederhana dengan HTMX

## Tech Stack

- **Backend**: FastAPI, Pydantic v2, SQLAlchemy 2.0
- **Database**: PostgreSQL + pgvector
- **Cache**: Redis
- **AI**: Cohere API (Embedding + LLM)
- **Frontend**: Jinja2 + HTMX

## Quick Start

1. Setup infrastructure (lihat [SETUP.md](SETUP.md))
2. Copy `.env.example` ke `.env` dan isi konfigurasi
3. Install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
4. Jalankan aplikasi:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Buka http://localhost:8000

## Struktur Project

```
RAG/
├── app/
│   ├── domain/          # Entities, Interfaces
│   ├── application/     # Use Cases, DTOs
│   ├── infrastructure/  # DB, Cache, AI Services
│   └── presentation/    # API Routes, Templates
├── static/              # CSS, JS
├── requirements.txt
├── .env.example
└── SETUP.md
```

## License

MIT
