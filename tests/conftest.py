"""Stub the heavy ML libs so tests run in seconds without downloading models."""
import hashlib
import os
import re
import sys
import tempfile
import types

import numpy as np

os.environ["DATA_DIR"] = tempfile.mkdtemp()
os.environ["USE_RERANK"] = "false"


class FakeEmbedder:
    def __init__(self, *a, **k):
        pass

    def encode(self, texts, normalize_embeddings=True, batch_size=32):
        out = []
        for t in texts:
            v = np.zeros(256)
            for w in re.findall(r"\w+", t.lower()):
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % 256] += 1
            out.append(v / (np.linalg.norm(v) or 1))
        return np.array(out)


class FakeCross:
    def __init__(self, *a, **k):
        pass

    def predict(self, pairs):
        return [float(len(set(q.split()) & set(d.split()))) for q, d in pairs]


st = types.ModuleType("sentence_transformers")
st.SentenceTransformer = FakeEmbedder
st.CrossEncoder = FakeCross
sys.modules["sentence_transformers"] = st

fw = types.ModuleType("faster_whisper")
fw.WhisperModel = object
sys.modules["faster_whisper"] = fw
