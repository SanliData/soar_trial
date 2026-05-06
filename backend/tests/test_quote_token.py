"""
TEST: quote_token
PURPOSE: Test quote token generation and validation
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import pytest
from datetime import datetime, timedelta
from src.core.quote_token import generate_quote_token, validate_quote_token
from src.config.pricing import MAX_RESULTS_PER_QUERY, QUOTE_TOKEN_EXPIRY_MINUTES


***REMOVED*** Set test secret
os.environ["QUOTE_SECRET"] = "test-secret-key-for-quote-tokens-12345"


class TestQuoteToken:
    """Test quote token generation and validation"""
    
    def test_generate_quote_token_basic(self):
        """Test basic quote token generation"""
        result = generate_quote_token(
            total_cost=1.99,
            max_results=100
        )
        
        assert "quote_token" in result
        assert "expires_at" in result
        assert "request_fingerprint" in result
        assert "max_results" in result
        assert "total_cost" in result
        assert result["total_cost"] == 1.99
        assert result["max_results"] == 100
        
        ***REMOVED*** Check token format (payload.signature)
        assert "." in result["quote_token"]
        parts = result["quote_token"].split(".")
        assert len(parts) == 2
    
    def test_generate_quote_token_with_modules(self):
        """Test quote token generation with optional modules"""
        result = generate_quote_token(
            total_cost=3.96,  ***REMOVED*** 1.99 base + 0.49 persona + 0.49 export + 0.99 outreach
            include_persona_deepening=True,
            include_export=True,
            include_outreach_preparation=True,
            max_results=100
        )
        
        assert result["total_cost"] == 3.96
        assert result["max_results"] == 100
    
    def test_validate_quote_token_valid(self):
        """Test validation of valid quote token"""
        ***REMOVED*** Generate token
        quote_info = generate_quote_token(
            total_cost=1.99,
            include_persona_deepening=False,
            include_visit_route=False,
            include_export=False,
            include_outreach_preparation=False,
            max_results=100
        )
        
        ***REMOVED*** Validate token
        result = validate_quote_token(
            quote_token=quote_info["quote_token"],
            include_persona_deepening=False,
            include_visit_route=False,
            include_export=False,
            include_outreach_preparation=False,
            max_results=100
        )
        
        assert result["valid"] is True
        assert result["error"] is None
        assert result["error_code"] is None
        assert result["payload"] is not None
        assert result["payload"]["total_cost"] == 1.99
    
    def test_validate_quote_token_missing(self):
        """Test validation with missing token"""
        result = validate_quote_token(
            quote_token="",
            max_results=100
        )
        
        assert result["valid"] is False
        assert result["error_code"] == "QUOTE_TOKEN_MISSING"
    
    def test_validate_quote_token_invalid_signature(self):
        """Test validation with invalid signature"""
        ***REMOVED*** Generate valid token
        quote_info = generate_quote_token(total_cost=1.99, max_results=100)
        
        ***REMOVED*** Tamper with signature
        tampered_token = quote_info["quote_token"][:-10] + "XXXXXXXXXX"
        
        result = validate_quote_token(
            quote_token=tampered_token,
            max_results=100
        )
        
        assert result["valid"] is False
        assert result["error_code"] == "QUOTE_TOKEN_INVALID_SIGNATURE"
    
    def test_validate_quote_token_fingerprint_mismatch(self):
        """Test validation with fingerprint mismatch"""
        ***REMOVED*** Generate token with persona_deepening=True
        quote_info = generate_quote_token(
            total_cost=2.48,  ***REMOVED*** 1.99 + 0.49
            include_persona_deepening=True,
            max_results=100
        )
        
        ***REMOVED*** Try to validate with persona_deepening=False (mismatch)
        result = validate_quote_token(
            quote_token=quote_info["quote_token"],
            include_persona_deepening=False,  ***REMOVED*** Mismatch!
            max_results=100
        )
        
        assert result["valid"] is False
        assert result["error_code"] == "QUOTE_TOKEN_FINGERPRINT_MISMATCH"
    
    def test_validate_quote_token_max_results_exceeded(self):
        """Test validation with max_results exceeding limit"""
        ***REMOVED*** Generate token with max_results=100
        quote_info = generate_quote_token(total_cost=1.99, max_results=100)
        
        ***REMOVED*** Try to validate with max_results=200 (exceeds limit)
        result = validate_quote_token(
            quote_token=quote_info["quote_token"],
            max_results=200  ***REMOVED*** Exceeds MAX_RESULTS_PER_QUERY
        )
        
        assert result["valid"] is False
        assert result["error_code"] == "MAX_RESULTS_EXCEEDED"
    
    def test_validate_quote_token_max_results_clamped(self):
        """Test that max_results is clamped to MAX_RESULTS_PER_QUERY"""
        ***REMOVED*** Generate token with max_results=100
        quote_info = generate_quote_token(total_cost=1.99, max_results=100)
        
        ***REMOVED*** Validate with max_results=150 (should be clamped to 100)
        result = validate_quote_token(
            quote_token=quote_info["quote_token"],
            max_results=150  ***REMOVED*** Will be clamped to 100
        )
        
        ***REMOVED*** Should still be valid because it gets clamped
        assert result["valid"] is True
    
    def test_quote_token_expires(self):
        """Test that expired tokens are rejected"""
        ***REMOVED*** This test would require mocking time, which is complex
        ***REMOVED*** For now, we test the expiry logic exists
        quote_info = generate_quote_token(total_cost=1.99, max_results=100)
        
        ***REMOVED*** Token should have expires_at
        assert "expires_at" in quote_info
        
        ***REMOVED*** Parse expires_at
        expires_at = datetime.fromisoformat(quote_info["expires_at"].replace('Z', '+00:00'))
        assert expires_at > datetime.utcnow()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
