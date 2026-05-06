from pathlib import Path

ROOTS = ["src", "tests"]

violations = []

for root in ROOTS:
    base = Path(root)
    if not base.exists():
        continue

    for py_file in base.rglob("*.py"):
        data = py_file.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            violations.append(str(py_file))

if violations:
    print("BOM VIOLATIONS FOUND:")
    for v in violations:
        print(" -", v)
    raise SystemExit(1)

print("OK: no BOM detected in src/ and tests/")
