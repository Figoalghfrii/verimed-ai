"""Utility script to verify VeriMed API health endpoint from the command line."""

import json
import sys
import urllib.error
import urllib.request


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
            print(json.dumps(body, indent=2))
            if (
                body.get("success") is True
                and body.get("data", {}).get("status") == "healthy"
            ):
                return 0
            return 1
    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        print(f"Health check failed for {url}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
