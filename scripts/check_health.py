"""Utility script to verify VeriMed API health endpoint from the command line."""

import sys
import urllib.request
import json


def main() -> int:
    url = "http://localhost:8000/api/v1/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
            print(json.dumps(body, indent=2))
            if body.get("success") is True and body.get("data", {}).get("status") == "healthy":
                return 0
            return 1
    except Exception as exc:
        print(f"Health check failed for {url}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
