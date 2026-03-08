#!/usr/bin/env python
import sys
import os

# Add project to path
sys.path.insert(0, '/Users/salinastic/PycharmProjects/necta')

print("=" * 60)
print("TESTING NECTA API STARTUP")
print("=" * 60)

try:
    print("\n1. Testing imports...")
    from adopter.api.main import app
    print("   ✓ App imported successfully")

    print("\n2. Checking app routes...")
    routes = [route.path for route in app.routes]
    print(f"   ✓ Found {len(routes)} routes")
    for route in routes[:5]:
        print(f"     - {route}")

    print("\n3. App is ready!")
    print("=" * 60)
    print("\nTo start the server, run:")
    print("  uvicorn adopter.api.main:app --reload")
    print("\nThen in another terminal:")
    print("  curl http://localhost:8000/v1/health")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

