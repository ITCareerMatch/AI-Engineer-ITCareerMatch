# 🤖 ITCareerMatch — SBERT AI Service

Microservice FastAPI untuk **job matching berbasis AI** menggunakan model Siamese BERT yang sudah di-fine-tune. Service ini menerima teks CV dan daftar lowongan, lalu mengembalikan skor kesesuaian menggunakan **Hybrid Scoring** (SBERT semantic similarity + explicit skill matching).

---

## 🏗️ Arsitektur Service

```
Express.js (Backend Utama)
        ↓ HTTP Internal
FastAPI SBERT Service :8001
        ↓
SBERTModel (TensorFlow)
  ├── Tokenizer (all-MiniLM-L6-v2)
  ├── BERT Encoder (fine-tuned)
  ├── MeanPooling → Projection Head → L2Normalize
  └── Cosine Similarity → Score [0.0 - 1.0]
```

### Hybrid Scoring Formula

```
Final Score = (SBERT Score × 0.6) + (Skill Match Score × 0.4)
```

SBERT menangkap kecocokan semantik secara keseluruhan, sedangkan Skill Match memberikan bobot lebih pada skill yang secara eksplisit disebutkan di deskripsi lowongan.

---

## 📁 Struktur Folder

```
sbert-service/
├── app/
│   ├── model/
│   │   ├── itcareermatch_tokenizer/     # Tokenizer hasil fine-tuning
│   │   ├── itcareermatch_best.keras     # Full model (opsional)
│   │   ├── itcareermatch_encoder.keras  # Encoder model (opsional)
│   │   └── itcareermatch_weights.h5     # Weights yang dipakai saat inference
│   ├── routes/
│   │   └── ai_match.py                 # Endpoint /internal/ai/match & /analyze-single
│   ├── schemas/
│   │   └── match.py                    # Pydantic schema request & response
│   ├── services/
│   │   ├── inference.py                # SBERTModel — load model & predict_batch
│   │   ├── analyzer.py                 # Analisis gap skill
│   │   └── skill_extractor.py          # Ekstraksi skill dari teks
│   └── utils/
│       ├── config.py                   # Konfigurasi path model & parameter
│       └── text_cleaner.py             # Preprocessing teks CV & job desc
├── main.py                             # Entry point FastAPI
├── test_api.py                         # Script testing endpoint
├── requirements.txt                    # Dependencies Python
├── Procfile                            # Konfigurasi deploy (Railway)
├── .python-version                     # Versi Python
└── .gitignore
```

---

## ⚙️ Konfigurasi (`app/utils/config.py`)

| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| `HUGGINGFACE_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Base model BERT |
| `MAX_LEN` | `300` | Maksimum token per teks |
| `TOP_K_RECOMMENDATIONS` | `20` | Jumlah rekomendasi lowongan yang dikembalikan |
| `MODEL_WEIGHTS_PATH` | `app/model/itcareermatch_weights.h5` | Path weights model |
| `TOKENIZER_PATH` | `app/model/itcareermatch_tokenizer/` | Path tokenizer |

---

## 🚀 Cara Menjalankan

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Pastikan file model tersedia

```
app/model/
├── itcareermatch_tokenizer/   ← folder tokenizer
└── itcareermatch_weights.h5   ← file weights
```

> File model tidak di-push ke GitHub karena ukurannya besar. Hubungi tim AI Engineer untuk mendapatkan file model.

### 3. Jalankan service

```bash
uvicorn main:app --reload --port 8001
```

Cek status di browser:
```
http://localhost:8001
```

Response:
```json
{"status": "AI Service Running", "framework": "FastAPI"}
```

---

## 📡 API Endpoints

Semua endpoint bersifat **internal** — hanya boleh diakses dari backend Express, bukan dari frontend langsung.

---

### `POST /internal/ai/match`

Menghitung skor kesesuaian antara CV dan banyak lowongan sekaligus, lalu mengembalikan top 20 rekomendasi.

**Request Body:**
```json
{
  "user_id": "uuid-user",
  "cv_id": "uuid-cv",
  "cv_text": "Teks lengkap CV yang sudah di-parse...",
  "filtered_jobs": [
    {
      "job_id": "job-001",
      "title": "Data Engineer",
      "company_name": "PT. Contoh",
      "description": "Deskripsi lengkap lowongan..."
    }
  ]
}
```

**Response:**
```json
{
  "cv_id": "uuid-cv",
  "user_id": "uuid-user",
  "extracted_skills": ["python", "sql", "spark", "pandas"],
  "recommendations": [
    {
      "job_id": "job-001",
      "job_title": "Data Engineer",
      "company": "PT. Contoh",
      "match_score": 87.45
    }
  ]
}
```

---

### `POST /internal/ai/analyze-single`

Analisis mendalam untuk satu lowongan — menghitung skor + skill match + skill gap + AI insight.

**Request Body:**
```json
{
  "cv_text": "Teks lengkap CV yang sudah di-parse...",
  "job": {
    "job_id": "job-001",
    "title": "Data Engineer",
    "company_name": "PT. Contoh",
    "description": "Deskripsi lengkap lowongan..."
  }
}
```

**Response:**
```json
{
  "extracted_skills": ["python", "sql", "pandas"],
  "analysis": {
    "job_id": "job-001",
    "job_title": "Data Engineer",
    "company": "PT. Contoh",
    "match_score": 87.45,
    "skill_match": ["python", "sql"],
    "skill_gap": ["spark", "airflow"],
    "ai_insight": "Kamu memiliki fondasi yang kuat di Python dan SQL..."
  }
}
```

---

## 🧠 Detail Teknis Inference

Model dimuat sekali saat server start (`lifespan`) dan disimpan di `app.state.sbert_model` — tidak perlu reload setiap request.

`predict_batch` memproses data dalam **batch kecil (10 item)** untuk mencegah Out of Memory, karena Railway hanya menyediakan RAM 1GB.

```
Input: [job_desc_1, job_desc_2, ...] + [cv_text_1, cv_text_2, ...]
         ↓ Tokenisasi per batch (10 item)
         ↓ BERT Encoder → MeanPooling → Projection → L2Normalize
         ↓ Cosine Similarity → Scale [0, 1]
Output: [0.87, 0.65, 0.43, ...]   ← skor per pasang job-CV
```

---

## 🚢 Deploy ke Railway

### Procfile
Service ini sudah dikonfigurasi untuk Railway via `Procfile`. Pastikan isinya:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Catatan deploy
- **RAM minimum:** 1GB (Railway Starter Plan sudah cukup)
- **File model tidak di-push ke repo** — upload manual via Railway Volume atau gunakan cloud storage
- `predict_batch` sudah dioptimasi untuk RAM terbatas dengan mini-batch size 10

---

## 🧪 Testing

Jalankan script test untuk memastikan semua endpoint berjalan:

```bash
python test_api.py
```

Atau test manual via Swagger UI (otomatis tersedia di FastAPI):
```
http://localhost:8001/docs
```

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Framework | FastAPI (Python) |
| Model | Fine-tuned SBERT (TensorFlow + HuggingFace) |
| Base Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Schema Validation | Pydantic v2 |
| Deploy | Railway |
