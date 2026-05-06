"""
LOAD TEST: load_test
PURPOSE: Enterprise load and stress testing for SOAR B2B
ENCODING: UTF-8 WITHOUT BOM
"""

import asyncio
import time
import statistics
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict

import httpx

***REMOVED*** Test configuration
BASE_URL = "https://soarb2b.com"  ***REMOVED*** Production URL
***REMOVED*** BASE_URL = "http://localhost:8000"  ***REMOVED*** Local testing
API_KEY = "<REDACTED_SOARB2B_API_KEY>"

***REMOVED*** Test scenarios
TEST_SCENARIOS = {
    "concurrent_users": {
        "users": 1000,
        "requests_per_user": 5,
        "ramp_up_seconds": 30
    },
    "burst_rps": {
        "rps": 5000,
        "duration_seconds": 10
    }
}

***REMOVED*** Results storage
results = {
    "hotels": {
        "requests": [],
        "errors": [],
        "cache_hits": 0,
        "cache_misses": 0
    },
    "onboarding": {
        "requests": [],
        "errors": []
    }
}


async def test_hotels_endpoint(client: httpx.AsyncClient, location: str = "Istanbul") -> Dict[str, Any]:
    """Test hotels endpoint"""
    start_time = time.time()
    
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/b2b/demo/hotels",
            params={"location": location},
            timeout=30.0
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        result = {
            "endpoint": "/api/v1/b2b/demo/hotels",
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "success": 200 <= response.status_code < 300,
            "cache_header": response.headers.get("X-Cache", "MISS"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        ***REMOVED*** Check cache status
        cache_status = response.headers.get("X-Cache", "MISS")
        if cache_status == "HIT":
            results["hotels"]["cache_hits"] += 1
        else:
            results["hotels"]["cache_misses"] += 1
        
        return result
        
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "endpoint": "/api/v1/b2b/demo/hotels",
            "status_code": 0,
            "latency_ms": latency_ms,
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def test_onboarding_endpoint(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Test onboarding create-plan endpoint"""
    start_time = time.time()
    
    payload = {
        "company_name": "Test Company",
        "email": f"test_{int(time.time())}@test.com",
        "target_type": "B2B",
        "geography": "USA",
        "decision_roles": "CEO, CTO",
        "product_service": "Load test service",
        "meeting_goal": "Load testing"
    }
    
    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/b2b/onboarding/create-plan",
            json=payload,
            timeout=30.0
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "endpoint": "/api/v1/b2b/onboarding/create-plan",
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "success": 200 <= response.status_code < 300,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "endpoint": "/api/v1/b2b/onboarding/create-plan",
            "status_code": 0,
            "latency_ms": latency_ms,
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def simulate_concurrent_users(num_users: int, requests_per_user: int, ramp_up_seconds: int = 30):
    """Simulate concurrent users with ramp-up"""
    print(f"\n🚀 Starting concurrent users test: {num_users} users, {requests_per_user} req/user")
    
    async with httpx.AsyncClient() as client:
        client.headers.update({"X-API-Key": API_KEY})
        
        tasks = []
        
        ***REMOVED*** Ramp-up: gradually add users
        users_per_batch = max(1, num_users // (ramp_up_seconds // 2))
        
        for batch_idx in range(0, num_users, users_per_batch):
            batch_users = min(users_per_batch, num_users - batch_idx)
            
            for user_idx in range(batch_users):
                async def user_task(user_id: int):
                    user_results = []
                    for req_idx in range(requests_per_user):
                        ***REMOVED*** Alternate between hotels and onboarding
                        if req_idx % 2 == 0:
                            result = await test_hotels_endpoint(client, location=f"Location-{user_id}")
                            results["hotels"]["requests"].append(result)
                        else:
                            result = await test_onboarding_endpoint(client)
                            results["onboarding"]["requests"].append(result)
                        
                        user_results.append(result)
                        
                        ***REMOVED*** Small delay between requests
                        await asyncio.sleep(0.1)
                    
                    return user_results
                
                tasks.append(user_task(batch_idx + user_idx))
            
            ***REMOVED*** Wait before next batch (ramp-up)
            if batch_idx + users_per_batch < num_users:
                await asyncio.sleep(2)
        
        ***REMOVED*** Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"✅ Concurrent users test completed")


async def simulate_burst_rps(target_rps: int, duration_seconds: int):
    """Simulate burst RPS"""
    print(f"\n🚀 Starting burst RPS test: {target_rps} RPS for {duration_seconds}s")
    
    async with httpx.AsyncClient() as client:
        client.headers.update({"X-API-Key": API_KEY})
        
        start_time = time.time()
        request_count = 0
        tasks = []
        
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            ***REMOVED*** Create batch of requests to achieve target RPS
            for _ in range(target_rps // 10):  ***REMOVED*** Smaller batches for better control
                if time.time() - start_time >= duration_seconds:
                    break
                
                ***REMOVED*** Alternate endpoints
                if request_count % 2 == 0:
                    tasks.append(test_hotels_endpoint(client))
                    request_count += 1
                else:
                    tasks.append(test_onboarding_endpoint(client))
                    request_count += 1
            
            ***REMOVED*** Wait to maintain RPS
            elapsed = time.time() - batch_start
            sleep_time = max(0, 0.1 - elapsed)  ***REMOVED*** 100ms batch interval
            await asyncio.sleep(sleep_time)
        
        ***REMOVED*** Wait for remaining tasks
        if tasks:
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results_list:
                if isinstance(result, dict):
                    if result.get("endpoint") == "/api/v1/b2b/demo/hotels":
                        results["hotels"]["requests"].append(result)
                    else:
                        results["onboarding"]["requests"].append(result)
                elif isinstance(result, Exception):
                    print(f"⚠️ Task error: {result}")
    
    print(f"✅ Burst RPS test completed")


def calculate_metrics(endpoint_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate performance metrics"""
    if not endpoint_results:
        return {
            "total_requests": 0,
            "success_requests": 0,
            "error_requests": 0,
            "error_rate": 0.0,
            "avg_latency_ms": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "p99_latency_ms": 0.0,
            "min_latency_ms": 0.0,
            "max_latency_ms": 0.0
        }
    
    latencies = [r["latency_ms"] for r in endpoint_results if r.get("success")]
    successes = sum(1 for r in endpoint_results if r.get("success"))
    errors = len(endpoint_results) - successes
    
    if not latencies:
        return {
            "total_requests": len(endpoint_results),
            "success_requests": 0,
            "error_requests": errors,
            "error_rate": 1.0,
            "avg_latency_ms": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "p99_latency_ms": 0.0,
            "min_latency_ms": 0.0,
            "max_latency_ms": 0.0
        }
    
    sorted_latencies = sorted(latencies)
    
    return {
        "total_requests": len(endpoint_results),
        "success_requests": successes,
        "error_requests": errors,
        "error_rate": errors / len(endpoint_results) if endpoint_results else 0.0,
        "avg_latency_ms": statistics.mean(latencies),
        "p50_latency_ms": statistics.median(latencies),
        "p95_latency_ms": sorted_latencies[int(len(sorted_latencies) * 0.95)] if sorted_latencies else 0.0,
        "p99_latency_ms": sorted_latencies[int(len(sorted_latencies) * 0.99)] if sorted_latencies else 0.0,
        "min_latency_ms": min(latencies),
        "max_latency_ms": max(latencies)
    }


async def main():
    """Run all load tests"""
    print("=" * 70)
    print("ENTERPRISE LOAD TEST - SOAR B2B")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Test started: {datetime.utcnow().isoformat()}")
    
    ***REMOVED*** Test 1: Concurrent Users
    print("\n" + "=" * 70)
    print("TEST 1: Concurrent Users (1,000 users × 5 requests)")
    print("=" * 70)
    await simulate_concurrent_users(
        num_users=1000,
        requests_per_user=5,
        ramp_up_seconds=30
    )
    
    ***REMOVED*** Wait between tests
    await asyncio.sleep(10)
    
    ***REMOVED*** Test 2: Burst RPS
    print("\n" + "=" * 70)
    print("TEST 2: Burst RPS (5,000 RPS for 10 seconds)")
    print("=" * 70)
    await simulate_burst_rps(target_rps=5000, duration_seconds=10)
    
    ***REMOVED*** Calculate metrics
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    hotels_metrics = calculate_metrics(results["hotels"]["requests"])
    onboarding_metrics = calculate_metrics(results["onboarding"]["requests"])
    
    ***REMOVED*** Calculate cache hit ratio
    total_hotel_requests = results["hotels"]["cache_hits"] + results["hotels"]["cache_misses"]
    cache_hit_ratio = (results["hotels"]["cache_hits"] / total_hotel_requests * 100) if total_hotel_requests > 0 else 0.0
    
    print("\n📊 Hotels Endpoint Metrics:")
    print(json.dumps(hotels_metrics, indent=2))
    print(f"Cache Hits: {results['hotels']['cache_hits']}")
    print(f"Cache Misses: {results['hotels']['cache_misses']}")
    print(f"Cache Hit Ratio: {cache_hit_ratio:.2f}%")
    
    print("\n📊 Onboarding Endpoint Metrics:")
    print(json.dumps(onboarding_metrics, indent=2))
    
    ***REMOVED*** Save detailed results
    report = {
        "test_config": {
            "base_url": BASE_URL,
            "test_time": datetime.utcnow().isoformat(),
            "scenarios": TEST_SCENARIOS
        },
        "results": {
            "hotels": {
                "metrics": hotels_metrics,
                "cache_stats": {
                    "hits": results["hotels"]["cache_hits"],
                    "misses": results["hotels"]["cache_misses"],
                    "hit_ratio": cache_hit_ratio
                },
                "sample_requests": results["hotels"]["requests"][:10]  ***REMOVED*** First 10 for reference
            },
            "onboarding": {
                "metrics": onboarding_metrics,
                "sample_requests": results["onboarding"]["requests"][:10]
            }
        }
    }
    
    ***REMOVED*** Save to file
    with open("backend/tests/load_test_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Load test completed!")
    print("📄 Detailed results saved to: backend/tests/load_test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
