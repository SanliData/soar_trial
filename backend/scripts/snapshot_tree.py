from pathlib import Path

ROOTS = ["src", "tests", "docs", "scripts"]

out = Path("docs") / "TREE_SNAPSHOT.txt"
out.parent.mkdir(parents=True, exist_ok=True)

lines = []

for root in ROOTS:
    base = Path(root)
    if not base.exists():
        continue
    for path in sorted(base.rglob("*")):
        lines.append(str(path))

out.write_text("\n".join(lines), encoding="utf-8")
print(f"CREATED: {out}")
