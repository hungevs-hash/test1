from datetime import datetime
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
db = root / "data.db"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

if not db.exists():
    print("data.db not found, nothing to backup")
    raise SystemExit(0)

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out = backup_dir / f"data_{ts}.db"
shutil.copy2(db, out)
print(f"backup created: {out}")
