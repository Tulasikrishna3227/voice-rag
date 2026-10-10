import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE / "data"))
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma"
AUDIO_DIR = DATA_DIR / "audio"
SAMPLE_DIR = BASE / "data" / "sample"
for d in (UPLOAD_DIR, CHROMA_DIR, AUDIO_DIR):
    d.mkdir(parents=True, exist_ok=True)

EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small")
RERANK_MODEL = os.getenv("RERANK_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
USE_RERANK = os.getenv("USE_RERANK", "true").lower() == "true"

CHUNK_WORDS = int(os.getenv("CHUNK_WORDS", 200))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 40))
TOP_K_RETRIEVE = int(os.getenv("TOP_K_RETRIEVE", 20))
TOP_K_FINAL = int(os.getenv("TOP_K_FINAL", 4))

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:4b")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
