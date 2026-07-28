# fixture-feed

Self-updating football fixture calendars for Apple Calendar, tiered by priority.
GitHub Actions cron → Python → 3 ICS feeds → GitHub Pages → webcal subscriptions.
Subscribe once, done forever.

## Tiers

| Tier | Feed | Contents | Alerts |
|---|---|---|---|
| 🔴 Priority | `priority.ics` | All UCL fixtures + Man United, Barcelona, Real Madrid (all comps) | 1 day + 30 min before |
| 🔵 Secondary | `secondary.ics` | Man City, Atlético Madrid (EPL / La Liga only) | 30 min before |
| ⚪ Footnote | `footnote.ics` | Every other EPL + La Liga fixture | None |

Each fixture lands in exactly one feed. Rules evaluated in order: UCL → priority;
primary team playing → priority; secondary team playing → secondary; else footnote.

## How it self-heals

- Runs daily at 06:00 UTC (plus manual `workflow_dispatch`).
- Event `UID` derives from the API's stable match ID, so a rescheduled kickoff
  **updates** the existing calendar event instead of duplicating it.
- `SEQUENCE`/`DTSTAMP` derive from the API's `lastUpdated`, so unchanged fixtures
  produce byte-identical output — the workflow only commits when something
  actually changed.
- Postponed matches show as ⏸-prefixed, grayed-out (`STATUS:CANCELLED`) events
  until re-timed.
- On API failure the run exits nonzero without touching `docs/` — yesterday's
  feeds stay live. An empty feed never overwrites a good one.

## Setup (one-time)

1. **Token** — free account at [football-data.org](https://www.football-data.org/client/register),
   then add the token as an Actions secret: repo → Settings → Secrets and
   variables → Actions → New repository secret → name `FOOTBALL_DATA_TOKEN`.
2. **Pages** — repo → Settings → Pages → Deploy from a branch → `main` / `/docs`.
3. **Verify team IDs** (once): `FOOTBALL_DATA_TOKEN=... python src/verify_ids.py`
4. **First build** — Actions tab → *build feeds* → Run workflow. Confirm the
   three `.ics` files appear in `docs/`.
5. **Subscribe** — iPhone → Settings → Calendar → Accounts → Add Subscribed
   Calendar → paste each webcal URL from the
   [landing page](https://jfulmer4.github.io/fixture-feed/):
   - `webcal://jfulmer4.github.io/fixture-feed/priority.ics` (suggest red)
   - `webcal://jfulmer4.github.io/fixture-feed/secondary.ics` (suggest blue)
   - `webcal://jfulmer4.github.io/fixture-feed/footnote.ics` (suggest gray)

   **Leave "Remove Alerts" unchecked** or the baked-in reminders get stripped.
   Footnote calendar: toggle visibility off by default; flip on for big matchdays.

## Local development

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt pytest
.venv/bin/pytest -q                                  # tier rules + ICS format
FOOTBALL_DATA_TOKEN=... .venv/bin/python src/main.py # real build into docs/
```

## Notes

- Free tier exposes the current season only; season rollover repopulates the
  feeds automatically on the next run.
- Early-season TBD kickoff times are trusted as-is — the daily refresh corrects
  them as they firm up (stale times are a ≤24h problem).
- Cup competitions (FA Cup, Copa del Rey, Europa) are out of scope for v1;
  adding a comp code in `src/config.py` is a one-line change.
- Apple re-polls subscribed calendars on its own cadence (roughly daily) —
  building more often than daily wouldn't reach your phone any faster.
