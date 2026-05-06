from pathlib import Path
import shutil
import os
import stat

ROOTS = ["src", "tests"]

def onerror(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        print(f"SKIPPED (locked): {path}")

removed = False

for root in ROOTS:
    base = Path(root)
    if not base.exists():
        continue

    for pycache in base.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache, onerror=onerror)
            print(f"REMOVED: {pycache}")
            removed = True
        except Exception:
            print(f"SKIPPED (locked): {pycache}")

if not removed:
    print("OK: no __pycache__ found")
