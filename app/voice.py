import edge_tts
from faster_whisper import WhisperModel

from .config import WHISPER_MODEL

VOICES = {
    "te": "te-IN-ShrutiNeural",
    "hi": "hi-IN-SwaraNeural",
    "en": "en-IN-NeerjaNeural",
}
_whisper = None


def detect_lang(text: str) -> str:
    """Cheap script-based detection: Telugu / Devanagari (Hindi) / else English."""
    te = sum("\u0c00" <= ch <= "\u0c7f" for ch in text)
    hi = sum("\u0900" <= ch <= "\u097f" for ch in text)
    if te > hi and te > 0:
        return "te"
    if hi > 0:
        return "hi"
    return "en"


def transcribe(path: str):
    """Speech to text. Returns (text, language_code)."""
    global _whisper
    if _whisper is None:
        _whisper = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, info = _whisper.transcribe(path, beam_size=5)
    text = " ".join(s.text.strip() for s in segments).strip()
    lang = info.language if info.language in VOICES else detect_lang(text)
    return text, lang


async def synthesize(text: str, lang: str, out_path: str):
    """Text to speech with edge-tts (free)."""
    await edge_tts.Communicate(text, VOICES.get(lang, VOICES["en"])).save(out_path)
