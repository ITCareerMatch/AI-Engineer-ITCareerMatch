import re

def clean_it_text(text: str) -> str:
    """
    Membersihkan teks raw CV/Job dengan menghapus Email, No HP, URL,
    kata administratif, namun mempertahankan karakter esensial skill IT.
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Hapus URL dan Email
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    
    # 2. Hapus Nomor HP (Format Indonesia/Internasional/Umum)
    # Menangkap +62, 62, 08, dan angka panjang 10-14 digit
    text = re.sub(r'(?:\+62|62|0)[2-9]\d{7,12}\b', '', text)
    text = re.sub(r'\b\d{10,14}\b', '', text)
    
    # 3. Hapus Kata-kata Administratif CV (Noise)
    noise_words = [
        r'tempat[,]? tanggal lahir', r'tanggal lahir', 
        r'jenis kelamin', r'agama', r'kewarganegaraan', 
        r'status perkawinan', r'alamat', r'no hp', 
        r'nomor handphone', r'nomor telepon'
    ]
    for word in noise_words:
        text = re.sub(word, ' ', text, flags=re.IGNORECASE)
    
    # 4. Perlindungan Skill IT: Hapus karakter non-alphanumeric 
    # KECUALI spasi, +, #, ., -
    text = re.sub(r'[^a-zA-Z0-9\+\#\.\-\s]', ' ', text)
    
    # 5. Normalisasi spasi dan lowercase
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()