from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import ai_match
from app.services.inference import SBERTModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start: Muat model SBERT ke dalam memori saat server mulai
    try:
        app.state.sbert_model = SBERTModel()
    except Exception as e:
        print(f"Gagal memuat model SBERT: {e}")
        app.state.sbert_model = None
    
    yield 
    
    # Shutdown: Bersihkan memory
    app.state.sbert_model = None
    print("Memori dibersihkan. Server mati.")

app = FastAPI(title="ITCareerMatch AI Service", lifespan=lifespan)

# Daftarkan router untuk endpoint AI Match
app.include_router(ai_match.router)

@app.get("/")
def read_root():
    return {"status": "AI Service Running", "framework": "FastAPI"}