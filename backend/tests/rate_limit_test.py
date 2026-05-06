"""
RATE LIMIT TEST: rate_limit_test
PURPOSE: Test rate limiting with 150 req/min (expect 100 OK, 50 blocked)
ENCODING: UTF-8 WITHOUT BOM
"""

import asyncio
import time
import json
from datetime import datetime
from typing import List, Dict, Any

import httpx

***REMOVED*** Test configuration
BASE_URL = "https://soarb2b.com"  ***REMOVED*** Production URL
***REMOVED*** BASE_URL = "http://localhost:8000"  ***REMOVED*** Local testing
API_KEY = "<REDACTED_SOARB2B_API_KEY>"

***REMOVED*** Expected rate limit: 100 req/min
EXPECTED_LIMIT = 100
TEST_REQUESTS = 150  ***REMOVED*** Should get 100 OK + 50 429


async def test_rate_limit():
    """Test rate limiting by sending 150 requests in 1 minute"""
    print("=" * 70)
    print("RATE LIMIT TEST")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Expected limit: {EXPECTED_LIMIT} req/min")
    print(f"Test requests: {TEST_REQUESTS}")
    print(f"Expected: {EXPECTED_LIMIT} OK, {TEST_REQUESTS - EXPECTED_LIMIT} blocked (429)")
    
    results: List[Dict[str, Any]] = []
    
    async with httpx.AsyncClient() as client:
        client.headers.update({"X-API-Key": API_KEY})
        
        start_time = time.time()
        
        ***REMOVED*** Send requests as fast as possible (within 1 minute window)
        tasks = []
        for i in range(TEST_REQUESTS):
            async def make_request(req_id: int):
                req_start = time.time()
                try:
                    response = await client.get(
                        f"{BASE_URL}/api/v1/b2b/demo/hotels",
                        params={"location": "Test"},
                        timeout=30.0
                    )
                    
                    latency_ms = (time.time() - req_start) * 1000
                    
                    result = {
                        "request_id": req_id,
                        "status_code": response.status_code,
                        "latency_ms": latency_ms,
                        "success": 200 <= response.status_code < 300,
                        "rate_limited": response.status_code == 429,
                        "x_rate_limit_limit": response.headers.get("X-RateLimit-Limit"),
                        "x_rate_limit_remaining": response.headers.get("X-RateLimit-Remaining"),
                        "x_rate_limit_reset": response.headers.get("X-RateLimit-Reset"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    return result
                    
                except Exception as e:
                    latency_ms = (time.time() - req_start) * 1000
                    return {
                        "request_id": req_id,
                        "status_code": 0,
                        "latency_ms": latency_ms,
                        "success": False,
                        "rate_limited": False,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            tasks.append(make_request(i))
            
            ***REMOVED*** Small delay to avoid overwhelming the system
            await asyncio.sleep(0.05)  ***REMOVED*** 20 requests per second
        
        ***REMOVED*** Wait for all requests to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        ***REMOVED*** Filter out exceptions
        results = [r for r in results if isinstance(r, dict)]
        
        elapsed_time = time.time() - start_time
    
    ***REMOVED*** Analyze results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r.get("status_code") == 200)
    rate_limited_count = sum(1 for r in results if r.get("rate_limited"))
    error_count = sum(1 for r in results if not r.get("success") and not r.get("rate_limited"))
    
    print(f"\n📊 Summary:")
    print(f"  Total requests: {len(results)}")
    print(f"  200 OK: {success_count}")
    print(f"  429 Rate Limited: {rate_limited_count}")
    print(f"  Other errors: {error_count}")
    print(f"  Time elapsed: {elapsed_time:.2f}s")
    
    ***REMOVED*** Validation
    print("\n✅ Validation:")
    if success_count == EXPECTED_LIMIT:
        print(f"  ✅ Correct: {success_count} requests allowed (expected {EXPECTED_LIMIT})")
    else:
        print(f"  ❌ Incorrect: {success_count} requests allowed (expected {EXPECTED_LIMIT})")
    
    if rate_limited_count == TEST_REQUESTS - EXPECTED_LIMIT:
        print(f"  ✅ Correct: {rate_limited_count} requests blocked (expected {TEST_REQUESTS - EXPECTED_LIMIT})")
    else:
        print(f"  ⚠️  Warning: {rate_limited_count} requests blocked (expected {TEST_REQUESTS - EXPECTED_LIMIT})")
    
    ***REMOVED*** Sample rate limit headers
    rate_limited_results = [r for r in results if r.get("rate_limited")]
    if rate_limited_results:
        sample = rate_limited_results[0]
        print(f"\n📋 Sample Rate Limit Headers (429 response):")
        print(f"  X-RateLimit-Limit: {sample.get('x_rate_limit_limit')}")
        print(f"  X-RateLimit-Remaining: {sample.get('x_rate_limit_remaining')}")
        print(f"  X-RateLimit-Reset: {sample.get('x_rate_limit_reset')}")
    
    ***REMOVED*** Save results
    report = {
        "test_config": {
            "base_url": BASE_URL,
            "expected_limit": EXPECTED_LIMIT,
            "test_requests": TEST_REQUESTS,
            "test_time": datetime.utcnow().isoformat()
        },
        "results": {
            "total_requests": len(results),
            "success_count": success_count,
            "rate_limited_count": rate_limited_count,
            "error_count": error_count,
            "elapsed_time_seconds": elapsed_time,
            "validation": {
                "expected_success": EXPECTED_LIMIT,
                "actual_success": success_count,
                "passed": success_count == EXPECTED_LIMIT,
                "expected_blocked": TEST_REQUESTS - EXPECTED_LIMIT,
                "actual_blocked": rate_limited_count
            },
            "all_results": results
        }
    }
    
    with open("backend/tests/rate_limit_test_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Rate limit test completed!")
    print(f"📄 Results saved to: backend/tests/rate_limit_test_results.json")
    
    return report


if __name__ == "__main__":
    asyncio.run(test_rate_limit())
