from fastapi import FastAPI, Header, HTTPException, Depends
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from app.routes import ai_match
from app.services.inference import SBERTModel

load_dotenv()

async def verify_internal_key(x_internal_request: str = Header(None)):
    expected_key = os.getenv("INTERNAL_API_KEY")
    
    # Jika key tidak cocok atau kosong, tolak aksesnya
    if not expected_key or x_internal_request != expected_key:
         raise HTTPException(
             status_code=401, 
             detail="Unauthorized. Invalid or missing internal API key"
         )

@asynccontextmanager
async def lifespan(app: FastAPI):
    #
    try:
        print("⚙️ Memuat model SBERT ke memori...")
        app.state.sbert_model = SBERTModel()
        print("✅ Model SBERT berhasil dimuat!")
    except Exception as e:
        print(f"❌ Gagal memuat model SBERT: {e}")
        app.state.sbert_model = None
    
    yield 
    
    app.state.sbert_model = None
    print("🛑 Memori dibersihkan. Server mati.")

app = FastAPI(title="ITCareerMatch AI Service", lifespan=lifespan)

app.include_router(
    ai_match.router, 
    dependencies=[Depends(verify_internal_key)] 
)

@app.get("/")
def read_root():
    return {
        "status": "AI Service Running", 
        "framework": "FastAPI",
        "message": "Access to /internal/ai endpoints is restricted."
    }