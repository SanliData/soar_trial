"""
TEST: Canonical task documentation baseline files exist at repo root.
ENCODING: UTF-8 WITHOUT BOM
"""

from pathlib import Path


def test_task_implementation_standard_doc_exists():
    root = Path(__file__).resolve().parents[2]
    doc = root / "docs" / "TASK_IMPLEMENTATION_AND_PROOF_STANDARD.md"
    assert doc.is_file()


def test_task_standard_proof_doc_exists():
    root = Path(__file__).resolve().parents[2]
    doc = root / "docs" / "TASK_STANDARD_IMPLEMENTATION_PROOF.md"
    assert doc.is_file()
