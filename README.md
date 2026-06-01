# 💼 ITCareerMatch — AI-Powered Job Matching Platform

Platform pencarian kerja berbasis AI yang membantu pelamar kerja menemukan lowongan yang paling sesuai dengan CV mereka. Terdiri dari dua komponen AI utama: **model SBERT untuk job matching** dan **chatbot untuk konsultasi karir**.

---

## 🧩 Komponen AI

| Komponen | Teknologi | Fungsi |
|----------|-----------|--------|
| [ITCareerMatch SBERT](./sbert/) | TensorFlow + HuggingFace | Menghitung skor kesesuaian CV ↔ lowongan |
| [JobBot Chatbot](./chatbot/) | FastAPI + Groq (Llama 3) | Konsultasi karir & pasar kerja IT |

Dokumentasi detail masing-masing komponen tersedia di folder masing-masing.

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Web)                    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Express.js Gateway :3000                │
│         (Auth, Session, CV Upload, Routing)          │
└──────┬───────────────────────────────┬──────────────┘
       │                               │
┌──────▼──────────┐          ┌─────────▼──────────────┐
│  FastAPI SBERT  │          │   FastAPI Chatbot       │
│    Service      │          │      Service :8000      │
│  (Job Matching) │          │  (Groq Llama 3 + TTS)   │
└──────┬──────────┘          └─────────┬───────────────┘
       │                               │
┌──────▼──────────┐          ┌─────────▼───────────────┐
│    Supabase     │          │       Groq API           │
│  (CV & Jobs DB) │          │      (Cloud LLM)         │
└─────────────────┘          └──────────────────────────┘
```

---

## 📁 Struktur Repository

```
itcareermatch/
├── chatbot/                    # Chatbot service
│   ├── main.py                 # FastAPI — chatbot & TTS logic
│   ├── app.js                  # Express.js — gateway & routing
│   ├── routes/
│   │   └── chatbot.js          # Express router
│   ├── static/
│   │   └── index.html          # Frontend chatbot
│   ├── .env.example
│   ├── requirements.txt
│   ├── package.json
│   └── README.md               # Dokumentasi chatbot
│
├── sbert/                      # SBERT model
│   ├── finetune_sbert.ipynb    # Notebook training
│   ├── final_dataset.csv       # Dataset (job_desc, resume, match_label)
│   ├── save_model/             # Output model hasil training
│   └── README.md               # Dokumentasi SBERT
│
└── README.md                   # File ini
```

---

## 🚀 Quick Start

### Chatbot Service

```bash
cd chatbot

# Install dependencies
pip install -r requirements.txt
npm install

# Konfigurasi environment
cp .env.example .env
# Edit .env dengan API key yang sesuai

# Jalankan
uvicorn main:app --reload --port 8000   # Terminal 1
node app.js                              # Terminal 2
```

Buka `http://localhost:3000`

### SBERT Training

```bash
cd sbert

# Install dependencies
pip install tensorflow transformers pandas scikit-learn numpy

# Jalankan notebook
jupyter notebook finetune_sbert.ipynb
```

---

## 🔑 Environment Variables

### Chatbot (`.env`)

| Variable | Keterangan |
|----------|------------|
| `GROQ_API_KEY` | API key dari [console.groq.com](https://console.groq.com) |
| `SUPABASE_URL` | URL project Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key Supabase |
| `INTERNAL_API_KEY` | Secret key untuk komunikasi internal Express ↔ FastAPI |
| `FASTAPI_URL` | URL FastAPI chatbot (default: `http://localhost:8000`) |
| `PORT` | Port Express (default: `3000`) |

---

## 🤝 Alur Integrasi Antar Komponen

```
1. User upload CV
        ↓
2. Express parse PDF → simpan raw_text ke Supabase (cv_archives)
        ↓
3. SBERT Service hitung skor CV ↔ semua lowongan
        ↓
4. Tampilkan lowongan dengan skor tertinggi ke user
        ↓
5. User tanya ke JobBot → Express inject CV dari Supabase
        ↓
6. JobBot jawab berdasarkan profil CV user secara spesifik
```

---

## 👥 Tim Pengembang

| Role | Tanggung Jawab |
|------|---------------|
| AI Engineer | SBERT model, Chatbot service (FastAPI + Express) |
| Data Scientist | Dataset preparation, evaluasi model |
| Full Stack Developer | Frontend, backend Express, integrasi Supabase |

---

## 🛠️ Tech Stack Lengkap

| Layer | Teknologi |
|-------|-----------|
| Frontend | HTML / CSS / JavaScript |
| Gateway | Express.js (Node.js) |
| Chatbot Service | FastAPI (Python) |
| LLM | Llama 3.3 70B via Groq API |
| TTS | Orpheus v1 via Groq API |
| Job Matching | Fine-tuned SBERT (TensorFlow + HuggingFace) |
| Database | Supabase (PostgreSQL) |
| Storage | Supabase Storage |
