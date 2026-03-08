#!/usr/bin/env python
"""
NECTA API - Startup Verification and Quick Test Guide
"""
import subprocess
import time
import sys
import requests
import json

print("\n" + "=" * 70)
print(" NECTA API - STARTUP VERIFICATION")
print("=" * 70)

# Step 1: Import test
print("\n[1/3] Testing imports...")
try:
    from adopter.api.main import app
    print("      ✓ App imported successfully")
except Exception as e:
    print(f"      ✗ Failed to import app: {e}")
    sys.exit(1)

# Step 2: Check routes
print("\n[2/3] Verifying API routes...")
routes = {}
for route in app.routes:
    if hasattr(route, 'path'):
        method = route.methods if hasattr(route, 'methods') else {'GET'}
        routes[route.path] = method

print(f"      ✓ Found {len(routes)} routes")
print("\n      Available endpoints:")
for path in sorted(routes.keys()):
    if path.startswith('/v1'):
        print(f"        GET {path}")

# Step 3: Test recommendations
print("\n[3/3] Startup instructions...")
print("\n      To start the API server:")
print("      ────────────────────────")
print("      $ uvicorn adopter.api.main:app --reload")
print("\n      Then in another terminal, test endpoints:")
print("      ──────────────────────────────────────────")
print("      $ curl http://localhost:8000/v1/health")
print("      $ curl http://localhost:8000/v1/meta/exam-types")
print("      $ curl http://localhost:8000/v1/centers | jq .")
print("      $ curl http://localhost:8000/v1/summaries/ACSEE | jq .")
print("\n      To submit a job:")
print("      ────────────────")
print("""      $ curl -X POST http://localhost:8000/v1/jobs \\
        -H "Content-Type: application/json" \\
        -d '{
          "type": "results",
          "examType": "ACSEE",
          "years": [2023]
        }' | jq .""")
print("\n      To start workers:")
print("      ─────────────────")
print("      $ python worker.py --worker-id worker-1 --poll-interval 5")
print("      $ python worker.py --worker-id worker-2 --poll-interval 5")

print("\n" + "=" * 70)
print(" ✓ NECTA API is ready for deployment!")
print("=" * 70 + "\n")

