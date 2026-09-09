"""
Standalone Remotive API diagnostic.

Run directly (no project imports needed):

    python src/check_remotive.py

This bypasses job_discovery.py entirely so we can see exactly what
Remotive's API returns for different requests, independent of
anything in our own pipeline.
"""

import requests

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "JobApplicationAutomation/1.0"})

urls = [
    "https://remotive.com/api/remote-jobs",
    "https://remotive.com/api/remote-jobs?limit=5",
    "https://remotive.com/api/remote-jobs?limit=1000",
]

for url in urls:
    print(f"\nGET {url}")
    try:
        r = SESSION.get(url, timeout=30)
        print(f"  status: {r.status_code}")
        print(f"  headers of interest: "
              f"content-length={r.headers.get('content-length')}, "
              f"x-ratelimit-remaining={r.headers.get('x-ratelimit-remaining')}")
        data = r.json()
        jobs = data.get("jobs", [])
        print(f"  top-level keys: {list(data.keys())}")
        print(f"  job-count field (if present): {data.get('job-count')}")
        print(f"  len(jobs): {len(jobs)}")
    except Exception as e:
        print(f"  ERROR: {e}")

# Also try without any custom User-Agent, in case Remotive is
# rate-limiting based on that header specifically.
print("\nGET https://remotive.com/api/remote-jobs?limit=1000 (default requests User-Agent)")
try:
    r = requests.get("https://remotive.com/api/remote-jobs?limit=1000", timeout=30)
    data = r.json()
    print(f"  status: {r.status_code}")
    print(f"  len(jobs): {len(data.get('jobs', []))}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n--- Full metadata fields from the plain request ---")
try:
    r = requests.get("https://remotive.com/api/remote-jobs", timeout=30)
    data = r.json()
    print(f"  00-warning       : {data.get('00-warning')}")
    print(f"  0-legal-notice   : {data.get('0-legal-notice')}")
    print(f"  job-count        : {data.get('job-count')}")
    print(f"  total-job-count  : {data.get('total-job-count')}")
except Exception as e:
    print(f"  ERROR: {e}")