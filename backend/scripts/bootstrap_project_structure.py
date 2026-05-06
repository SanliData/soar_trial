"""
BOOTSTRAP SCRIPT
PURPOSE: Create full Finder_OS backend directory structure
SCOPE: Folders only (no files)
SAFETY: Idempotent, audit-safe
"""

from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

DIRS = [
    ***REMOVED*** core
    "src",
    "src/http",
    "src/http/v1",
    "src/growth_activation",

    ***REMOVED*** future bounded contexts
    "src/matching",
    "src/records",
    "src/analytics",
    "src/notifications",
    "src/payments",

    ***REMOVED*** infrastructure
    "src/core",
    "src/core/config",
    "src/core/logging",
    "src/core/security",

    ***REMOVED*** persistence
    "src/db",
    "src/db/models",
    "src/db/migrations",

    ***REMOVED*** messaging / events
    "src/events",
    "src/events/schemas",

    ***REMOVED*** docs
    "docs",
    "docs/main_book",
    "docs/live_book",
    "docs/appendices",

    ***REMOVED*** tests
    "tests",
    "tests/growth_activation",
    "tests/http",
    "tests/core",

    ***REMOVED*** ops
    "scripts",
    "scripts/ops",

    ***REMOVED*** misc
    "logs",
    "tmp",
]

for rel in DIRS:
    path = BASE / rel
    path.mkdir(parents=True, exist_ok=True)
    print(f"OK: {rel}")
