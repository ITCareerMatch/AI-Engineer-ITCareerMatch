# JobBot — Job Market Chatbot

Chatbot sederhana untuk Q&A seputar pasar kerja, skill, dan karir.
Dibangun sebagai demo/prototype untuk project CareerLens.

**Stack**: FastAPI + Groq (Llama 3) + Vanilla HTML/JS

---

## Setup (5 menit)

### 1. Dapatkan Groq API Key (gratis)
1. Buka https://console.groq.com
2. Daftar / login (gratis, tidak perlu kartu kredit)
3. Klik **"Create API Key"**
4. Copy key-nya

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Buat file .env
```bash
cp .env.example .env
```
Buka file `.env`, ganti `gsk_xxxxxxxx` dengan API key kamu:
```
GROQ_API_KEY=gsk_api_key_kamu_di_sini
```

### 4. Jalankan server
```bash
uvicorn main:app --reload --port 8000
```

### 5. Buka browser
```
http://localhost:8000
```

---

## Struktur file
```
jobmarket-chatbot/
├── main.py          # FastAPI backend + endpoint /chat
├── static/
│   └── index.html   # Frontend UI chatbot
├── requirements.txt
├── .env.example
└── README.md
```

## Endpoint API

### POST /chat
Request:
```json
{
  "message": "Skill apa yang paling dicari untuk Data Engineer?",
  "history": []
}
```

Response:
```json
{
  "reply": "Untuk posisi Data Engineer, skill yang paling dicari adalah...",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### GET /health
Cek apakah server berjalan.

---

## Catatan untuk integrasi ke CareerLens

Endpoint `/chat` di file `main.py` ini bisa langsung dipindahkan ke backend
CareerLens sebagai route baru. Yang perlu disesuaikan:
- Tambahkan JWT auth middleware
- Simpan history ke tabel `ai_insights` di PostgreSQL
- Update system prompt dengan data tren skill dari `skill_trends_output.csv`
