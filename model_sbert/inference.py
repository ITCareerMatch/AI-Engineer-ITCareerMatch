import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModel

# 1. Definisikan custom layer MeanPooling yang digunakan dalam model
@tf.keras.utils.register_keras_serializable()
class MeanPooling(tf.keras.layers.Layer):
    def call(self, inputs):
        token_embeddings, attention_mask = inputs
        mask = tf.cast(tf.expand_dims(attention_mask, axis=-1), dtype=token_embeddings.dtype)
        masked = token_embeddings * mask
        sum_embeddings = tf.reduce_sum(masked, axis=1)
        sum_mask = tf.reduce_sum(mask, axis=1)
        return sum_embeddings / tf.clip_by_value(sum_mask, 1e-9, 1e9)

# 2. Definisikan kelas ITCareerMatcher untuk memuat model dan melakukan inferensi
class ITCareerMatcher:
    def __init__(self, weights_path="save_model/itcareermatch_weights.h5", 
                 tokenizer_path="save_model/itcareermatch_tokenizer",
                 model_name="sentence-transformers/all-MiniLM-L6-v2"):
        
        self.max_len = 300
        
        print("Memuat Tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        
        print("Membangun ulang arsitektur model...")
        self.model = self._build_model_architecture(model_name)
        
        print(f"Memuat bobot dari {weights_path}...")
        self.model.load_weights(weights_path)

        print("Model berhasil dimuat dan siap digunakan!")

    def _build_model_architecture(self, model_name):
        """Membangun ulang arsitektur persis seperti saat training"""
        # Input Layers
        job_ids = tf.keras.layers.Input(shape=(self.max_len,), dtype=tf.int32, name="job_input_ids")
        job_mask = tf.keras.layers.Input(shape=(self.max_len,), dtype=tf.int32, name="job_attention_mask")
        cv_ids = tf.keras.layers.Input(shape=(self.max_len,), dtype=tf.int32, name="cv_input_ids")
        cv_mask = tf.keras.layers.Input(shape=(self.max_len,), dtype=tf.int32, name="cv_attention_mask")

        # Load SBERT
        bert_model = TFAutoModel.from_pretrained(model_name)
        
        # Freeze semua layer kecuali layer terakhir dari encoder dan pooler
        bert_model.trainable = True 
        bert_model.bert.embeddings.trainable = False
        bert_model.bert.pooler.trainable = False
        
        for layer in bert_model.bert.encoder.layer:
            layer.trainable = False
            
        for layer in bert_model.bert.encoder.layer[-1:]:
            layer.trainable = True
       
        # Mean Pooling Layer
        pooling_layer = MeanPooling(name="mean_pooling")

        job_out = bert_model(input_ids=job_ids, attention_mask=job_mask)[0]
        cv_out = bert_model(input_ids=cv_ids, attention_mask=cv_mask)[0]

        job_vec = pooling_layer([job_out, job_mask])
        cv_vec = pooling_layer([cv_out, cv_mask])

        # Projection Head
        dense = tf.keras.layers.Dense(128, activation="relu")
        dropout = tf.keras.layers.Dropout(0.2) 
        projection = tf.keras.layers.Dense(64, activation=None)

        job_proj = projection(dropout(dense(job_vec)))
        cv_proj = projection(dropout(dense(cv_vec)))

        # L2 Normalization
        normalize_layer = tf.keras.layers.Lambda(lambda x: tf.nn.l2_normalize(x, axis=1), name="l2_normalize")
        job_proj = normalize_layer(job_proj)
        cv_proj = normalize_layer(cv_proj)

        # Cosine Similarity
        cosine_sim = tf.keras.layers.Dot(axes=1, normalize=False, name="cosine_similarity")([job_proj, cv_proj])

        # Scale menjadi (0 to 1)
        final_output = tf.keras.layers.Lambda(lambda x: (x + 1.0) / 2.0, name="scaled_similarity")(cosine_sim)
        final_output = tf.keras.layers.Activation("linear", dtype="float32", name="final_score")(final_output)

        model = tf.keras.Model(inputs=[job_ids, job_mask, cv_ids, cv_mask], outputs=final_output)
        return model

    # Fungsi untuk memproses satu pasangan job description dan resume
    def _preprocess(self, job_desc, resume):
        job_tokens = self.tokenizer(job_desc, padding="max_length", truncation=True,
                                    max_length=self.max_len, return_tensors="tf")
        resume_tokens = self.tokenizer(resume, padding="max_length", truncation=True,
                                       max_length=self.max_len, return_tensors="tf")
        return (job_tokens["input_ids"], job_tokens["attention_mask"],
                resume_tokens["input_ids"], resume_tokens["attention_mask"])

    # Fungsi untuk memproses batch data dan menghasilkan skor kecocokan
    def predict_batch(self, job_descs, resumes):
        all_inputs = [self._preprocess(j, r) for j, r in zip(job_descs, resumes)]
        
        # Gabungkan tensor untuk proses batch
        job_ids = tf.concat([inp[0] for inp in all_inputs], axis=0)
        job_mask = tf.concat([inp[1] for inp in all_inputs], axis=0)
        cv_ids = tf.concat([inp[2] for inp in all_inputs], axis=0)
        cv_mask = tf.concat([inp[3] for inp in all_inputs], axis=0)
        
        # Buat dictionary input untuk model
        inputs_dict = {
            "job_input_ids": job_ids,
            "job_attention_mask": job_mask,
            "cv_input_ids": cv_ids,
            "cv_attention_mask": cv_mask
        }
        
        scores = self.model(inputs_dict, training=False)
        return scores.numpy().flatten()

# Test inference dengan contoh data
if __name__ == "__main__":
    matcher = ITCareerMatcher()

    # Contoh data lowongan pekerjaan
    jobs = [
    "Android Developer dengan pengalaman Kotlin dan Jetpack Compose",
    "Backend Engineer menggunakan Node.js dan MongoDB",
    "Data Scientist dengan keahlian Python dan Machine Learning",
    "DevOps Engineer menguasai Docker, Kubernetes, dan CI/CD",
    "Frontend Developer dengan React.js dan TypeScript",
    "Cybersecurity Analyst dengan pengetahuan penetration testing",
    "Cloud Engineer berpengalaman di AWS dan GCP",
    "AI Engineer fokus pada NLP dan TensorFlow",
    "QA Engineer dengan pengalaman automated testing menggunakan Selenium",
    "Mobile Programmer iOS dengan Swift dan UIKit",
    "Fullstack Developer dengan pengalaman MERN Stack (MongoDB, Express, React, Node.js)",
    "Backend Engineer dengan pengalaman Go dan PostgreSQL",
    "Frontend Developer dengan Vue.js dan Tailwind CSS",
    "Data Engineer berpengalaman membangun pipeline ETL dengan Apache Spark",
    "Machine Learning Engineer dengan pengalaman PyTorch dan model deep learning",
    "DevOps Engineer dengan pengalaman Terraform dan monitoring Prometheus",
    "Cloud Engineer dengan spesialisasi Azure dan serverless architecture",
    "Security Engineer dengan keahlian cloud security dan incident response",
    "QA Engineer dengan pengalaman API testing menggunakan Postman dan JMeter",
    "Mobile Developer Android dengan Kotlin Multiplatform Mobile (KMM)",
    "Software Engineer dengan pengalaman microservices architecture dan gRPC",
    "Web Developer dengan pengalaman Next.js dan GraphQL",
    "Data Analyst dengan keahlian SQL, Tableau, dan Power BI",
    "AI Engineer dengan fokus pada Computer Vision dan OpenCV",
    "Backend Developer dengan pengalaman Laravel dan MySQL"
    ]


    # Contoh data CV
    resume = """Lulusan S1 Informatika dengan pengalaman tiga tahun sebagai Fullstack Web Developer, berfokus pada pengembangan aplikasi berbasis web menggunakan React.js, Tailwind CSS, dan Vite untuk frontend, serta Node.js dan Express.js untuk backend. Berpengalaman membangun sistem end-to-end mulai dari desain antarmuka, integrasi API, hingga deployment menggunakan platform seperti Vercel dan Railway. Terampil dalam pengelolaan database PostgreSQL, integrasi AI/ML, serta penerapan autentikasi dan keamanan aplikasi. Familiar dengan version control menggunakan Git/GitHub dan terbiasa bekerja dalam tim kolaboratif. Berorientasi pada pengembangan aplikasi web yang responsif, scalable, dan sesuai kebutuhan industri modern.
    """

    print("\nMenghitung kecocokan CV dengan Lowongan Kerja...\n")
    # Hitung skor untuk semua job terhadap 1 CV
    scores = matcher.predict_batch(jobs, [resume]*len(jobs))

    # Tampilkan hasil (Diurutkan dari skor tertinggi)
    results = list(zip(jobs, scores))
    results.sort(key=lambda x: x[1], reverse=True)

    for j, s in results:
        print(f"Score: {s:.4f} | Job: {j}")