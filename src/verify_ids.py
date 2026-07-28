"""One-time helper: confirm the hardcoded team IDs against the live API.

Usage: FOOTBALL_DATA_TOKEN=... python src/verify_ids.py
"""
import os
import sys

import requests

import config


def main():
    token = os.environ.get("FOOTBALL_DATA_TOKEN")
    if not token:
        print("FOOTBALL_DATA_TOKEN is not set", file=sys.stderr)
        return 1

    expected = {**config.PRIMARY_TEAM_IDS, **config.SECONDARY_TEAM_IDS}
    failures = 0
    for team_id, expected_name in expected.items():
        resp = requests.get(
            f"{config.API_BASE}/teams/{team_id}",
            headers={"X-Auth-Token": token},
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"✗ id {team_id}: HTTP {resp.status_code}")
            failures += 1
            continue
        actual_name = resp.json().get("name", "")
        mark = "✓" if actual_name == expected_name else "✗"
        if mark == "✗":
            failures += 1
        print(f"{mark} id {team_id}: expected {expected_name!r}, API says {actual_name!r}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
