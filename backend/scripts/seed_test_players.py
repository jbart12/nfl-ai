"""
Seed Test Players

Adds a few well-known NFL players for testing the prediction system.
These players have real ESPN IDs so we can backfill their stats.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.nfl import Player
import structlog

logger = structlog.get_logger()

# Test players with ESPN IDs
TEST_PLAYERS = [
    {
        "id": "mahomes_patrick",
        "name": "Patrick Mahomes",
        "player_position": "QB",
        "team_id": "KC",
        "jersey_number": 15,
        "espn_id": "3139477",  # Patrick Mahomes ESPN ID
        "status": "ACTIVE"
    },
    {
        "id": "allen_josh",
        "name": "Josh Allen",
        "player_position": "QB",
        "team_id": "BUF",
        "jersey_number": 17,
        "espn_id": "3918298",  # Josh Allen ESPN ID
        "status": "ACTIVE"
    },
    {
        "id": "mccaffrey_christian",
        "name": "Christian McCaffrey",
        "player_position": "RB",
        "team_id": "SF",
        "jersey_number": 23,
        "espn_id": "3116385",  # Christian McCaffrey ESPN ID
        "status": "ACTIVE"
    },
    {
        "id": "hill_tyreek",
        "name": "Tyreek Hill",
        "player_position": "WR",
        "team_id": "MIA",
        "jersey_number": 10,
        "espn_id": "3043078",  # Tyreek Hill ESPN ID
        "status": "ACTIVE"
    },
    {
        "id": "kelce_travis",
        "name": "Travis Kelce",
        "player_position": "TE",
        "team_id": "KC",
        "jersey_number": 87,
        "espn_id": "2566",  # Travis Kelce ESPN ID
        "status": "ACTIVE"
    },
]


async def seed_test_players():
    """Seed test players into the database"""
    print("Test Players Seeder")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            # Check how many already exist
            existing_count = 0
            for player_data in TEST_PLAYERS:
                existing = await session.get(Player, player_data["id"])
                if existing:
                    existing_count += 1
                    logger.info("player_exists", player=player_data["name"])

            if existing_count == len(TEST_PLAYERS):
                logger.info("all_players_exist", count=len(TEST_PLAYERS))
                print(f"\n✓ All {len(TEST_PLAYERS)} test players already exist")
                return

            # Add players
            logger.info("seeding_players", count=len(TEST_PLAYERS))

            for player_data in TEST_PLAYERS:
                existing = await session.get(Player, player_data["id"])
                if not existing:
                    player = Player(**player_data)
                    session.add(player)
                    logger.info("player_added", player=player_data["name"])

            await session.commit()
            logger.info("players_seeded_success", count=len(TEST_PLAYERS))

            print(f"\n✓ Successfully seeded {len(TEST_PLAYERS)} test players")
            print("\nSeeded Players:")
            print("=" * 60)
            for player_data in TEST_PLAYERS:
                print(f"  {player_data['player_position']:3} {player_data['name']:25} ({player_data['team_id']}) - ESPN ID: {player_data['espn_id']}")

            print("\n✓ Players seeding completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error("seeding_failed", error=str(e))
            print(f"\n✗ Error seeding players: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_test_players())
