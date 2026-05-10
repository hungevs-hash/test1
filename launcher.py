import subprocess
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
APP_FILE = APP_DIR / "app.py"

if not APP_FILE.exists():
    print("Cannot find app.py")
    sys.exit(1)

cmd = [sys.executable, "-m", "streamlit", "run", str(APP_FILE)]
subprocess.run(cmd, cwd=str(APP_DIR), check=False)
