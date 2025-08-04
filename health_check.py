#!/usr/bin/env python3
"""
Simple health check script for testing the Whisper Transcribe API
"""
import requests
import sys
import time

def check_health(base_url="http://localhost:8000"):
    """Check the health of the application"""
    endpoints = [
        "/",
        "/health", 
        "/api/health"
    ]
    
    print(f"=== Health Check for {base_url} ===")
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\nChecking {url}...")
            
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    # Allow custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    if check_health(base_url):
        print("\n✅ All health checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Health checks failed!")
        sys.exit(1) 