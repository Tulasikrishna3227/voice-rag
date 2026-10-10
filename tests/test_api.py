from fastapi.testclient import TestClient

from app import rag, voice
from app.main import app

client = TestClient(app)


def test_end_to_end(monkeypatch):
    monkeypatch.setattr(rag, "generate", lambda system, user: "The fee is 300 rupees [1].")
    client.delete("/reset")
    assert client.post("/load-sample").json()["chunks"] >= 6
    assert "clinic_en.txt" in client.get("/sources").json()["sources"]

    r = client.post("/ask", json={"question": "What is the consultation fee at Sunrise Clinic?"})
    j = r.json()
    assert r.status_code == 200 and j["language"] == "en"
    assert j["sources"][0]["source"] == "clinic_en.txt"
    assert "300" in j["answer"]


def test_upload_and_voice(monkeypatch):
    monkeypatch.setattr(rag, "generate", lambda system, user: "300 [1]")
    monkeypatch.setattr(voice, "transcribe", lambda path: ("What is the consultation fee?", "en"))

    async def fake_tts(text, lang, out_path):
        assert "[1]" not in text  # citations stripped before speech
        open(out_path, "wb").write(b"ID3")

    monkeypatch.setattr(voice, "synthesize", fake_tts)

    up = client.post("/upload", files=[("files", ("note.txt", b"The consultation fee is 300 rupees today."))])
    assert up.json()["results"][0]["chunks"] >= 1

    r = client.post("/ask-voice", files={"file": ("q.wav", b"RIFF....")})
    j = r.json()
    assert r.status_code == 200 and j["transcript"].startswith("What is")
    assert client.get(j["audio_url"]).status_code == 200


def test_bad_upload_type():
    r = client.post("/upload", files=[("files", ("x.exe", b"x"))])
    assert "error" in r.json()["results"][0]
