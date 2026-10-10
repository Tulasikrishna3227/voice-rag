"""Retrieval hit-rate and answer correctness, with and without reranking.

    python -m eval.eval             # full (needs the LLM running)
    python -m eval.eval --no-llm    # retrieval only
    python -m eval.eval --no-sample --file my_questions.json   # your own docs/questions

A question counts as correct if ANY string in "any_of" appears in the answer.
"""
import argparse
import json
from pathlib import Path

from app import rag
from app.config import SAMPLE_DIR
from app.ingest import ingest_file


def run(questions, rerank: bool, use_llm: bool):
    hit = correct = 0
    for q in questions:
        res = rag.answer(q["question"], rerank=rerank, use_llm=use_llm)
        if any(s["source"] == q["source"] and s["page"] == q["page"] for s in res["sources"]):
            hit += 1
        if use_llm and any(k.lower() in res["answer"].lower() for k in q["any_of"]):
            correct += 1
    n = len(questions)
    return hit / n, (correct / n if use_llm else None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--no-sample", action="store_true", help="don't index data/sample first")
    ap.add_argument("--file", default=str(Path(__file__).parent / "questions.json"))
    a = ap.parse_args()
    if not a.no_sample:
        for p in sorted(SAMPLE_DIR.glob("*.txt")):
            rag.store.add(ingest_file(p))
    qs = json.loads(Path(a.file).read_text(encoding="utf-8"))
    print(f"{len(qs)} questions\n")
    print("| Setup | Retrieval hit-rate | Answer correctness |\n|---|---|---|")
    for name, rr in [("No rerank", False), ("With rerank", True)]:
        h, c = run(qs, rr, not a.no_llm)
        print(f"| {name} | {h:.0%} | {'n/a' if c is None else f'{c:.0%}'} |")
