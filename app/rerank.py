from sentence_transformers import CrossEncoder

from .config import RERANK_MODEL


class Reranker:
    def __init__(self):
        self.model = None  # lazy load

    def rerank(self, query, hits, top_n):
        if not hits:
            return []
        if self.model is None:
            self.model = CrossEncoder(RERANK_MODEL)
        scores = self.model.predict([(query, h["text"]) for h in hits])
        for h, s in zip(hits, scores):
            h["rerank_score"] = float(s)
        return sorted(hits, key=lambda h: -h["rerank_score"])[:top_n]
