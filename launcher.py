import subprocess
import sys
import time
import webbrowser
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
APP_FILE = APP_DIR / "app.py"
LOG_DIR = APP_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "launcher.log"
URL = "http://localhost:8501"


def log(msg: str):
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main():
    if not APP_FILE.exists():
        log("ERROR: app.py not found")
        print("Cannot find app.py")
        sys.exit(1)

    cmd = [sys.executable, "-m", "streamlit", "run", str(APP_FILE), "--server.headless=true"]
    log(f"Starting: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=str(APP_DIR))
    time.sleep(4)
    webbrowser.open(URL)
    code = proc.wait()
    log(f"Exited with code: {code}")
    sys.exit(code)


if __name__ == "__main__":
    main()
