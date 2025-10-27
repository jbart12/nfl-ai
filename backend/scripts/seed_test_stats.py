"""
Seed Test Game Stats

Creates realistic test game statistics for testing the prediction system.
Since ESPN API isn't responding, we'll use realistic test data.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, date
import uuid

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.nfl import Player, Game, PlayerGameStats
import structlog

logger = structlog.get_logger()


# Realistic test data for Patrick Mahomes 2024 season (first 5 games)
MAHOMES_STATS = [
    {"week": 1, "passing_yards": 291, "passing_tds": 2, "passing_completions": 20, "passing_attempts": 28, "interceptions": 0, "opponent": "DET"},
    {"week": 2, "passing_yards": 315, "passing_tds": 2, "passing_completions": 23, "passing_attempts": 30, "interceptions": 1, "opponent": "CIN"},
    {"week": 3, "passing_yards": 260, "passing_tds": 1, "passing_completions": 22, "passing_attempts": 32, "interceptions": 0, "opponent": "ATL"},
    {"week": 4, "passing_yards": 279, "passing_tds": 2, "passing_completions": 27, "passing_attempts": 37, "interceptions": 1, "opponent": "LAC"},
    {"week": 5, "passing_yards": 330, "passing_tds": 4, "passing_completions": 25, "passing_attempts": 33, "interceptions": 0, "opponent": "NO"},
]

# Josh Allen 2024 season stats
ALLEN_STATS = [
    {"week": 1, "passing_yards": 232, "passing_tds": 1, "passing_completions": 18, "passing_attempts": 26, "interceptions": 1, "opponent": "ARI"},
    {"week": 2, "passing_yards": 265, "passing_tds": 2, "passing_completions": 21, "passing_attempts": 31, "interceptions": 0, "opponent": "MIA"},
    {"week": 3, "passing_yards": 314, "passing_tds": 3, "passing_completions": 26, "passing_attempts": 32, "interceptions": 0, "opponent": "JAX"},
    {"week": 4, "passing_yards": 215, "passing_tds": 2, "passing_completions": 19, "passing_attempts": 27, "interceptions": 1, "opponent": "BAL"},
    {"week": 5, "passing_yards": 356, "passing_tds": 3, "passing_completions": 28, "passing_attempts": 34, "interceptions": 1, "opponent": "HOU"},
]

# Tyreek Hill 2024 season stats
HILL_STATS = [
    {"week": 1, "receiving_yards": 130, "receiving_tds": 1, "receiving_receptions": 7, "receiving_targets": 11, "opponent": "JAX"},
    {"week": 2, "receiving_yards": 80, "receiving_tds": 0, "receiving_receptions": 5, "receiving_targets": 8, "opponent": "BUF"},
    {"week": 3, "receiving_yards": 112, "receiving_tds": 2, "receiving_receptions": 8, "receiving_targets": 13, "opponent": "SEA"},
    {"week": 4, "receiving_yards": 95, "receiving_tds": 1, "receiving_receptions": 6, "receiving_targets": 9, "opponent": "TEN"},
    {"week": 5, "receiving_yards": 146, "receiving_tds": 1, "receiving_receptions": 9, "receiving_targets": 14, "opponent": "NE"},
]


async def create_game(session: AsyncSession, week: int, season: int, home_team: str, away_team: str, player_team: str) -> str:
    """Create a test game"""
    game_id = f"2024_{week}_{home_team}_{away_team}"

    existing = await session.get(Game, game_id)
    if existing:
        return game_id

    # Calculate game date (Sep 8 start + 7 days per week, handling month boundaries)
    day = 8 + ((week - 1) * 7)
    month = 9
    if day > 30:  # September has 30 days
        day -= 30
        month = 10

    game = Game(
        id=game_id,
        season=season,
        week=week,
        game_date=date(2024, month, day),
        home_team_id=home_team,
        away_team_id=away_team,
        opponent_team_id=away_team if player_team == home_team else home_team,
        is_completed=True,
        home_score=27,
        away_score=24
    )

    session.add(game)
    return game_id


async def seed_test_stats():
    """Seed test game statistics"""
    print("Test Game Stats Seeder")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            stats_added = 0

            # Patrick Mahomes stats
            logger.info("seeding_mahomes_stats", count=len(MAHOMES_STATS))
            for stat in MAHOMES_STATS:
                game_id = await create_game(
                    session, stat["week"], 2024,
                    "KC", stat["opponent"], "KC"
                )

                stat_id = f"mahomes_{stat['week']}_2024"
                existing = await session.get(PlayerGameStats, stat_id)

                if not existing:
                    game_stat = PlayerGameStats(
                        id=stat_id,
                        player_id="mahomes_patrick",
                        game_id=game_id,
                        season=2024,
                        week=stat["week"],
                        passing_yards=stat["passing_yards"],
                        passing_touchdowns=stat["passing_tds"],
                        passing_completions=stat["passing_completions"],
                        passing_attempts=stat["passing_attempts"],
                        interceptions=stat["interceptions"]
                    )
                    session.add(game_stat)
                    stats_added += 1

            # Josh Allen stats
            logger.info("seeding_allen_stats", count=len(ALLEN_STATS))
            for stat in ALLEN_STATS:
                game_id = await create_game(
                    session, stat["week"], 2024,
                    "BUF", stat["opponent"], "BUF"
                )

                stat_id = f"allen_{stat['week']}_2024"
                existing = await session.get(PlayerGameStats, stat_id)

                if not existing:
                    game_stat = PlayerGameStats(
                        id=stat_id,
                        player_id="allen_josh",
                        game_id=game_id,
                        season=2024,
                        week=stat["week"],
                        passing_yards=stat["passing_yards"],
                        passing_touchdowns=stat["passing_tds"],
                        passing_completions=stat["passing_completions"],
                        passing_attempts=stat["passing_attempts"],
                        interceptions=stat["interceptions"]
                    )
                    session.add(game_stat)
                    stats_added += 1

            # Tyreek Hill stats
            logger.info("seeding_hill_stats", count=len(HILL_STATS))
            for stat in HILL_STATS:
                game_id = await create_game(
                    session, stat["week"], 2024,
                    "MIA", stat["opponent"], "MIA"
                )

                stat_id = f"hill_{stat['week']}_2024"
                existing = await session.get(PlayerGameStats, stat_id)

                if not existing:
                    game_stat = PlayerGameStats(
                        id=stat_id,
                        player_id="hill_tyreek",
                        game_id=game_id,
                        season=2024,
                        week=stat["week"],
                        receiving_yards=stat["receiving_yards"],
                        receiving_touchdowns=stat["receiving_tds"],
                        receiving_receptions=stat["receiving_receptions"],
                        receiving_targets=stat["receiving_targets"]
                    )
                    session.add(game_stat)
                    stats_added += 1

            await session.commit()
            logger.info("stats_seeded_success", count=stats_added)

            print(f"\n✓ Successfully seeded {stats_added} game stats")
            print("\nStats Summary:")
            print("=" * 60)
            print(f"  Patrick Mahomes (QB): {len(MAHOMES_STATS)} games")
            print(f"  Josh Allen (QB): {len(ALLEN_STATS)} games")
            print(f"  Tyreek Hill (WR): {len(HILL_STATS)} games")
            print("\n✓ Test stats seeding completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error("seeding_failed", error=str(e))
            print(f"\n✗ Error seeding stats: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_test_stats())
