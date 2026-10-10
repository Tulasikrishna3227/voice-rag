from app.ingest import chunk_words, ingest_file
from app.config import SAMPLE_DIR
from app.voice import detect_lang


def test_chunk_overlap():
    text = " ".join(f"w{i}" for i in range(100))
    chunks = chunk_words(text, size=40, overlap=10)
    assert chunks[0].split()[-10:] == chunks[1].split()[:10]
    assert all(len(c.split()) <= 40 for c in chunks)


def test_ingest_sample():
    chunks = ingest_file(SAMPLE_DIR / "clinic_en.txt")
    assert chunks and chunks[0]["source"] == "clinic_en.txt" and chunks[0]["page"] == 1


def test_detect_lang():
    assert detect_lang("What is the fee?") == "en"
    assert detect_lang("ఫీజు ఎంత?") == "te"
    assert detect_lang("फीस कितनी है?") == "hi"
