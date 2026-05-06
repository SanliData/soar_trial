***REMOVED***!/usr/bin/env python3
"""
Generate secure production API keys for SOAR B2B
"""
import secrets

def generate_api_keys(count=3):
    """Generate secure API keys"""
    keys = [secrets.token_urlsafe(32) for _ in range(count)]
    return keys

if __name__ == "__main__":
    keys = generate_api_keys(3)
    
    print("")
    print("="*70)
    print("PRODUCTION API KEYS GENERATED")
    print("="*70)
    print("")
    print("SOARB2B_API_KEYS=" + ",".join(keys))
    print("")
    print("Individual Keys:")
    for i, key in enumerate(keys, 1):
        print(f"  Key {i}: {key}")
    print("")
    print("="*70)
    print("IMPORTANT: Save these keys securely!")
    print("Add to Google Cloud Run environment variables.")
    print("NEVER commit these keys to GitHub!")
    print("="*70)
    print("")
