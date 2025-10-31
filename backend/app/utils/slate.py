"""Utility functions for determining game slates

A slate is a time grouping for NFL games:
- THURSDAY: Thursday Night Football
- SATURDAY: Saturday games (late season/playoffs)
- SUNDAY_EARLY: Sunday 1PM ET games
- SUNDAY_LATE: Sunday 4PM ET games
- SUNDAY_NIGHT: Sunday Night Football (~8:20PM ET)
- MONDAY: Monday Night Football
"""
from datetime import datetime, time
from typing import Optional
import pytz


# ET timezone for all NFL game times
ET = pytz.timezone('America/New_York')


def determine_slate(game_time: datetime) -> Optional[str]:
    """
    Determine the slate for a game based on its start time.

    Args:
        game_time: Game start time (datetime)

    Returns:
        Slate name or None if game_time is None
    """
    if not game_time:
        return None

    # Convert to ET if timezone-aware
    if game_time.tzinfo is not None:
        game_time_et = game_time.astimezone(ET)
    else:
        # Assume UTC and convert to ET
        game_time_et = pytz.utc.localize(game_time).astimezone(ET)

    # Get day of week (0=Monday, 6=Sunday)
    weekday = game_time_et.weekday()
    game_hour = game_time_et.hour

    # Thursday games
    if weekday == 3:  # Thursday
        return "THURSDAY"

    # Saturday games (typically late season)
    elif weekday == 5:  # Saturday
        return "SATURDAY"

    # Sunday games
    elif weekday == 6:  # Sunday
        # Sunday Night Football typically starts around 8:20 PM ET
        if game_hour >= 20:  # 8 PM or later
            return "SUNDAY_NIGHT"
        # Late afternoon games typically 4:00-4:25 PM ET
        elif game_hour >= 16:  # 4 PM or later
            return "SUNDAY_LATE"
        # Early games typically 1:00 PM ET
        else:
            return "SUNDAY_EARLY"

    # Monday games
    elif weekday == 0:  # Monday
        return "MONDAY"

    # Other days (rare, handle as edge case)
    else:
        # Default to categorizing by hour
        if game_hour >= 20:
            return "PRIMETIME"
        elif game_hour >= 16:
            return "AFTERNOON"
        else:
            return "EARLY"


# Slate display names for UI
SLATE_DISPLAY_NAMES = {
    "THURSDAY": "Thursday Night",
    "SATURDAY": "Saturday",
    "SUNDAY_EARLY": "Sunday Early (1PM ET)",
    "SUNDAY_LATE": "Sunday Late (4PM ET)",
    "SUNDAY_NIGHT": "Sunday Night",
    "MONDAY": "Monday Night",
    "PRIMETIME": "Primetime",
    "AFTERNOON": "Afternoon",
    "EARLY": "Early"
}


# Slate order for sorting
SLATE_ORDER = [
    "THURSDAY",
    "SATURDAY",
    "SUNDAY_EARLY",
    "SUNDAY_LATE",
    "SUNDAY_NIGHT",
    "MONDAY"
]


def get_slate_display_name(slate: str) -> str:
    """Get user-friendly display name for a slate"""
    return SLATE_DISPLAY_NAMES.get(slate, slate)


def get_sorted_slates(slates: list[str]) -> list[str]:
    """Sort slates in chronological order"""
    return sorted(slates, key=lambda s: SLATE_ORDER.index(s) if s in SLATE_ORDER else 999)
