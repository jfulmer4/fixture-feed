"""Orchestrate: fetch -> tier -> emit ICS files into docs/.

Exits nonzero WITHOUT touching docs/ on any fetch failure, so a bad run can
never overwrite good feeds with empty ones.
"""
import os
import sys

import build_ics
import config
import fetch
import tier

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")


def main():
    token = os.environ.get("FOOTBALL_DATA_TOKEN")
    if not token:
        print("FOOTBALL_DATA_TOKEN is not set", file=sys.stderr)
        return 1

    try:
        matches = fetch.fetch_all(token)
    except fetch.FetchError as exc:
        print(f"Fetch failed, leaving existing feeds untouched: {exc}", file=sys.stderr)
        return 1

    buckets = tier.bucket_matches(matches)
    for tier_name, filename in config.TIER_FILES.items():
        path = os.path.join(DOCS_DIR, filename)
        with open(path, "wb") as f:
            f.write(build_ics.build_calendar(buckets[tier_name], tier_name))
        print(f"{filename}: {len(buckets[tier_name])} fixtures")

    return 0


if __name__ == "__main__":
    sys.exit(main())
