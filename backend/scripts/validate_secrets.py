***REMOVED***!/usr/bin/env python3
"""
Validation script to test Secret Manager integration.
Tests both Secret Manager and environment variable fallback.
"""

import os
import sys
import json

***REMOVED*** Add backend/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from src.core.secret_manager import SecretManager, get_secret_manager
    from src.services.auth_service import AuthService
    print("✓ Imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

def test_secret_manager():
    """Test Secret Manager functionality"""
    print("\n=== Testing Secret Manager ===")
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "finderos-entegrasyon-480708")
    secret_mgr = SecretManager(project_id=project_id)
    
    print(f"Project ID: {project_id}")
    print(f"Secret Manager available: {secret_mgr.is_available()}")
    
    ***REMOVED*** Test reading secrets
    google_client_id = secret_mgr.get_secret("GOOGLE_CLIENT_ID")
    jwt_secret = secret_mgr.get_secret("JWT_SECRET")
    
    print(f"GOOGLE_CLIENT_ID: {'✓ Found' if google_client_id else '✗ Not found'}")
    print(f"JWT_SECRET: {'✓ Found' if jwt_secret else '✗ Not found'}")
    
    if google_client_id:
        print(f"  Value: {google_client_id[:20]}...")
    if jwt_secret:
        print(f"  Value: {'*' * min(len(jwt_secret), 20)}... (length: {len(jwt_secret)})")
    
    return google_client_id and jwt_secret

def test_auth_service():
    """Test AuthService configuration"""
    print("\n=== Testing AuthService ===")
    
    auth_service = AuthService()
    
    print(f"Google Client ID set: {bool(auth_service.google_client_id)}")
    print(f"JWT Secret set: {bool(auth_service.jwt_secret)}")
    print(f"Is configured: {auth_service.is_configured()}")
    
    if auth_service.google_client_id:
        print(f"  Client ID: {auth_service.google_client_id[:20]}...")
    if auth_service.jwt_secret:
        print(f"  JWT Secret length: {len(auth_service.jwt_secret)}")
        if len(auth_service.jwt_secret) < 64:
            print("  ⚠ WARNING: JWT_SECRET should be at least 64 bytes (86 chars)")
    
    return auth_service.is_configured()

def main():
    """Run all tests"""
    print("Secret Manager Validation")
    print("=" * 50)
    
    ***REMOVED*** Test Secret Manager
    secret_mgr_ok = test_secret_manager()
    
    ***REMOVED*** Test AuthService
    auth_service_ok = test_auth_service()
    
    ***REMOVED*** Summary
    print("\n=== Summary ===")
    print(f"Secret Manager: {'✓ PASS' if secret_mgr_ok else '✗ FAIL'}")
    print(f"AuthService: {'✓ PASS' if auth_service_ok else '✗ FAIL'}")
    
    if secret_mgr_ok and auth_service_ok:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
