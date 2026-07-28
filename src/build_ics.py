"""ICS generation. Output must be byte-stable for unchanged input — the workflow
only commits when files diff, so nothing here may depend on the current time."""
from datetime import datetime, timezone

from icalendar import Alarm, Calendar, Event

import config


def _parse_utc(stamp):
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(timezone.utc)


def _tla(team):
    tla = team.get("tla")
    if tla:
        return tla
    name = team.get("shortName") or team.get("name") or "TBD"
    return name[:3].upper()


def build_event(match, tier):
    postponed = match["status"] == "POSTPONED"
    comp = match["competition"]
    comp_label = config.COMPETITIONS.get(comp["code"], comp["code"])
    home, away = match["homeTeam"], match["awayTeam"]

    title = f"{config.TIER_EMOJI[tier]} {_tla(home)} v {_tla(away)} · {comp_label}"
    if postponed:
        title = f"⏸ {title}"

    start = _parse_utc(match["utcDate"])
    # lastUpdated drives DTSTAMP and SEQUENCE: both only move when the API
    # actually changes the match, so a reschedule bumps SEQUENCE (Apple re-reads
    # the event) while an unchanged fixture emits identical bytes run over run.
    updated = _parse_utc(match["lastUpdated"]) if match.get("lastUpdated") else start

    event = Event()
    event.add("uid", f"fd-{match['id']}@{config.UID_DOMAIN}")
    event.add("summary", title)
    event.add("dtstart", start)
    event.add("dtend", start + config.MATCH_DURATION)
    event.add("dtstamp", updated)
    event.add("sequence", int(updated.timestamp()))

    description = f"{home.get('name', 'TBD')} vs {away.get('name', 'TBD')} — {comp['name']}"
    if match.get("matchday"):
        description += f", Matchday {match['matchday']}"
    event.add("description", description)

    if match.get("venue"):
        event.add("location", match["venue"])
    if postponed:
        event.add("status", "CANCELLED")

    for trigger in config.TIER_ALARMS[tier]:
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", title)
        alarm.add("trigger", trigger)
        event.add_component(alarm)

    return event


def build_calendar(matches, tier):
    """Return the serialized ICS bytes for one tier's matches."""
    cal = Calendar()
    cal.add("prodid", "-//fixture-feed//football-calendars//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", config.CALENDAR_NAMES[tier])
    cal.add("x-published-ttl", "PT12H")
    for match in sorted(matches, key=lambda m: (m["utcDate"], m["id"])):
        cal.add_component(build_event(match, tier))
    return cal.to_ical()
