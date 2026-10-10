from openai import OpenAI

from .config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL

_client = None


def generate(system: str, user: str) -> str:
    global _client
    if _client is None:
        local = "localhost" in LLM_BASE_URL or "127.0.0.1" in LLM_BASE_URL or "host.docker.internal" in LLM_BASE_URL
        if not LLM_API_KEY and not local:
            raise RuntimeError("LLM_API_KEY is not set. Copy .env.example to .env, or use local Ollama.")
        _client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY or "ollama", timeout=300)
    r = _client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.1,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return r.choices[0].message.content.strip()
