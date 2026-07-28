"""Static configuration: teams, competitions, tiers, alert rules."""
from datetime import timedelta

API_BASE = "https://api.football-data.org/v4"

# football-data.org team IDs. IDs are stable, but run `python src/verify_ids.py`
# once with a live token to confirm before first deploy.
PRIMARY_TEAM_IDS = {
    66: "Manchester United FC",
    81: "FC Barcelona",
    86: "Real Madrid CF",
}

SECONDARY_TEAM_IDS = {
    65: "Manchester City FC",
    78: "Club Atlético de Madrid",
}

# competition code -> short label used in event titles
COMPETITIONS = {
    "PL": "EPL",
    "PD": "LAL",
    "CL": "UCL",
}

UCL_CODE = "CL"

# Match statuses worth keeping on a calendar. FINISHED is deliberately dropped.
INCLUDE_STATUSES = {"SCHEDULED", "TIMED", "POSTPONED", "IN_PLAY", "PAUSED"}

MATCH_DURATION = timedelta(hours=2)

UID_DOMAIN = "fixture-feed"

TIER_EMOJI = {
    "priority": "🔴",
    "secondary": "🔵",
    "footnote": "⚪",
}

# Negative timedeltas = alarm fires before kickoff.
TIER_ALARMS = {
    "priority": [timedelta(days=-1), timedelta(minutes=-30)],
    "secondary": [timedelta(minutes=-30)],
    "footnote": [],
}

TIER_FILES = {
    "priority": "priority.ics",
    "secondary": "secondary.ics",
    "footnote": "footnote.ics",
}

CALENDAR_NAMES = {
    "priority": "Football · Priority",
    "secondary": "Football · Secondary",
    "footnote": "Football · Footnote",
}
