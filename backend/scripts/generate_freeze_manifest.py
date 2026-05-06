from pathlib import Path

FROZEN = [
    "growth_activation",
    "matching",
    "analytics",
    "records",
]

out = Path("docs") / "FREEZE_MANIFEST.md"
out.parent.mkdir(parents=True, exist_ok=True)

lines = ["***REMOVED*** FREEZE MANIFEST\n", "\n", "The following bounded contexts are frozen:\n", "\n"]
for item in FROZEN:
    lines.append(f"- {item}\n")

out.write_text("".join(lines), encoding="utf-8")

print("FROZEN:")
for item in FROZEN:
    print("-", item)
print(f"CREATED: {out}")
