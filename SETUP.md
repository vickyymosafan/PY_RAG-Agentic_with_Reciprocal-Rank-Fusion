# Panduan Setup Manual - RAG Chatbot

## 1. Install PostgreSQL + pgvector

### Windows

1. Download PostgreSQL: https://www.postgresql.org/download/windows/
2. Jalankan installer, catat password untuk `postgres`
3. Buka Command Prompt:

```cmd
cd "C:\Program Files\PostgreSQL\16\bin"
psql -U postgres
```

4. Di psql:

```sql
CREATE DATABASE rag_db;
\c rag_db
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### Alternatif: Supabase (Gratis)

- Daftar di https://supabase.com
- Buat project baru (pgvector sudah terinstall)
- Copy connection string

---

## 2. Install Redis

### Windows

- Download dari: https://github.com/tporadowski/redis/releases
- Extract dan jalankan `redis-server.exe`

### Alternatif: Redis Cloud (Gratis)

- Daftar di https://redis.com/try-free/
- Copy connection string

---

## 3. Setup Project

```powershell
cd "d:\Vicky\project baru\RAG"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## 4. Konfigurasi .env

```powershell
copy .env.example .env
```

Edit `.env`:

```env
COHERE_API_KEY=your_actual_api_key
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/rag_db
REDIS_URL=redis://localhost:6379/0
```

---

## 5. Jalankan

```powershell
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Buka: http://localhost:8000

---

## Troubleshooting

**Cannot connect to PostgreSQL**: Pastikan service running, check password
**Cannot connect to Redis**: Pastikan redis-server running
**COHERE_API_KEY not found**: Daftar di https://dashboard.cohere.com
