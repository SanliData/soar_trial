from pathlib import Path

FORBIDDEN = [
    "src.http",
    "fastapi",
]

violations = []

def check_file(path: Path):
    text = path.read_text(encoding="utf-8")
    for forbidden in FORBIDDEN:
        if forbidden in text:
            violations.append(f"{path} imports {forbidden}")

for domain in ["analytics", "growth_activation", "matching", "records"]:
    base = Path("src") / domain
    if not base.exists():
        continue

    for py in base.rglob("*.py"):
        check_file(py)

if violations:
    print("IMPORT GRAPH VIOLATIONS:")
    for v in violations:
        print(" -", v)
    raise SystemExit(1)

print("OK: no forbidden imports detected")
