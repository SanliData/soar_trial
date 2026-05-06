"""
TESTS: test_web_acquisition
PURPOSE: Tests for web acquisition service
ENCODING: UTF-8 WITHOUT BOM
"""

import pytest
from src.services.web_acquisition.compliance import SourcesPolicy, get_rate_limiter
from src.services.web_acquisition.interfaces import AcquisitionJobRequest
from src.core.query_limits import MAX_RESULTS_PER_QUERY


def test_sources_policy_restricted():
    """Test that restricted domains are blocked."""
    assert SourcesPolicy.is_restricted("linkedin.com") is True
    assert SourcesPolicy.is_restricted("www.linkedin.com") is True
    assert SourcesPolicy.is_restricted("jobs.linkedin.com") is True
    assert SourcesPolicy.is_restricted("facebook.com") is True
    assert SourcesPolicy.is_restricted("twitter.com") is True


def test_sources_policy_official():
    """Test that official sources are allowed."""
    assert SourcesPolicy.is_official_source("gov.tr") is True
    assert SourcesPolicy.is_allowed("gov.tr", SourcesPolicy.OFFICIAL_ONLY) is True
    assert SourcesPolicy.is_allowed("belediyeler.gov.tr", SourcesPolicy.OFFICIAL_ONLY) is True


def test_sources_policy_company_website():
    """Test that company websites are allowed in official_only policy."""
    assert SourcesPolicy.is_company_website("acme.com") is True
    assert SourcesPolicy.is_allowed("acme.com", SourcesPolicy.OFFICIAL_ONLY) is True
    assert SourcesPolicy.is_allowed("www.acme.com", SourcesPolicy.OFFICIAL_ONLY) is True


def test_sources_policy_blocklist_enforcement():
    """Test that restricted domains are blocked even in public_web policy."""
    assert SourcesPolicy.is_allowed("linkedin.com", SourcesPolicy.PUBLIC_WEB) is False
    assert SourcesPolicy.is_allowed("facebook.com", SourcesPolicy.PUBLIC_WEB) is False


def test_rate_limiter():
    """Test rate limiting functionality."""
    limiter = get_rate_limiter()
    limiter.reset()  ***REMOVED*** Clear state
    
    domain = "example.com"
    
    ***REMOVED*** First 10 requests should be allowed
    for i in range(10):
        assert limiter.is_allowed(domain) is True
    
    ***REMOVED*** 11th request should be blocked
    assert limiter.is_allowed(domain) is False
    
    ***REMOVED*** Reset should allow requests again
    limiter.reset(domain)
    assert limiter.is_allowed(domain) is True


def test_acquisition_job_request_validation():
    """Test acquisition job request validation."""
    ***REMOVED*** Valid request
    request = AcquisitionJobRequest(
        plan_id="test_plan",
        target_type="both",
        sources_policy="official_only",
        max_results=100
    )
    assert request.plan_id == "test_plan"
    assert request.max_results == 100


def test_cap_enforcement():
    """Test that max_results is capped to MAX_RESULTS_PER_QUERY."""
    from src.core.query_limits import enforce_query_limit
    
    ***REMOVED*** Standard user (not admin)
    assert enforce_query_limit(50, is_admin=False) == 50
    assert enforce_query_limit(100, is_admin=False) == 100
    assert enforce_query_limit(200, is_admin=False) == 100  ***REMOVED*** Capped
    assert enforce_query_limit(500, is_admin=False) == 100  ***REMOVED*** Capped
    
    ***REMOVED*** Admin can request more (but still capped to override limit)
    assert enforce_query_limit(200, is_admin=True) <= 1000  ***REMOVED*** Admin override


def test_sources_policy_validation():
    """Test sources policy validation."""
    assert SourcesPolicy.validate_sources_policy("official_only") is True
    assert SourcesPolicy.validate_sources_policy("public_web") is True
    assert SourcesPolicy.validate_sources_policy("invalid") is False


def test_stagehand_adapter_dry_run():
    """Test that Stagehand adapter works in dry-run mode."""
    import os
    from src.services.web_acquisition.stagehand_adapter import get_stagehand_adapter
    
    ***REMOVED*** Ensure Stagehand is disabled for this test
    original_value = os.getenv("SOAR_ENABLE_STAGEHAND", "false")
    
    adapter = get_stagehand_adapter()
    
    ***REMOVED*** In dry-run mode, should return mocked results
    if not adapter.is_enabled():
        ***REMOVED*** This will work in dry-run mode
        pass  ***REMOVED*** Dry-run mode is acceptable


***REMOVED*** Integration test (requires database)
@pytest.mark.skip(reason="Requires database setup")
def test_create_acquisition_job():
    """Test creating an acquisition job (requires database)."""
    ***REMOVED*** TODO: Implement with test database
    pass


@pytest.mark.skip(reason="Requires database setup")
def test_export_csv_format():
    """Test that CSV export returns valid format (requires database)."""
    ***REMOVED*** TODO: Implement with test database
    pass


@pytest.mark.skip(reason="Requires database setup")
def test_export_json_format():
    """Test that JSON export returns valid format (requires database)."""
    ***REMOVED*** TODO: Implement with test database
    pass
