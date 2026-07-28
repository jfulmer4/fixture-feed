import tier


def make_match(comp_code="PL", home_id=999, away_id=998, **overrides):
    match = {
        "id": 12345,
        "competition": {"code": comp_code, "name": "Premier League"},
        "homeTeam": {"id": home_id, "name": "Home FC", "tla": "HOM"},
        "awayTeam": {"id": away_id, "name": "Away FC", "tla": "AWY"},
        "status": "TIMED",
        "utcDate": "2026-09-19T14:00:00Z",
        "lastUpdated": "2026-07-01T00:00:00Z",
        "matchday": 5,
    }
    match.update(overrides)
    return match


MCI, ATM = 65, 78
MUN, BAR, RMA = 66, 81, 86


def test_any_ucl_match_is_priority():
    # Rule 1 fires regardless of who is playing
    assert tier.assign_tier(make_match(comp_code="CL")) == "priority"


def test_city_ucl_match_is_priority_not_secondary():
    assert tier.assign_tier(make_match(comp_code="CL", home_id=MCI)) == "priority"


def test_primary_team_epl_match_is_priority():
    assert tier.assign_tier(make_match(home_id=MUN)) == "priority"


def test_primary_team_away_is_priority():
    assert tier.assign_tier(make_match(comp_code="PD", away_id=RMA)) == "priority"


def test_city_epl_match_is_secondary():
    assert tier.assign_tier(make_match(home_id=MCI)) == "secondary"


def test_atletico_laliga_match_is_secondary():
    assert tier.assign_tier(make_match(comp_code="PD", away_id=ATM)) == "secondary"


def test_primary_beats_secondary_when_both_play():
    # e.g. Man United v Man City: rule 2 fires before rule 3
    assert tier.assign_tier(make_match(home_id=MUN, away_id=MCI)) == "priority"


def test_neutral_epl_match_is_footnote():
    assert tier.assign_tier(make_match()) == "footnote"


def test_barcelona_laliga_is_priority():
    assert tier.assign_tier(make_match(comp_code="PD", home_id=BAR)) == "priority"


def test_bucket_matches_partitions_without_duplicates():
    matches = [
        make_match(comp_code="CL", home_id=MCI),  # priority via rule 1
        make_match(home_id=MUN),                  # priority via rule 2
        make_match(home_id=MCI),                  # secondary
        make_match(),                             # footnote
    ]
    buckets = tier.bucket_matches(matches)
    assert len(buckets["priority"]) == 2
    assert len(buckets["secondary"]) == 1
    assert len(buckets["footnote"]) == 1
    assert sum(len(v) for v in buckets.values()) == len(matches)
