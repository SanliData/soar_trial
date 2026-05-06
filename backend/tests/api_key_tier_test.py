"""
API KEY TIER TEST: api_key_tier_test
PURPOSE: Test API key tier-based quotas (free/pro/enterprise)
ENCODING: UTF-8 WITHOUT BOM
"""

import asyncio
import os
import time
import json
from datetime import datetime
from typing import Dict, Any, List

import httpx

***REMOVED*** Test configuration (never hardcode production credentials)
BASE_URL = os.getenv("SOARB2B_BASE_URL", "http://127.0.0.1:8000")

***REMOVED*** Tier quotas (requests per minute)
TIER_QUOTAS = {
    "free": 50,
    "standard": 100,  ***REMOVED*** Current default
    "premium": 500,
    "enterprise": 10000  ***REMOVED*** Effectively unlimited
}

***REMOVED*** Test API keys (these should be created in database first)
***REMOVED*** For testing, we'll use the existing key and simulate different tiers
TEST_API_KEYS = {
    "free": os.getenv("SOARB2B_API_KEY_FREE", ""),
    "standard": os.getenv("SOARB2B_API_KEY_STANDARD", ""),
    "premium": os.getenv("SOARB2B_API_KEY_PREMIUM", ""),
    "enterprise": os.getenv("SOARB2B_API_KEY_ENTERPRISE", ""),
}


async def test_tier_quota(tier: str, api_key: str, expected_quota: int):
    """Test quota enforcement for a specific tier"""
    if not api_key:
        raise RuntimeError(f"Missing API key for tier={tier}. Set SOARB2B_API_KEY_{tier.upper()} env var.")
    print(f"\n{'=' * 70}")
    print(f"Testing Tier: {tier.upper()}")
    print(f"{'=' * 70}")
    print(f"Expected quota: {expected_quota} req/min")
    print(f"Test requests: {expected_quota + 20} (should allow {expected_quota}, block 20)")
    
    results: List[Dict[str, Any]] = []
    
    async with httpx.AsyncClient() as client:
        client.headers.update({"X-API-Key": api_key})
        
        start_time = time.time()
        test_requests = expected_quota + 20
        
        ***REMOVED*** Send requests
        tasks = []
        for i in range(test_requests):
            async def make_request(req_id: int):
                req_start = time.time()
                try:
                    response = await client.get(
                        f"{BASE_URL}/api/v1/b2b/demo/hotels",
                        params={"location": f"Test-{tier}"},
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
            await asyncio.sleep(0.1)  ***REMOVED*** Small delay
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        results = [r for r in results if isinstance(r, dict)]
        
        elapsed_time = time.time() - start_time
    
    ***REMOVED*** Analyze results
    success_count = sum(1 for r in results if r.get("status_code") == 200)
    rate_limited_count = sum(1 for r in results if r.get("rate_limited"))
    
    print(f"\n📊 Results for {tier}:")
    print(f"  Total requests: {len(results)}")
    print(f"  200 OK: {success_count}")
    print(f"  429 Rate Limited: {rate_limited_count}")
    print(f"  Expected quota: {expected_quota}")
    print(f"  Elapsed time: {elapsed_time:.2f}s")
    
    ***REMOVED*** Validation
    if success_count <= expected_quota:
        print(f"  ✅ PASS: Quota enforced correctly ({success_count} <= {expected_quota})")
        passed = True
    else:
        print(f"  ❌ FAIL: Quota not enforced ({success_count} > {expected_quota})")
        passed = False
    
    return {
        "tier": tier,
        "expected_quota": expected_quota,
        "total_requests": len(results),
        "success_count": success_count,
        "rate_limited_count": rate_limited_count,
        "elapsed_time_seconds": elapsed_time,
        "passed": passed,
        "results": results
    }


async def main():
    """Run all tier quota tests"""
    print("=" * 70)
    print("API KEY TIER QUOTA TEST")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Test started: {datetime.utcnow().isoformat()}")
    
    tier_results = []
    
    ***REMOVED*** Test each tier
    for tier, quota in TIER_QUOTAS.items():
        api_key = TEST_API_KEYS.get(tier)
        if not api_key:
            print(f"\n⚠️  Skipping {tier}: No API key configured")
            continue
        
        result = await test_tier_quota(tier, api_key, quota)
        tier_results.append(result)
        
        ***REMOVED*** Wait between tier tests
        await asyncio.sleep(5)
    
    ***REMOVED*** Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for result in tier_results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} {result['tier'].upper()}: {result['success_count']}/{result['expected_quota']} quota")
    
    ***REMOVED*** Save results
    report = {
        "test_config": {
            "base_url": BASE_URL,
            "tier_quotas": TIER_QUOTAS,
            "test_time": datetime.utcnow().isoformat()
        },
        "results": tier_results
    }
    
    with open("backend/tests/api_key_tier_test_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Tier quota test completed!")
    print(f"📄 Results saved to: backend/tests/api_key_tier_test_results.json")
    
    return report


if __name__ == "__main__":
    asyncio.run(main())
