"""
Backfill Player Stats from Sleeper API

This is the PRIMARY data source for current 2025 NFL season data.
Sleeper API provides up-to-date, free, real-time statistics.

CRITICAL: This ensures we always have the latest data.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.nfl import Player, PlayerGameStats, Game, Team
from app.services.sleeper_stats import get_sleeper_stats_service
import structlog

logger = structlog.get_logger()


async def validate_data_freshness(session: AsyncSession) -> None:
    """
    Validate that our data is current and fresh.

    CRITICAL: Alerts if data is more than 7 days old.
    """
    result = await session.execute(
        select(PlayerGameStats).order_by(PlayerGameStats.created_at.desc()).limit(1)
    )
    latest_stat = result.scalar_one_or_none()

    if not latest_stat:
        logger.warning("no_data_found", message="Database has no player stats! This is a CRITICAL issue.")
        print("\n" + "="*60)
        print("⚠️  WARNING: NO DATA IN DATABASE")
        print("="*60)
        return

    days_old = (datetime.utcnow() - latest_stat.created_at).days

    if days_old > 7:
        logger.error(
            "stale_data_detected",
            days_old=days_old,
            latest_data_from=latest_stat.created_at.isoformat(),
            message="DATA IS STALE! This is a CRITICAL issue."
        )
        print("\n" + "="*60)
        print(f"🚨 CRITICAL: DATA IS {days_old} DAYS OLD!")
        print(f"Latest data from: {latest_stat.created_at.date()}")
        print("Your predictions will be based on outdated information.")
        print("="*60 + "\n")
    else:
        logger.info("data_freshness_ok", days_old=days_old)
        print(f"✓ Data freshness OK ({days_old} days old)")


async def backfill_from_sleeper(
    season: str,
    weeks: list = None,
    season_type: str = "regular"
):
    """
    Backfill player stats from Sleeper API.

    Args:
        season: Season year (e.g., "2025")
        weeks: List of weeks to backfill, or None for all
        season_type: "regular", "pre", or "post"
    """
    print("NFL Player Stats Backfill - Sleeper API")
    print("="*60)
    print(f"Season: {season}")
    print(f"Season Type: {season_type}")
    print(f"Weeks: {weeks if weeks else 'All available'}")
    print("="*60)
    print()

    async with AsyncSessionLocal() as session:
        try:
            # Validate data freshness first
            await validate_data_freshness(session)
            print()

            sleeper_service = get_sleeper_stats_service()

            # Get current NFL state
            nfl_state = await sleeper_service.get_nfl_state()
            current_week = nfl_state.get("week")
            current_season = nfl_state.get("season")

            print(f"📡 Current NFL State:")
            print(f"   Season: {current_season}")
            print(f"   Week: {current_week}")
            print(f"   Type: {nfl_state.get('season_type')}")
            print()

            # Determine weeks to process
            if not weeks:
                if season == current_season and season_type == nfl_state.get("season_type"):
                    # For current season, only go up to current week
                    weeks = list(range(1, current_week + 1))
                else:
                    # For past seasons, do all 18 weeks
                    max_week = 18 if season_type == "regular" else 5
                    weeks = list(range(1, max_week + 1))

            print(f"Processing {len(weeks)} weeks...")
            print()

            stats_created = 0
            stats_skipped = 0
            games_created = 0

            for week in weeks:
                print(f"Week {week}...")

                # Fetch all stats for this week
                week_stats = await sleeper_service.get_player_stats_for_week(
                    season=season,
                    week=week,
                    season_type=season_type
                )

                if not week_stats:
                    print(f"  No stats available for Week {week}")
                    continue

                print(f"  Found stats for {len(week_stats)} players")

                # Process each player's stats
                for sleeper_id, raw_stats in week_stats.items():
                    # Check if this player exists in our database with Sleeper ID
                    result = await session.execute(
                        select(Player).where(Player.sleeper_id == sleeper_id)
                    )
                    player = result.scalar_one_or_none()

                    if not player:
                        # Skip players we don't track
                        continue

                    # Normalize stats to our schema
                    normalized_stats = sleeper_service.normalize_stats(raw_stats)

                    # Skip if player didn't play (no meaningful stats)
                    if not any(normalized_stats.values()):
                        continue

                    # Check if stat already exists
                    stat_id = f"{player.id}_{season}_{week}"
                    existing = await session.get(PlayerGameStats, stat_id)

                    if existing:
                        stats_skipped += 1
                        continue

                    # Create PlayerGameStats entry (game_id is optional - Sleeper doesn't provide game details)
                    game_stat = PlayerGameStats(
                        id=stat_id,
                        player_id=player.id,
                        game_id=None,  # Sleeper doesn't provide full game details
                        season=int(season),
                        week=week,
                        **normalized_stats
                    )

                    session.add(game_stat)
                    stats_created += 1

                await session.commit()
                print(f"  ✓ Week {week} complete")

            print()
            print("="*60)
            print(f"✓ Backfill complete")
            print(f"  Stats created: {stats_created}")
            print(f"  Stats skipped (already exist): {stats_skipped}")
            print("="*60)

        except Exception as e:
            logger.error("backfill_error", error=str(e))
            print(f"\n✗ Error: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill player stats from Sleeper API")
    parser.add_argument("--season", type=str, default="2025", help="Season year (default: 2025)")
    parser.add_argument("--weeks", type=int, nargs="+", help="Specific weeks to backfill (default: all)")
    parser.add_argument("--season-type", choices=["regular", "pre", "post"], default="regular")

    args = parser.parse_args()

    asyncio.run(backfill_from_sleeper(
        season=args.season,
        weeks=args.weeks,
        season_type=args.season_type
    ))
