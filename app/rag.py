from .config import TOP_K_RETRIEVE, TOP_K_FINAL, USE_RERANK
from .llm import generate
from .rerank import Reranker
from .store import Store
from .voice import detect_lang

store = Store()
reranker = Reranker()

LANG_NAMES = {"te": "Telugu", "hi": "Hindi", "en": "English"}

SYSTEM = (
    "You are a document assistant. Answer ONLY from the numbered context passages. "
    "Reply in {language}. Cite passages inline like [1], [2]. "
    "If the answer is not in the context, say you don't know in {language}. Do not invent facts."
)


def retrieve(question: str, rerank: bool | None = None):
    rerank = USE_RERANK if rerank is None else rerank
    hits = store.search(question, k=TOP_K_RETRIEVE)
    if rerank:
        return reranker.rerank(question, hits, TOP_K_FINAL)
    return hits[:TOP_K_FINAL]


def answer(question: str, lang: str | None = None, rerank: bool | None = None, use_llm: bool = True):
    lang = lang or detect_lang(question)
    hits = retrieve(question, rerank)
    if not hits:
        return {"answer": "No documents indexed yet.", "language": lang, "sources": []}
    text = ""
    if use_llm:
        context = "\n\n".join(
            f"[{i + 1}] ({h['source']} p.{h['page']})\n{h['text']}" for i, h in enumerate(hits)
        )
        text = generate(
            SYSTEM.format(language=LANG_NAMES[lang]),
            f"Context:\n{context}\n\nQuestion: {question}",
        )
    sources = [
        {"id": i + 1, "source": h["source"], "page": h["page"], "snippet": h["text"][:300]}
        for i, h in enumerate(hits)
    ]
    return {"answer": text, "language": lang, "sources": sources}
