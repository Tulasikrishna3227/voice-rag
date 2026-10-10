import chromadb
from sentence_transformers import SentenceTransformer

from .config import CHROMA_DIR, EMBED_MODEL


class Store:
    def __init__(self):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.col = self.client.get_or_create_collection("docs", metadata={"hnsw:space": "cosine"})

    def _embed(self, texts, prefix):
        # e5 models expect "query: " / "passage: " prefixes
        return self.model.encode(
            [prefix + t for t in texts], normalize_embeddings=True, batch_size=32
        ).tolist()

    def add(self, chunks):
        if not chunks:
            return 0
        for i in range(0, len(chunks), 128):
            b = chunks[i : i + 128]
            self.col.upsert(
                ids=[c["id"] for c in b],
                documents=[c["text"] for c in b],
                metadatas=[{"source": c["source"], "page": c["page"]} for c in b],
                embeddings=self._embed([c["text"] for c in b], "passage: "),
            )
        return len(chunks)

    def search(self, query, k=20):
        n = self.col.count()
        if n == 0:
            return []
        r = self.col.query(
            query_embeddings=self._embed([query], "query: "), n_results=min(k, n)
        )
        return [
            {"text": d, "source": m["source"], "page": m["page"], "score": 1 - dist}
            for d, m, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0])
        ]

    def sources(self):
        metas = self.col.get(include=["metadatas"])["metadatas"]
        return sorted({m["source"] for m in metas})

    def reset(self):
        self.client.delete_collection("docs")
        self.col = self.client.get_or_create_collection("docs", metadata={"hnsw:space": "cosine"})
