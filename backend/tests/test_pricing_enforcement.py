"""
TEST: pricing_enforcement
PURPOSE: Test hard enforcement of quote tokens in query execution
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import pytest
from fastapi.testclient import TestClient
from src.app import create_app

***REMOVED*** Set test secrets
os.environ["QUOTE_SECRET"] = "test-secret-key-for-quote-tokens-12345"
os.environ["JWT_SECRET"] = "test-jwt-secret-key-12345"
os.environ["SOARB2B_API_KEYS"] = "test-api-key-12345"

app = create_app()
client = TestClient(app)


class TestPricingEnforcement:
    """Test hard enforcement of quote tokens"""
    
    def test_pricing_calculate_returns_quote_token(self):
        """Test that /pricing/calculate returns quote_token"""
        response = client.get("/v1/subscriptions/pricing/calculate")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "cost" in data
        assert "quote_token" in data
        assert "expires_at" in data
        assert "request_fingerprint" in data
        
        ***REMOVED*** Verify cost structure
        assert "total_cost" in data["cost"]
        assert "max_results" in data["cost"]
        assert data["cost"]["max_results"] == 100
    
    def test_pricing_calculate_with_modules(self):
        """Test pricing calculation with optional modules"""
        response = client.get(
            "/v1/subscriptions/pricing/calculate",
            params={
                "include_persona_deepening": "true",
                "include_export": "true"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["cost"]["total_cost"] > 1.99  ***REMOVED*** Should include module costs
        assert "quote_token" in data
    
    def test_query_execution_blocked_without_quote_token(self):
        """Test that query execution is blocked without quote_token"""
        response = client.post(
            "/api/v1/b2b/onboarding/create-plan",
            headers={"X-API-Key": "test-api-key-12345"},
            json={
                "target_type": "hotels",
                "geography": "Istanbul",
                "decision_roles": "procurement",
                "product_service": "cleaning services",
                "meeting_goal": "sales meeting",
                "auto_start_queries": True
                ***REMOVED*** quote_token missing
            }
        )
        
        ***REMOVED*** Should return 400 with error
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        ***REMOVED*** Check if it's the quote token error
        detail = data["detail"]
        if isinstance(detail, dict):
            assert detail.get("error_code") == "QUOTE_TOKEN_MISSING"
        else:
            ***REMOVED*** Might be string format
            assert "quote_token" in str(detail).lower() or "required" in str(detail).lower()
    
    def test_query_execution_with_valid_quote_token(self):
        """Test that query execution succeeds with valid quote_token"""
        ***REMOVED*** Step 1: Get quote token
        quote_response = client.get("/v1/subscriptions/pricing/calculate")
        assert quote_response.status_code == 200
        quote_data = quote_response.json()
        quote_token = quote_data["quote_token"]
        
        ***REMOVED*** Step 2: Execute query with valid quote token
        response = client.post(
            "/api/v1/b2b/onboarding/create-plan",
            headers={"X-API-Key": "test-api-key-12345"},
            json={
                "target_type": "hotels",
                "geography": "Istanbul",
                "decision_roles": "procurement",
                "product_service": "cleaning services",
                "meeting_goal": "sales meeting",
                "auto_start_queries": True,
                "quote_token": quote_token,
                "max_results": 100
            }
        )
        
        ***REMOVED*** Should succeed (200 or 201)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "plan_id" in data
    
    def test_query_execution_with_invalid_quote_token(self):
        """Test that query execution is blocked with invalid quote token"""
        response = client.post(
            "/api/v1/b2b/onboarding/create-plan",
            headers={"X-API-Key": "test-api-key-12345"},
            json={
                "target_type": "hotels",
                "geography": "Istanbul",
                "decision_roles": "procurement",
                "product_service": "cleaning services",
                "meeting_goal": "sales meeting",
                "auto_start_queries": True,
                "quote_token": "invalid.token.here",
                "max_results": 100
            }
        )
        
        ***REMOVED*** Should return 400
        assert response.status_code == 400
        data = response.json()
        detail = data.get("detail", {})
        if isinstance(detail, dict):
            assert detail.get("error_code") in [
                "QUOTE_TOKEN_INVALID_FORMAT",
                "QUOTE_TOKEN_INVALID_SIGNATURE",
                "QUOTE_TOKEN_VALIDATION_ERROR"
            ]
    
    def test_query_execution_with_fingerprint_mismatch(self):
        """Test that query execution is blocked with fingerprint mismatch"""
        ***REMOVED*** Get quote token with persona_deepening=True
        quote_response = client.get(
            "/v1/subscriptions/pricing/calculate",
            params={"include_persona_deepening": "true"}
        )
        quote_token = quote_response.json()["quote_token"]
        
        ***REMOVED*** Try to execute with persona_deepening=False (mismatch)
        response = client.post(
            "/api/v1/b2b/onboarding/create-plan",
            headers={"X-API-Key": "test-api-key-12345"},
            json={
                "target_type": "hotels",
                "geography": "Istanbul",
                "decision_roles": "procurement",
                "product_service": "cleaning services",
                "meeting_goal": "sales meeting",
                "auto_start_queries": True,
                "quote_token": quote_token,
                "include_persona_deepening": False,  ***REMOVED*** Mismatch!
                "max_results": 100
            }
        )
        
        ***REMOVED*** Should return 400
        assert response.status_code == 400
        data = response.json()
        detail = data.get("detail", {})
        if isinstance(detail, dict):
            assert detail.get("error_code") == "QUOTE_TOKEN_FINGERPRINT_MISMATCH"
    
    def test_max_results_enforced(self):
        """Test that max_results > 100 is rejected"""
        response = client.post(
            "/api/v1/b2b/onboarding/create-plan",
            headers={"X-API-Key": "test-api-key-12345"},
            json={
                "target_type": "hotels",
                "geography": "Istanbul",
                "decision_roles": "procurement",
                "product_service": "cleaning services",
                "meeting_goal": "sales meeting",
                "auto_start_queries": True,
                "quote_token": "dummy.token",
                "max_results": 200  ***REMOVED*** Exceeds limit
            }
        )
        
        ***REMOVED*** Should return 400
        assert response.status_code == 400
        data = response.json()
        detail = data.get("detail", {})
        if isinstance(detail, dict):
            assert detail.get("error_code") == "MAX_RESULTS_EXCEEDED"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
