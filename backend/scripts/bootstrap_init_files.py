"""
BOOTSTRAP SCRIPT
PURPOSE: Ensure __init__.py exists in all Python package directories
SCOPE: src/ and tests/ trees only
SAFETY: Idempotent, does not overwrite existing files
"""

from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TARGETS = [
    BASE / "src",
    BASE / "tests",
]

for root in TARGETS:
    for path in root.rglob("*"):
        if path.is_dir():
            init_file = path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                print(f"CREATED: {init_file.relative_to(BASE)}")
