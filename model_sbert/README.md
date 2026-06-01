# 🧠 ITCareerMatch — Fine-tuned SBERT Model

Model Siamese BERT yang di-fine-tune untuk menghitung **skor kesesuaian antara CV pelamar kerja dan deskripsi pekerjaan** di industri IT. Dibangun di atas `sentence-transformers/all-MiniLM-L6-v2` menggunakan TensorFlow/Keras dengan arsitektur Siamese Network.

---

## 🏗️ Arsitektur Model

```
Job Description ──→ [BERT Encoder] ──→ MeanPooling ──→ ProjectionHead ──→ L2Normalize ──→ ┐
                                                                                            ├──→ CosineSimilarity ──→ ScaleTo[0,1] ──→ Match Score
CV / Resume ──────→ [BERT Encoder] ──→ MeanPooling ──→ ProjectionHead ──→ L2Normalize ──→ ┘
```

Model menghasilkan **skor antara 0.0 sampai 1.0** — semakin mendekati 1.0, semakin cocok CV dengan lowongan tersebut.

### Komponen Utama

| Komponen | Detail |
|----------|--------|
| Base model | `sentence-transformers/all-MiniLM-L6-v2` |
| Strategi fine-tuning | Freeze semua layer, unfreeze 1 encoder layer terakhir |
| Pooling | Custom `MeanPooling` (masked average) |
| Projection Head | Dense(128, ReLU) → Dropout(0.3) → Dense(64) |
| Normalisasi | Custom `L2Normalize` |
| Output | Cosine similarity di-scale ke [0, 1] dengan `ScaleTo01` |
| Max token length | 300 |

---

## 📁 Struktur File

```
sbert-model/
├── finetune_sbert.ipynb        # Notebook training lengkap
├── final_dataset.csv           # Dataset training (job_desc, resume, match_label)
├── save_model/
│   ├── itcareermatch_best.keras      # Full model terbaik
│   ├── itcareermatch_weights.h5      # Weights terbaik
│   ├── itcareermatch_encoder.keras   # Encoder-only model (untuk inference)
│   └── itcareermatch_tokenizer/      # Tokenizer hasil fine-tuning
└── logs/
    └── fit/                    # TensorBoard logs
```

---

## ⚙️ Konfigurasi Training

| Parameter | Nilai |
|-----------|-------|
| Base Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Max Sequence Length | 300 |
| Batch Size | 32 |
| Epochs | 20 (dengan Early Stopping) |
| Learning Rate | 2e-5 (Cosine Decay) |
| Optimizer | AdamW (weight_decay=1e-4) |
| Loss Function | Mean Squared Error (MSE) |
| Precision | Mixed Precision (float16) |
| Early Stopping Patience | 3 epoch |

---

## 📊 Dataset

File `final_dataset.csv` berisi 3 kolom:

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `job_desc` | string | Deskripsi lowongan pekerjaan |
| `resume` | string | Teks CV pelamar |
| `match_label` | float (0.0–1.0) | Skor kesesuaian (label ground truth) |

Split data: **80% train / 10% validation / 10% test**

---

## 🚀 Cara Menjalankan Training

### 1. Install dependencies

```bash
pip install tensorflow transformers pandas scikit-learn numpy
```

> Disarankan menggunakan GPU. Pastikan CUDA & cuDNN sudah terinstall.

### 2. Siapkan dataset

Letakkan `final_dataset.csv` di folder yang sama dengan notebook. Pastikan kolom `job_desc`, `resume`, dan `match_label` ada.

### 3. Jalankan notebook

Buka `finetune_sbert.ipynb` dan jalankan cell secara berurutan dari atas ke bawah:

| Cell | Fungsi |
|------|--------|
| 1 | Import library & konfigurasi |
| 2 | Load dataset & split train/val/test |
| 3 | Analisis panjang token |
| 4 | Tokenisasi & buat `tf.data.Dataset` |
| 5 | Definisi custom layers |
| 6 | Build Siamese model |
| 7 | Setup loss function & TensorBoard |
| 8 | Setup optimizer & metrics |
| 9 | Definisi training & validation step |
| 10 | Training loop dengan early stopping |
| 11 | Evaluasi pada test set |

### 4. Monitor training dengan TensorBoard

```bash
tensorboard --logdir logs/fit
```

Buka browser ke `http://localhost:6006`

---

## 📦 Output Model

Setelah training selesai, model tersimpan di folder `save_model/`:

| File | Kegunaan |
|------|----------|
| `itcareermatch_best.keras` | Full Siamese model — untuk training lanjutan |
| `itcareermatch_weights.h5` | Weights saja — untuk load ulang ke arsitektur yang sama |
| `itcareermatch_encoder.keras` | Encoder model — untuk inference (hanya butuh 1 teks input) |
| `itcareermatch_tokenizer/` | Tokenizer — wajib disertakan saat inference |

---

## 🔍 Cara Inference

Untuk menghitung skor kesesuaian CV dengan lowongan:

```python
import tensorflow as tf
from transformers import AutoTokenizer

# Load tokenizer dan encoder model
tokenizer = AutoTokenizer.from_pretrained("save_model/itcareermatch_tokenizer")
model = tf.keras.models.load_model("save_model/itcareermatch_best.keras")

def predict_match(job_desc: str, resume: str, max_len: int = 300) -> float:
    # Tokenisasi job description dan CV
    job_tokens = tokenizer(
        job_desc, padding="max_length", truncation=True,
        max_length=max_len, return_tensors="tf"
    )
    cv_tokens = tokenizer(
        resume, padding="max_length", truncation=True,
        max_length=max_len, return_tensors="tf"
    )

    # Prediksi skor
    score = model.predict([
        job_tokens["input_ids"], job_tokens["attention_mask"],
        cv_tokens["input_ids"],  cv_tokens["attention_mask"]
    ])
    return float(score[0][0])

# Contoh penggunaan
job = "We are looking for a Data Engineer with Python, Spark, and SQL experience."
cv  = "3 years experience as Python developer. Skilled in Pandas, SQL, and basic Spark."

score = predict_match(job, cv)
print(f"Match Score: {score:.4f}")  # Output: 0.0 - 1.0
```

---

## 🧩 Custom Layers

Model menggunakan 3 custom layer yang harus terdaftar saat load model:

| Layer | Fungsi |
|-------|--------|
| `MeanPooling` | Rata-rata token embedding dengan mempertimbangkan attention mask |
| `L2Normalize` | Normalisasi vektor ke unit sphere untuk cosine similarity |
| `ScaleTo01` | Scale output cosine similarity dari [-1,1] ke [0,1] |

Semua layer sudah didaftarkan dengan `@tf.keras.utils.register_keras_serializable()` sehingga otomatis dikenali saat `tf.keras.models.load_model()`.

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Framework | TensorFlow / Keras |
| Base Model | HuggingFace Transformers (`all-MiniLM-L6-v2`) |
| Training | Custom loop dengan `tf.GradientTape` |
| Optimasi | Mixed Precision (float16), AdamW, Cosine Decay LR |
| Monitoring | TensorBoard |
| Environment | Jupyter Notebook |
