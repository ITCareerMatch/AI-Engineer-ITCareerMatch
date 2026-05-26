import os

# Lokasi direktori model dan tokenizer
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Konfigurasi Model SBERT
MODEL_WEIGHTS_PATH = os.path.join(BASE_DIR, "model", "itcareermatch_weights.h5")
TOKENIZER_PATH = os.path.join(BASE_DIR, "model", "itcareermatch_tokenizer")
HUGGINGFACE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MAX_LEN = 300 

# Konfigurasi Output
TOP_K_RECOMMENDATIONS = 20