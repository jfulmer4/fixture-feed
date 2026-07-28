"""football-data.org client: one call per competition, retry with backoff."""
import sys
import time

import requests

import config

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 10


class FetchError(Exception):
    """Raised when a competition fetch fails after all retries."""


def fetch_competition_matches(code, token, session=None):
    """Return the raw match list for one competition, retrying on failure."""
    http = session or requests
    url = f"{config.API_BASE}/competitions/{code}/matches"
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = http.get(url, headers={"X-Auth-Token": token}, timeout=30)
            if resp.status_code == 429:
                # Rate limited: honor Retry-After if given, else back off hard.
                wait = int(resp.headers.get("Retry-After", 60))
                print(f"{code}: rate limited, waiting {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()["matches"]
        except (requests.RequestException, KeyError, ValueError) as exc:
            last_error = exc
            if attempt < MAX_ATTEMPTS:
                wait = BACKOFF_SECONDS * attempt
                print(f"{code}: attempt {attempt} failed ({exc}), retrying in {wait}s", file=sys.stderr)
                time.sleep(wait)
    raise FetchError(f"{code}: all {MAX_ATTEMPTS} attempts failed: {last_error}")


def fetch_all(token, session=None):
    """Fetch every configured competition and keep only calendar-worthy matches."""
    matches = []
    for code in config.COMPETITIONS:
        matches.extend(fetch_competition_matches(code, token, session=session))
        time.sleep(1)  # 3 calls/run sits far under the 10 req/min cap; pause is just politeness
    return [m for m in matches if m["status"] in config.INCLUDE_STATUSES]
