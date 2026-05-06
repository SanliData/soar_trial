"""
Tests: UPAP hard filters (company_size_max=50, company_limit=100) and evidence.
"""

import pytest
from src.core.upap_limits import (
    COMPANY_SIZE_MAX,
    COMPANY_LIMIT,
    passes_company_size_max,
    filter_rows_by_upap,
    _parse_company_size_max,
)


class TestParseCompanySizeMax:
    def test_range_1_10(self):
        assert _parse_company_size_max("1-10") == 10

    def test_range_11_50(self):
        assert _parse_company_size_max("11-50") == 50

    def test_range_51_200(self):
        assert _parse_company_size_max("51-200") == 200

    def test_single_number(self):
        assert _parse_company_size_max("50") == 50
        assert _parse_company_size_max("100") == 100

    def test_empty_or_none(self):
        assert _parse_company_size_max("") is None
        assert _parse_company_size_max(None) is None


class TestPassesCompanySizeMax:
    def test_pass(self):
        assert passes_company_size_max("1-10") is True
        assert passes_company_size_max("11-50") is True
        assert passes_company_size_max("1-50") is True
        assert passes_company_size_max("50") is True

    def test_fail(self):
        assert passes_company_size_max("51-200") is False
        assert passes_company_size_max("201-500") is False
        assert passes_company_size_max("100") is False

    def test_unknown_allowed(self):
        assert passes_company_size_max("") is True
        assert passes_company_size_max(None) is True


class TestFilterRowsByUpap:
    def test_empty_rows_fail(self):
        rows = []
        out, ev = filter_rows_by_upap(rows, "trace-1", "run-1")
        assert out == []
        assert ev["status"] == "FAIL"
        assert ev["reason"] == "no_rows"
        assert ev["trace_id"] == "trace-1"
        assert ev["run_id"] == "run-1"
        assert "timestamp" in ev

    def test_pass_under_limit(self):
        rows = [
            {"company_name": "A", "company_size": "11-50"},
            {"company_name": "B", "company_size": "1-10"},
        ]
        out, ev = filter_rows_by_upap(rows, "t", "r")
        assert len(out) == 2
        assert ev["status"] == "PASS"
        assert ev["rows_before"] == 2
        assert ev["rows_after"] == 2
        assert ev["limit"] == COMPANY_LIMIT
        assert ev["company_size_max"] == COMPANY_SIZE_MAX

    def test_reject_over_50(self):
        rows = [
            {"company_name": "A", "company_size": "11-50"},
            {"company_name": "B", "company_size": "51-200"},
            {"company_name": "C", "company_size": "201-500"},
        ]
        out, ev = filter_rows_by_upap(rows, "t", "r")
        assert len(out) == 1
        assert out[0]["company_name"] == "A"
        assert ev["rejected_size_count"] == 2
        assert ev["rows_after"] == 1
        assert ev["status"] == "PASS"

    def test_all_rejected_fail(self):
        rows = [
            {"company_name": "X", "company_size": "51-200"},
            {"company_name": "Y", "company_size": "100"},
        ]
        out, ev = filter_rows_by_upap(rows, "t", "r")
        assert len(out) == 0
        assert ev["status"] == "FAIL"
        assert ev["reason"] == "no_rows_after_upap_filters"
        assert ev["rows_after"] == 0
        assert ev["rejected_size_count"] == 2

    def test_cap_at_100(self):
        rows = [{"company_name": f"C{i}", "company_size": "1-10"} for i in range(150)]
        out, ev = filter_rows_by_upap(rows, "t", "r")
        assert len(out) == COMPANY_LIMIT
        assert ev["rows_after"] == 100
        assert ev["status"] == "PASS"
        assert ev["reason"] == "capped_to_company_limit"
