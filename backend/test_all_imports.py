import sys
sys.path.insert(0, '.')

errors = []
warnings = []

def test_import(module_name, description=""):
    try:
        __import__(module_name)
        print(f"[OK] {module_name}" + (f" - {description}" if description else ""))
        return True
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)[:100]}"
        print(f"[ERROR] {module_name}")
        print(f"        {error_msg}")
        errors.append((module_name, error_msg, str(e)))
        return False

print("=" * 70)
print("FINDER_OS - COMPREHENSIVE IMPORT TEST")
print("=" * 70)

***REMOVED*** Test 1: Core dependencies
print("\n[1] Testing Core Dependencies...")
test_import("fastapi", "FastAPI framework")
test_import("uvicorn", "ASGI server")
test_import("sqlalchemy", "ORM")
test_import("pydantic", "Data validation")

***REMOVED*** Test 2: Database
print("\n[2] Testing Database...")
test_import("src.db.base")

***REMOVED*** Test 3: Models (skip auth_service for now)
print("\n[3] Testing Models...")
test_import("src.models.user")
test_import("src.models.company")
test_import("src.models.product")
test_import("src.models.persona")
test_import("src.models.campaign")

***REMOVED*** Test 4: Services (skip auth_service)
print("\n[4] Testing Services (excluding auth_service)...")
test_import("src.services.vision_service")
test_import("src.services.geocoding_service")
test_import("src.services.google_ads_service")
test_import("src.services.payment_service")

***REMOVED*** Test 5: Routers (will fail at auth_service)
print("\n[5] Testing Routers...")
test_import("src.http.v1.livebook_endpoints")
test_import("src.http.v1.matching_router")
test_import("src.http.v1.analytics_router")
test_import("src.http.v1.records_router")

***REMOVED*** Test 6: Auth Service (known issue)
print("\n[6] Testing Auth Service (KNOWN ISSUE)...")
test_import("src.services.auth_service", "This will fail - Header=None issue")

***REMOVED*** Test 7: Router Registry (will fail due to auth_service)
print("\n[7] Testing Router Registry (will fail due to auth_service)...")
test_import("src.http.v1.router_registry")

***REMOVED*** Test 8: App (will fail due to router_registry)
print("\n[8] Testing App (will fail due to router_registry)...")
test_import("src.app")

***REMOVED*** Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total Errors Found: {len(errors)}")

if errors:
    print("\nERROR DETAILS:")
    for i, (module, msg, detail) in enumerate(errors, 1):
        print(f"\n{i}. {module}")
        print(f"   Error: {msg}")
        if len(detail) < 150:
            print(f"   Full: {detail[:150]}")
else:
    print("\n[SUCCESS] All imports successful!")

print("\n" + "=" * 70)
