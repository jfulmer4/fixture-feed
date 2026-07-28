"""Tier assignment — rules evaluated in order, first match wins (spec §1).

1. UCL fixture                -> priority
2. Any primary team playing   -> priority
3. Any secondary team playing -> secondary
4. Everything else fetched    -> footnote
"""
import config


def assign_tier(match):
    """Return 'priority' | 'secondary' | 'footnote' for a football-data.org match dict."""
    if match["competition"]["code"] == config.UCL_CODE:
        return "priority"
    team_ids = {match["homeTeam"].get("id"), match["awayTeam"].get("id")}
    if team_ids & set(config.PRIMARY_TEAM_IDS):
        return "priority"
    if team_ids & set(config.SECONDARY_TEAM_IDS):
        return "secondary"
    return "footnote"


def bucket_matches(matches):
    """Split a match list into {tier: [matches]} with every tier key present."""
    buckets = {tier: [] for tier in config.TIER_FILES}
    for match in matches:
        buckets[assign_tier(match)].append(match)
    return buckets
