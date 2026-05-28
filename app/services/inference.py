import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModel
from app.utils import config

@tf.keras.utils.register_keras_serializable()
class MeanPooling(tf.keras.layers.Layer):
    def call(self, inputs):
        token_embeddings, attention_mask = inputs
        mask = tf.cast(tf.expand_dims(attention_mask, axis=-1), dtype=token_embeddings.dtype)
        masked = token_embeddings * mask
        sum_embeddings = tf.reduce_sum(masked, axis=1)
        sum_mask = tf.reduce_sum(mask, axis=1)
        return sum_embeddings / tf.clip_by_value(sum_mask, 1e-9, 1e9)

# Class untuk memuat model SBERT dan melakukan match scoring antara deskripsi pekerjaan dan CV
class SBERTModel:
    def __init__(self):
        print("Menyiapkan Model SBERT...")
        self.tokenizer = AutoTokenizer.from_pretrained(config.TOKENIZER_PATH)
        self.model = self._build_architecture()
        self.model.load_weights(config.MODEL_WEIGHTS_PATH)
        print("Model SBERT Siap Digunakan!")

    def _build_architecture(self):
        job_ids = tf.keras.layers.Input(shape=(config.MAX_LEN,), dtype=tf.int32, name="job_input_ids")
        job_mask = tf.keras.layers.Input(shape=(config.MAX_LEN,), dtype=tf.int32, name="job_attention_mask")
        cv_ids = tf.keras.layers.Input(shape=(config.MAX_LEN,), dtype=tf.int32, name="cv_input_ids")
        cv_mask = tf.keras.layers.Input(shape=(config.MAX_LEN,), dtype=tf.int32, name="cv_attention_mask")

        # Load pre-trained BERT model
        bert_model = TFAutoModel.from_pretrained(config.HUGGINGFACE_MODEL_NAME)
        
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

        dense = tf.keras.layers.Dense(128, activation="relu")
        dropout = tf.keras.layers.Dropout(0.2) 
        projection = tf.keras.layers.Dense(64, activation=None)

        job_proj = projection(dropout(dense(job_vec)))
        cv_proj = projection(dropout(dense(cv_vec)))

        # L2 Normalization dan Cosine Similarity
        normalize_layer = tf.keras.layers.Lambda(lambda x: tf.nn.l2_normalize(x, axis=1), name="l2_normalize")
        job_proj = normalize_layer(job_proj)
        cv_proj = normalize_layer(cv_proj)

        cosine_sim = tf.keras.layers.Dot(axes=1, normalize=False, name="cosine_similarity")([job_proj, cv_proj])

        # Output Scaling ke Rentang 0-1
        final_output = tf.keras.layers.Lambda(lambda x: (x + 1.0) / 2.0, name="scaled_similarity")(cosine_sim)
        final_output = tf.keras.layers.Activation("linear", dtype="float32", name="final_score")(final_output)

        model = tf.keras.Model(inputs=[job_ids, job_mask, cv_ids, cv_mask], outputs=final_output)
        return model

    # Fungsi untuk melakukan prediksi antara daftar deskripsi pekerjaan dan CV
def predict_batch(self, job_descs: list, resumes: list, batch_size: int = 15) -> list:
        """
        Melakukan prediksi secara bertahap untuk mencegah Out of Memory
        karena keterbatasan kapasitas RAM 1GB dari Railway.
        """
        all_scores = []
        total_items = len(job_descs)

        # Proses data per batch kecil
        for i in range(0, total_items, batch_size):
            batch_jobs = job_descs[i : i + batch_size]
            batch_cvs = resumes[i : i + batch_size]

            # Tokenisasi hanya untuk batch saat ini
            job_tok = self.tokenizer(
                batch_jobs, padding="max_length", truncation=True, 
                max_length=config.MAX_LEN, return_tensors="tf"
            )
            cv_tok = self.tokenizer(
                batch_cvs, padding="max_length", truncation=True, 
                max_length=config.MAX_LEN, return_tensors="tf"
            )
            
            inputs_dict = {
                "job_input_ids": job_tok["input_ids"],
                "job_attention_mask": job_tok["attention_mask"],
                "cv_input_ids": cv_tok["input_ids"],
                "cv_attention_mask": cv_tok["attention_mask"]
            }
            
            # Prediksi batch ini dan simpan skornya
            scores = self.model(inputs_dict, training=False).numpy().flatten()
            all_scores.extend(scores.tolist())

        return all_scores