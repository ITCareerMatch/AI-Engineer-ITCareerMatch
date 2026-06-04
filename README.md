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
│
├── chatbot/                           # Layanan Chatbot AI (Groq LLM)
│   ├── main.py                        # FastAPI chatbot & TTS service
│   ├── app.js                         # Express gateway
│   ├── routes/
│   │   └── chatbot.js                 # Routing chatbot
│   ├── static/
│   │   └── index.html                 # UI chatbot
│   ├── .env.example
│   ├── requirements.txt
│   ├── package.json
│   └── README.md
│
├── model_sbert/                       # Pengembangan & Training Model AI
│   ├── finetune_sbert.ipynb           # Notebook fine-tuning SBERT
│   ├── final_dataset.csv              # Dataset training
│   ├── save_model/
│   │   ├── itcareermatch_best.keras
│   │   ├── itcareermatch_encoder.keras
│   │   ├── itcareermatch_weights.h5
│   │   └── itcareermatch_tokenizer/
│   ├── inference.py                   # Pengujian inferensi model
│   └── README.md
│
├── sbert-service/                     # 
│   ├── app/
│   │   ├── model/                     # Direktori penyimpanan bobot model & tokenizer
│   │   ├── routes/
│   │   │   └── ai_match.py            # Endpoint utama (Job recomendation & Gap Analysis)
│   │   ├── schemas/
│   │   │   └── match.py               # Skema validasi request & response (Pydantic)
│   │   ├── services/
│   │   │   ├── analyzer.py            # Logika kalkulasi Gap Analysis
│   │   │   ├── inference.py           # Modul inferensi model SBERT & Batch Chunking
│   │   │   └── skill_extractor.py     # Modul ekstraksi entitas skill berbasis Regex
│   │   ├── utils/
│   │   │   ├── config.py              # Variabel konfigurasi & konstanta aplikasi
│   │   │   └── text_cleaner.py        # Preprocessing teks CV dan Loker
│   │   └── main.py                    # Entry point aplikasi & Security Middleware (API Key)
│   ├── .python-version                # Penentu versi Python untuk Cloud Server
│   ├── Procfile                       # Startup command untuk Railway
│   ├── requirements.txt               # Daftar dependensi produksi (tensorflow-cpu, fastapi, dll)
│   ├── test_api.py                    # Pengujian endpoint di server local (uvicorn) 
│   └── README.md             
│
└── README.md
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
| Frontend | React.js |
| Gateway | Express.js (Node.js) |
| Chatbot Service | FastAPI (Python) |
| LLM | Llama 3.3 70B via Groq API |
| TTS | Orpheus v1 via Groq API |
| Job Matching | Fine-tuned SBERT (TensorFlow + HuggingFace) |
| Database | Supabase (PostgreSQL) |
| Storage | Supabase Storage |
