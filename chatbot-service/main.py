from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
import io
import re
import wave

load_dotenv()
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

# Installasi
groq_client: Groq | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global groq_client
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY tidak ditemukan di .env — pastikan sudah diisi!")
    groq_client = Groq(api_key=api_key)
    print("[OK] Groq client siap")
    yield
    groq_client = None

app = FastAPI(title="Job Market Chatbot", lifespan=lifespan)

# Untuk serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# System prompt
SYSTEM_PROMPT = """Kamu adalah asisten karir dan pasar kerja yang bernama JobBot.
Kamu membantu user memahami tren pasar kerja, skill yang dibutuhkan di industri IT, 
tips karir, informasi gaji, dan hal-hal seputar dunia kerja IT. Kamu hanya menjawab seputar industri IT

Jika terdapat bagian [Konteks CV User] di pesan, gunakan informasi tersebut 
untuk memberikan saran yang dipersonalisasi — misalnya menilai kesesuaian skill 
user dengan posisi tertentu, atau merekomendasikan langkah karir berdasarkan 
pengalaman mereka.

Jika tidak ada konteks CV, tetap bantu user dengan informasi umum seputar 
pasar kerja IT.

Panduan menjawab:
- Gunakan Bahasa Indonesia yang ramah dan mudah dipahami
- Berikan jawaban yang konkret dan actionable, bukan hanya teori
- Jika ditanya skill, sebutkan skill spesifik yang relevan
- Jika ditanya gaji, berikan range umum dan faktor yang mempengaruhinya
- Akui keterbatasan jika pertanyaan di luar domain karir/pekerjaan IT
- Jika ditanya diluar industri IT, akui keterbatasan
- Jawab dengan ringkas tapi lengkap, maksimal 3-4 paragraf

Contoh topik yang bisa kamu bantu:
- "Skill apa yang dibutuhkan untuk jadi Data Engineer?"
- "Berapa gaji rata-rata Software Engineer di Jakarta?"
- "Bagaimana cara pindah karir ke bidang AI?"
- "Industri apa yang sedang banyak hiring sekarang?"
"""

# Schema
class Message(BaseModel):
    role: str   # "user" atau "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []

class ChatResponse(BaseModel):
    reply: str
    history: list[Message]

class TTSRequest(BaseModel):
    text: str
    voice: str = "diana"

# Endpoints
@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "model": "llama-3.3-70b-versatile"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, x_internal_request: str = Header(default=None)):
    if INTERNAL_API_KEY and x_internal_request != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    # Susun history untuk dikirim ke Groq
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Tambahkan history sebelumnya (max 10 pesan terakhir supaya tidak terlalu panjang)
    for msg in req.history[-10:]:
        messages.append({"role": msg.role, "content": msg.content})

    # Tambahkan pesan baru dari user
    messages.append({"role": "user", "content": req.message})

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

    # Update history
    updated_history = list(req.history) + [
        Message(role="user", content=req.message),
        Message(role="assistant", content=reply),
    ]

    return ChatResponse(reply=reply, history=updated_history)

# ── TTS Helpers ────────────────────────────────────────────────────────────────
MAX_CHUNK = 190  # sedikit di bawah limit 200 Orpheus

def clean_text_for_tts(text: str) -> str:
    """Hapus markdown agar tidak dibaca secara literal oleh TTS."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)   # **bold**
    text = re.sub(r'\*(.+?)\*',     r'\1', text)   # *italic*
    text = re.sub(r'`(.+?)`',       r'\1', text)   # `code`
    text = re.sub(r'#+\s*',         '',    text)   # # heading
    text = re.sub(r'\n+',           ' ',   text)   # newline → spasi
    return text.strip()

def split_into_chunks(text: str, max_chars: int = MAX_CHUNK) -> list[str]:
    """Potong teks menjadi chunk ≤ max_chars dengan batas kalimat/koma."""
    # Pisah per kalimat
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks: list[str] = []
    current = ""

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        # Kalimat sendiri sudah lebih panjang → potong per koma
        if len(sent) > max_chars:
            parts = [p.strip() for p in sent.split(',') if p.strip()]
            for part in parts:
                if len(current) + len(part) + 2 <= max_chars:
                    current = (current + ", " + part).strip(", ") if current else part
                else:
                    if current:
                        chunks.append(current)
                    # Kalau part-nya sendiri masih panjang, potong paksa
                    while len(part) > max_chars:
                        chunks.append(part[:max_chars])
                        part = part[max_chars:]
                    current = part
        else:
            if len(current) + len(sent) + 1 <= max_chars:
                current = (current + " " + sent).strip() if current else sent
            else:
                if current:
                    chunks.append(current)
                current = sent

    if current:
        chunks.append(current)

    return [c for c in chunks if c.strip()]

def combine_wav_bytes(wav_list: list[bytes]) -> bytes:
    """Gabungkan beberapa WAV bytes menjadi satu file WAV."""
    if len(wav_list) == 1:
        return wav_list[0]

    frames_all = b""
    params = None

    for wav_bytes in wav_list:
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, 'rb') as wf:
            if params is None:
                params = wf.getparams()
            frames_all += wf.readframes(wf.getnframes())

    out = io.BytesIO()
    with wave.open(out, 'wb') as wf:
        # Set parameter satu per satu — JANGAN pakai setparams()
        # karena setparams() ikut copy nframes dari chunk pertama
        # yang menyebabkan overflow saat WAV digabung
        wf.setnchannels(params.nchannels)
        wf.setsampwidth(params.sampwidth)
        wf.setframerate(params.framerate)
        wf.writeframes(frames_all)  # nframes dihitung otomatis

    return out.getvalue()

# ── TTS Endpoint ───────────────────────────────────────────────────────────────
@app.post("/tts")
def text_to_speech(req: TTSRequest, x_internal_request: str = Header(default=None)):
    if INTERNAL_API_KEY and x_internal_request != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    """Convert text to speech menggunakan Groq Orpheus TTS.
    Teks dipotong per kalimat (≤190 char) lalu WAV-nya digabung.
    """
    try:
        clean = clean_text_for_tts(req.text)
        chunks = split_into_chunks(clean)

        if not chunks:
            raise HTTPException(status_code=400, detail="Teks kosong setelah dibersihkan.")

        wav_parts: list[bytes] = []
        for chunk in chunks:
            resp = groq_client.audio.speech.create(
                model="canopylabs/orpheus-v1-english",
                voice=req.voice,
                input=chunk,
                response_format="wav",
            )
            wav_parts.append(resp.read())

        combined = combine_wav_bytes(wav_parts)
        return StreamingResponse(
            io.BytesIO(combined),
            media_type="audio/wav",
            headers={"Content-Disposition": "inline; filename=speech.wav"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

@app.get("/tts/voices")
def get_voices():
    """Daftar voice Orpheus yang tersedia."""
    voices = [
        {"id": "autumn", "name": "Autumn (Female)"},
        {"id": "diana",  "name": "Diana (Female)"},
        {"id": "hannah", "name": "Hannah (Female)"},
        {"id": "austin", "name": "Austin (Male)"},
        {"id": "daniel", "name": "Daniel (Male)"},
        {"id": "troy",   "name": "Troy (Male)"},
    ]
    return {"voices": voices}
