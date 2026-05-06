"""
Demo Data Seeder for SOAR B2B
Creates sample data for testing and development
"""

import requests
import json

BASE = "http://127.0.0.1:8000"

def post(url, data):
    """POST request to endpoint"""
    try:
        r = requests.post(BASE + url, json=data)
        print(f"✓ POST {url} - Status: {r.status_code}")
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"✗ POST {url} - Error: {str(e)}")
        return None

def get(url):
    """GET request to endpoint"""
    try:
        r = requests.get(BASE + url)
        print(f"✓ GET {url} - Status: {r.status_code}")
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"✗ GET {url} - Error: {str(e)}")
        return None

print("=" * 50)
print("SOAR B2B - Demo Data Seeder")
print("=" * 50)
print("")

***REMOVED*** Products
print("--- Creating Products ---")
post("/v1/v1/products/create", {
    "name": "Hotel Blanket",
    "category": "textile",
    "identification_type": "barcode"
})

post("/v1/v1/products/create", {
    "name": "Bath Towel Set",
    "category": "textile",
    "identification_type": "barcode"
})

***REMOVED*** Campaign
print("")
print("--- Creating Campaigns ---")
post("/v1/v1/campaigns/create", {
    "name": "NY Hotels Campaign",
    "ad_content_type": "text",
    "ad_content": "Premium hotel supplies",
    "ad_type": "search",
    "target": {
        "company_ids": [],
        "personnel_ids": []
    }
})

***REMOVED*** Analytics Events
print("")
print("--- Creating Analytics Events ---")
post("/v1/analytics/events", {
    "event": "demo_seed",
    "properties": {
        "source": "seed_script"
    }
})

***REMOVED*** Research
print("")
print("--- Running Company Research ---")
post("/v1/v1/research/batch-research", {
    "company_names": ["Hilton", "Marriott"]
})

print("")
print("=" * 50)
print("Seed completed!")
print("=" * 50)
