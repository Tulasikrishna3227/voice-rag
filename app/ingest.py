from pathlib import Path
import pymupdf as fitz  # PyMuPDF

from .config import CHUNK_WORDS, CHUNK_OVERLAP


def load_file(path: Path):
    """Return a list of (page_number, text)."""
    if path.suffix.lower() == ".pdf":
        with fitz.open(path) as doc:
            return [(i + 1, p.get_text()) for i, p in enumerate(doc)]
    return [(1, path.read_text(encoding="utf-8", errors="ignore"))]


def chunk_words(text: str, size: int = CHUNK_WORDS, overlap: int = CHUNK_OVERLAP):
    words = text.split()
    step = max(size - overlap, 1)
    chunks = []
    for i in range(0, len(words), step):
        piece = words[i : i + size]
        if len(piece) >= 5:
            chunks.append(" ".join(piece))
    return chunks


def ingest_file(path: Path):
    """Read a file and return chunk dicts ready for the vector store."""
    chunks = []
    for page, text in load_file(path):
        for j, c in enumerate(chunk_words(text)):
            chunks.append(
                {"id": f"{path.name}:{page}:{j}", "text": c, "source": path.name, "page": page}
            )
    return chunks
