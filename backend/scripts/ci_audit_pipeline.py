import subprocess
import sys

STEPS = [
    ("UTF-8 audit", ["python", "scripts/audit_utf8_no_bom.py"]),
    ("Pycache cleanup", ["python", "scripts/cleanup_pycache.py"]),
    ("Import graph audit", ["python", "scripts/audit_import_graph.py"]),
    ("Run tests", ["python", "-m", "pytest"]),
    ("Freeze manifest", ["python", "scripts/generate_freeze_manifest.py"]),
    ("Tree snapshot", ["python", "scripts/snapshot_tree.py"]),
]

def run_step(name, cmd):
    print(f"\n=== {name} ===")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"FAILED: {name}")
        sys.exit(1)
    print(f"OK: {name}")

if __name__ == "__main__":
    for name, cmd in STEPS:
        run_step(name, cmd)

    print("\nCI AUDIT PIPELINE PASSED ✅")
