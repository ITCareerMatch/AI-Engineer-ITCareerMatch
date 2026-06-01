# 🤖 JobBot — Chatbot Service

Layanan chatbot berbasis AI untuk membantu pelamar kerja memahami tren pasar kerja, skill yang dibutuhkan, informasi gaji, dan saran karir di industri IT. Dibangun dengan **FastAPI** (Python) dan **Express.js** (Node.js) sebagai gateway, menggunakan **Groq API** sebagai LLM provider.

---

## 🏗️ Arsitektur

```
Frontend (index.html)
        ↕
Express.js :3000        ← gateway utama (routing, session, inject CV)
        ↕
FastAPI :8000           ← chatbot service (LLM, TTS)
        ↕
Groq API (cloud)
```

---

## 📁 Struktur Folder

```
jobmarket-chatbot/
├── main.py              # FastAPI — chatbot logic, Groq, TTS
├── app.js               # Express.js — entry point, serve frontend
├── routes/
│   └── chatbot.js       # Express router — jembatan frontend ↔ FastAPI
├── static/
│   └── index.html       # Tampilan frontend chatbot
├── .env                 # Secret keys (JANGAN di-push ke GitHub)
├── .env.example         # Template .env untuk referensi tim
├── requirements.txt     # Dependencies Python
└── package.json         # Dependencies Node.js
```

---

## ⚙️ Prerequisites

- Python >= 3.10
- Node.js >= 18
- Akun [Groq](https://console.groq.com) (untuk API key)
- Supabase project (untuk akses tabel `cv_archives`)

---

## 🚀 Cara Menjalankan

### 1. Clone & masuk ke folder
```bash
git clone <repo-url>
cd jobmarket-chatbot
```

### 2. Install dependencies Python
```bash
pip install -r requirements.txt
```

### 3. Install dependencies Node.js
```bash
npm install
```

### 4. Buat file `.env`
Salin dari template lalu isi nilainya:
```bash
cp .env.example .env
```

Isi `.env`:
```env
# Groq
GROQ_API_KEY=your_groq_api_key

# Supabase
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Internal security
INTERNAL_API_KEY=your_random_secret_string

# Express
FASTAPI_URL=http://localhost:8000
PORT=3000
```

> Untuk generate `INTERNAL_API_KEY` yang aman:
> ```bash
> node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
> ```

### 5. Jalankan kedua service

```bash
# Terminal 1 — FastAPI
uvicorn main:app --reload --port 8000

# Terminal 2 — Express
node app.js
```

### 6. Buka browser
```
http://localhost:3000
```

---

## 📡 API Endpoints

Semua endpoint diakses melalui Express di port `3000`.

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/api/chatbot/health` | Cek status service |
| `POST` | `/api/chatbot/chat` | Kirim pesan ke chatbot |
| `POST` | `/api/chatbot/tts` | Text-to-speech |
| `GET` | `/api/chatbot/voices` | Daftar voice TTS |

### `POST /api/chatbot/chat`

Request:
```json
{
  "message": "Skill apa yang dibutuhkan untuk jadi Data Engineer?",
  "history": []
}
```

Response:
```json
{
  "reply": "Untuk menjadi Data Engineer, kamu perlu menguasai...",
  "history": [
    { "role": "user", "content": "Skill apa yang dibutuhkan untuk jadi Data Engineer?" },
    { "role": "assistant", "content": "Untuk menjadi Data Engineer, kamu perlu menguasai..." }
  ]
}
```

### `POST /api/chatbot/tts`

Request:
```json
{
  "text": "Teks yang ingin diucapkan",
  "voice": "diana"
}
```

Response: Binary `audio/wav`

### `GET /api/chatbot/voices`

Response:
```json
{
  "voices": [
    { "id": "autumn", "name": "Autumn (Female)" },
    { "id": "diana",  "name": "Diana (Female)" },
    { "id": "hannah", "name": "Hannah (Female)" },
    { "id": "austin", "name": "Austin (Male)" },
    { "id": "daniel", "name": "Daniel (Male)" },
    { "id": "troy",   "name": "Troy (Male)" }
  ]
}
```

---

## 🔐 Keamanan Internal

Endpoint `/chat` dan `/tts` di FastAPI dilindungi dengan header `x-internal-request`. Hanya request yang berasal dari Express (dengan key yang benar) yang akan diterima.

Header ini ditambahkan otomatis oleh `routes/chatbot.js` — **frontend tidak perlu mengirimnya secara manual**.

---

## 🧠 Fitur Personalisasi CV

Jika user sudah login dan memiliki CV tersimpan di Supabase (tabel `cv_archives`, kolom `raw_text`), chatbot akan otomatis mengambil CV terbaru dan menjadikannya konteks jawaban — sehingga bot bisa memberikan saran yang dipersonalisasi berdasarkan profil user.

---

## 👥 Integrasi untuk Tim

### Backend Developer
- Pastikan `req.session?.user?.id` terisi dari sistem login yang ada
- Isi `SUPABASE_URL` dan `SUPABASE_SERVICE_ROLE_KEY` di `.env`
- Gunakan `INTERNAL_API_KEY` yang sama dengan yang dipakai AI service

### Frontend Developer
- Tambahkan `credentials: 'include'` di semua fetch ke `/api/chatbot/*`
- Embed `static/index.html` ke halaman web utama
- Cukup kirim `message` dan `history` — CV diambil otomatis dari server

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Chatbot Service | FastAPI (Python) |
| Gateway | Express.js (Node.js) |
| LLM | Llama 3.3 70B via Groq |
| TTS | Orpheus v1 via Groq |
| Database | Supabase (PostgreSQL) |
| Frontend | Vanilla HTML/CSS/JS |
