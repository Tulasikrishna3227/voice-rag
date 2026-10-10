import os
import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="Voice RAG", page_icon="🎙️")
st.title("🎙️ Voice RAG: Telugu · Hindi · English")

with st.sidebar:
    st.header("Documents")
    files = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt", "md"], accept_multiple_files=True)
    if files and st.button("Index"):
        r = requests.post(
            f"{API}/upload", files=[("files", (f.name, f.getvalue())) for f in files], timeout=600
        )
        st.json(r.json())
    if st.button("Load sample docs (EN/TE/HI)"):
        st.json(requests.post(f"{API}/load-sample", timeout=300).json())
    try:
        st.write("Indexed:", requests.get(f"{API}/sources", timeout=10).json()["sources"])
    except Exception:
        st.error("API not reachable. Start it first.")
    if st.button("Reset index"):
        requests.delete(f"{API}/reset", timeout=30)
        st.rerun()


def show(res):
    st.markdown(res["answer"])
    with st.expander("Sources"):
        for s in res["sources"]:
            st.caption(f"[{s['id']}] {s['source']} · page {s['page']}")
            st.write(s["snippet"] + "…")


tab_text, tab_voice = st.tabs(["Text", "Voice"])

with tab_text:
    q = st.text_input("Ask a question (Telugu / Hindi / English)")
    if q:
        r = requests.post(f"{API}/ask", json={"question": q}, timeout=300)
        if r.ok:
            show(r.json())
        else:
            st.error(r.text)

with tab_voice:
    audio = st.audio_input("Record your question")
    if audio and st.button("Ask by voice"):
        r = requests.post(
            f"{API}/ask-voice", files={"file": (audio.name or "q.wav", audio.getvalue())}, timeout=300
        )
        if r.ok:
            res = r.json()
            st.write(f"**You said:** {res['transcript']}")
            show(res)
            st.audio(requests.get(API + res["audio_url"], timeout=60).content, format="audio/mp3")
        else:
            st.error(r.text)
