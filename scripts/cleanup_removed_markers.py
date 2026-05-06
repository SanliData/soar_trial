#!/usr/bin/env python3
"""
SCRIPT: cleanup_removed_markers
PURPOSE: Remove git-filter-repo default '***REMOVED***' markers from source files.

This repo historically used git-filter-repo for sensitive data removal.
If replace-text patterns were too broad (or default replacements were applied),
git-filter-repo can leave literal markers like '***REMOVED***' that break syntax
in Python files.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = [
    ROOT / "backend" / "src",
]

MARKER = "***REMOVED***"
INLINE = "<REDACTED>"


def _clean_python(text: str) -> str:
    out_lines: list[str] = []
    for line in text.splitlines(True):
        if MARKER not in line and INLINE not in line:
            out_lines.append(line)
            continue
        # If marker is on a standalone "comment-like" separator line, convert to a real comment.
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if stripped.startswith(MARKER):
            rest = stripped[len(MARKER) :].rstrip("\r\n")
            out_lines.append(f"{indent}# {rest.strip()}\n")
        else:
            new_line = line
            # Convert inline markers to comments.
            new_line = new_line.replace(MARKER, "")
            if INLINE in new_line:
                # Most occurrences were appended as an inline comment marker.
                new_line = new_line.replace(f" {INLINE} ", "  # ")
                new_line = new_line.replace(f"\t{INLINE}\t", "\t#\t")
                new_line = new_line.replace(f" {INLINE}", "  #")
                new_line = new_line.replace(INLINE, "#")
            out_lines.append(new_line)
    return "".join(out_lines)


def main() -> int:
    changed = 0
    scanned = 0
    for base in TARGET_DIRS:
        for p in base.rglob("*.py"):
            scanned += 1
            txt = p.read_text(encoding="utf-8", errors="replace")
            if MARKER not in txt and INLINE not in txt:
                continue
            new_txt = _clean_python(txt)
            if new_txt != txt:
                p.write_text(new_txt, encoding="utf-8")
                changed += 1
    print(f"cleanup_removed_markers: scanned={scanned} changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

