from datetime import datetime, timezone

from icalendar import Calendar

import build_ics
from test_tier import make_match


def parse(ics_bytes):
    return Calendar.from_ical(ics_bytes)


def events_of(cal):
    return [c for c in cal.subcomponents if c.name == "VEVENT"]


def alarms_of(event):
    return [c for c in event.subcomponents if c.name == "VALARM"]


def test_uid_derives_from_match_id():
    cal = parse(build_ics.build_calendar([make_match(id=777)], "footnote"))
    assert str(events_of(cal)[0]["uid"]) == "fd-777@fixture-feed"


def test_title_format_and_emoji():
    cal = parse(build_ics.build_calendar([make_match(home_id=66)], "priority"))
    assert str(events_of(cal)[0]["summary"]) == "🔴 HOM v AWY · EPL"


def test_priority_gets_two_alarms_secondary_one_footnote_none():
    match = [make_match()]
    assert len(alarms_of(events_of(parse(build_ics.build_calendar(match, "priority")))[0])) == 2
    assert len(alarms_of(events_of(parse(build_ics.build_calendar(match, "secondary")))[0])) == 1
    assert len(alarms_of(events_of(parse(build_ics.build_calendar(match, "footnote")))[0])) == 0


def test_event_duration_is_two_hours():
    cal = parse(build_ics.build_calendar([make_match()], "footnote"))
    event = events_of(cal)[0]
    assert event["dtstart"].dt == datetime(2026, 9, 19, 14, 0, tzinfo=timezone.utc)
    assert (event["dtend"].dt - event["dtstart"].dt).total_seconds() == 2 * 3600


def test_postponed_match_is_cancelled_with_prefix():
    cal = parse(build_ics.build_calendar([make_match(status="POSTPONED")], "priority"))
    event = events_of(cal)[0]
    assert str(event["status"]) == "CANCELLED"
    assert str(event["summary"]).startswith("⏸ ")


def test_output_is_deterministic():
    matches = [make_match(id=2, utcDate="2026-09-20T14:00:00Z"), make_match(id=1)]
    first = build_ics.build_calendar(matches, "priority")
    second = build_ics.build_calendar(list(reversed(matches)), "priority")
    assert first == second


def test_sequence_bumps_when_last_updated_changes():
    before = build_ics.build_calendar([make_match()], "priority")
    after = build_ics.build_calendar(
        [make_match(lastUpdated="2026-07-02T00:00:00Z")], "priority"
    )
    seq_before = int(events_of(parse(before))[0]["sequence"])
    seq_after = int(events_of(parse(after))[0]["sequence"])
    assert seq_after > seq_before


def test_venue_becomes_location_when_present():
    cal = parse(build_ics.build_calendar([make_match(venue="Old Trafford")], "priority"))
    assert str(events_of(cal)[0]["location"]) == "Old Trafford"
    cal_no_venue = parse(build_ics.build_calendar([make_match()], "priority"))
    assert "location" not in events_of(cal_no_venue)[0]
