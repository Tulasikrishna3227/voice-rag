# 🎙️ Voice RAG: Telugu · Hindi · English

[![CI](https://github.com/Tulasikrishna3227/voice-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/Tulasikrishna3227/voice-rag/actions)

Ask questions about your documents by **text or voice** in Telugu, Hindi or English and get **cited answers** in the same language (spoken back too). Runs **fully free and local**: no API keys required.

<!-- Add after uploading docs/demo.gif:  ![demo](docs/demo.gif) -->

## How it works
```
PDF/TXT → PyMuPDF → chunking → multilingual-e5 embeddings → ChromaDB
Question (text, or mic → faster-whisper) → embed → top-20 → cross-encoder rerank → top-4
   → grounded prompt → local LLM (Ollama) → answer with [1][2] citations → edge-tts audio
```

| Part | Tool |
|---|---|
| Embeddings | `intfloat/multilingual-e5-small` (local) |
| Vector DB | ChromaDB (local) |
| Reranker | multilingual cross-encoder (local, switchable) |
| STT | faster-whisper (local) |
| TTS | edge-tts (free, needs internet, no key) |
| LLM | Ollama `gemma3:4b` (local); Groq/OpenRouter/Gemini optional via `.env` |
| API / UI | FastAPI / Streamlit |

Tested on Windows 11, Python 3.10, 16 GB RAM, CPU only (no GPU).

## Quick start
**Requirements:** Python 3.10–3.12, [Ollama](https://ollama.com), ~8 GB free RAM.
```bash
git clone https://github.com/Tulasikrishna3227/voice-rag.git && cd voice-rag
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
ollama pull gemma3:4b
cp .env.example .env                                   # Windows: copy .env.example .env
python run.py                                          # starts API (8000) + UI (8501)
```
No Git? Use **Code → Download ZIP** on GitHub instead of `git clone`.

Open http://localhost:8501 (if Streamlit asks for an email, just press Enter) → click **Load sample docs** → ask *"సన్‌రైజ్ క్లినిక్ కన్సల్టేషన్ ఫీజు ఎంత?"* or use the **Voice** tab.
The first run downloads the embedding and Whisper models (a few minutes, once), and the first answer is slow while Ollama loads the model.

### Docker
```bash
cp .env.example .env
# set LLM_BASE_URL=http://host.docker.internal:11434/v1 in .env (Ollama runs on your host)
docker compose up --build        # UI :8501, API docs :8000/docs
```

## Using a hosted LLM instead
Edit `.env` (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`). Groq's free tier is much faster than CPU Ollama, especially for Telugu. No code changes needed.

## API
| Endpoint | Purpose |
|---|---|
| `POST /upload` | index PDF/TXT/MD files |
| `POST /load-sample` | index the bundled EN/TE/HI demo docs |
| `POST /ask` | `{"question": "..."}` → answer + sources |
| `POST /ask-voice` | audio file → transcript + answer + sources + `audio_url` |
| `GET /sources` · `DELETE /reset` | list / clear index |

## Tests & evaluation
```bash
pip install -r requirements-dev.txt && pytest -q     # fast, models stubbed (also runs in CI)
python -m eval.eval --no-llm                         # retrieval only
python -m eval.eval                                  # + answer correctness (needs Ollama running)
```
`eval/questions.json` has 12 cross-language questions over 6 sample documents (e.g. a Telugu question answered from an English document). A question counts as correct if any string in its `any_of` list appears in the answer. Stop the app before running the eval (both use the same local database).

**Results** (Gemma3 4B via Ollama, `multilingual-e5-small`):

| Setup | Retrieval hit-rate | Answer correctness |
|---|---|---|
| No rerank | 100% | 100% |
| With rerank | 100% | 100% |

Both setups score 100% on this small set, so it can't tell them apart. The sample corpus is only 6 short documents; a larger corpus is needed for a meaningful reranking comparison. On this set, the reranker did not hurt Telugu retrieval. To try a stronger (but heavier) reranker: `RERANK_MODEL=BAAI/bge-reranker-v2-m3`.

## Limitations
- Scanned PDFs need OCR (not included; Tesseract supports Telugu).
- Small local LLMs (3–4B) are slow on CPU and weaker in Telugu than hosted ones.
- Whisper `small` is weaker on Telugu; try `WHISPER_MODEL=medium`.
- edge-tts needs an internet connection.

## Roadmap
Larger evaluation corpus · hybrid BM25 + vector search · OCR · streaming answers · fully offline TTS · optional Sarvam AI provider

## License
MIT
