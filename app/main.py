import re
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from . import rag, voice
from .config import AUDIO_DIR, SAMPLE_DIR, UPLOAD_DIR
from .ingest import ingest_file

app = FastAPI(title="Voice RAG (Telugu / Hindi / English)")


class AskIn(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/upload")
def upload(files: list[UploadFile] = File(...)):
    report = []
    for f in files:
        name = Path(f.filename).name
        if Path(name).suffix.lower() not in {".pdf", ".txt", ".md"}:
            report.append({"file": name, "error": "unsupported type"})
            continue
        dest = UPLOAD_DIR / name
        dest.write_bytes(f.file.read())
        n = rag.store.add(ingest_file(dest))
        report.append({"file": name, "chunks": n, **({"warning": "no text found (scanned PDF? needs OCR)"} if n == 0 else {})})
    return {"results": report}


@app.post("/load-sample")
def load_sample():
    """Index the bundled EN/TE/HI demo documents."""
    n = sum(rag.store.add(ingest_file(p)) for p in sorted(SAMPLE_DIR.glob("*.txt")))
    return {"chunks": n}


@app.get("/sources")
def sources():
    return {"sources": rag.store.sources()}


@app.delete("/reset")
def reset():
    rag.store.reset()
    return {"ok": True}


@app.post("/ask")
def ask(body: AskIn):
    try:
        return rag.answer(body.question)
    except RuntimeError as e:
        raise HTTPException(500, str(e))


@app.post("/ask-voice")
async def ask_voice(file: UploadFile = File(...)):
    uid = uuid.uuid4().hex
    suffix = Path(file.filename or "a.wav").suffix or ".wav"
    in_path = AUDIO_DIR / f"in_{uid}{suffix}"
    in_path.write_bytes(await file.read())
    transcript, lang = await run_in_threadpool(voice.transcribe, str(in_path))
    if not transcript:
        raise HTTPException(400, "Could not understand the audio.")
    try:
        result = await run_in_threadpool(rag.answer, transcript, lang)
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    out_name = f"{uid}.mp3"
    spoken = re.sub(r"\[\d+\]|[*_#`]", "", result["answer"])  # don't read citations aloud
    await voice.synthesize(spoken, lang, str(AUDIO_DIR / out_name))
    return {"transcript": transcript, **result, "audio_url": f"/audio/{out_name}"}


@app.get("/audio/{name}")
def audio(name: str):
    p = AUDIO_DIR / Path(name).name
    if not p.exists():
        raise HTTPException(404)
    return FileResponse(p, media_type="audio/mpeg")
