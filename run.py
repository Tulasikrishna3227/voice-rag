"""Start API + UI with one command:  python run.py"""
import subprocess
import sys
import threading
import time
import webbrowser

procs = [
    subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"]),
    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "ui.py",
         "--server.port", "8501", "--server.headless", "true"]
    ),
]

# headless mode skips Streamlit's email prompt but doesn't open a browser, so do it here
threading.Thread(
    target=lambda: (time.sleep(10), webbrowser.open("http://localhost:8501")), daemon=True
).start()

try:
    for p in procs:
        p.wait()
except KeyboardInterrupt:
    for p in procs:
        p.terminate()
