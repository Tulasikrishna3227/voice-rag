"""Start API + UI with one command:  python run.py"""
import subprocess
import sys

procs = [
    subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"]),
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "ui.py", "--server.port", "8501"]),
]
try:
    for p in procs:
        p.wait()
except KeyboardInterrupt:
    for p in procs:
        p.terminate()
