"""
Seed NFL Teams Data

Populates the teams table with all 32 NFL teams.
Run this script after initial migration to set up base data.

Usage:
    python -m scripts.seed_teams
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.nfl import Team
import structlog

logger = structlog.get_logger()


# All 32 NFL Teams (2025 Season)
NFL_TEAMS = [
    # AFC East
    {"id": "BUF", "name": "Bills", "city": "Buffalo", "conference": "AFC", "division": "East"},
    {"id": "MIA", "name": "Dolphins", "city": "Miami", "conference": "AFC", "division": "East"},
    {"id": "NE", "name": "Patriots", "city": "New England", "conference": "AFC", "division": "East"},
    {"id": "NYJ", "name": "Jets", "city": "New York", "conference": "AFC", "division": "East"},

    # AFC North
    {"id": "BAL", "name": "Ravens", "city": "Baltimore", "conference": "AFC", "division": "North"},
    {"id": "CIN", "name": "Bengals", "city": "Cincinnati", "conference": "AFC", "division": "North"},
    {"id": "CLE", "name": "Browns", "city": "Cleveland", "conference": "AFC", "division": "North"},
    {"id": "PIT", "name": "Steelers", "city": "Pittsburgh", "conference": "AFC", "division": "North"},

    # AFC South
    {"id": "HOU", "name": "Texans", "city": "Houston", "conference": "AFC", "division": "South"},
    {"id": "IND", "name": "Colts", "city": "Indianapolis", "conference": "AFC", "division": "South"},
    {"id": "JAX", "name": "Jaguars", "city": "Jacksonville", "conference": "AFC", "division": "South"},
    {"id": "TEN", "name": "Titans", "city": "Tennessee", "conference": "AFC", "division": "South"},

    # AFC West
    {"id": "DEN", "name": "Broncos", "city": "Denver", "conference": "AFC", "division": "West"},
    {"id": "KC", "name": "Chiefs", "city": "Kansas City", "conference": "AFC", "division": "West"},
    {"id": "LV", "name": "Raiders", "city": "Las Vegas", "conference": "AFC", "division": "West"},
    {"id": "LAC", "name": "Chargers", "city": "Los Angeles", "conference": "AFC", "division": "West"},

    # NFC East
    {"id": "DAL", "name": "Cowboys", "city": "Dallas", "conference": "NFC", "division": "East"},
    {"id": "NYG", "name": "Giants", "city": "New York", "conference": "NFC", "division": "East"},
    {"id": "PHI", "name": "Eagles", "city": "Philadelphia", "conference": "NFC", "division": "East"},
    {"id": "WAS", "name": "Commanders", "city": "Washington", "conference": "NFC", "division": "East"},

    # NFC North
    {"id": "CHI", "name": "Bears", "city": "Chicago", "conference": "NFC", "division": "North"},
    {"id": "DET", "name": "Lions", "city": "Detroit", "conference": "NFC", "division": "North"},
    {"id": "GB", "name": "Packers", "city": "Green Bay", "conference": "NFC", "division": "North"},
    {"id": "MIN", "name": "Vikings", "city": "Minnesota", "conference": "NFC", "division": "North"},

    # NFC South
    {"id": "ATL", "name": "Falcons", "city": "Atlanta", "conference": "NFC", "division": "South"},
    {"id": "CAR", "name": "Panthers", "city": "Carolina", "conference": "NFC", "division": "South"},
    {"id": "NO", "name": "Saints", "city": "New Orleans", "conference": "NFC", "division": "South"},
    {"id": "TB", "name": "Buccaneers", "city": "Tampa Bay", "conference": "NFC", "division": "South"},

    # NFC West
    {"id": "ARI", "name": "Cardinals", "city": "Arizona", "conference": "NFC", "division": "West"},
    {"id": "LAR", "name": "Rams", "city": "Los Angeles", "conference": "NFC", "division": "West"},
    {"id": "SF", "name": "49ers", "city": "San Francisco", "conference": "NFC", "division": "West"},
    {"id": "SEA", "name": "Seahawks", "city": "Seattle", "conference": "NFC", "division": "West"},
]


async def seed_teams():
    """Seed the teams table with all 32 NFL teams"""
    async with AsyncSessionLocal() as session:
        try:
            logger.info("seeding_teams", count=len(NFL_TEAMS))

            # Check if teams already exist
            from sqlalchemy import select
            result = await session.execute(select(Team))
            existing_teams = result.scalars().all()

            if existing_teams:
                logger.info("teams_already_seeded", count=len(existing_teams))
                print(f"✓ Teams already seeded ({len(existing_teams)} teams)")
                return

            # Insert all teams
            teams_created = 0
            for team_data in NFL_TEAMS:
                team = Team(**team_data)
                session.add(team)
                teams_created += 1

            await session.commit()

            logger.info("teams_seeded_success", count=teams_created)
            print(f"✓ Successfully seeded {teams_created} NFL teams")

            # Display summary by division
            print("\nSeeded Teams by Division:")
            print("=" * 60)

            for conference in ["AFC", "NFC"]:
                print(f"\n{conference}:")
                for division in ["East", "North", "South", "West"]:
                    teams = [t for t in NFL_TEAMS
                            if t["conference"] == conference and t["division"] == division]
                    team_names = [f"{t['city']} {t['name']}" for t in teams]
                    print(f"  {division}: {', '.join(team_names)}")

        except Exception as e:
            await session.rollback()
            logger.error("seed_teams_error", error=str(e))
            print(f"✗ Error seeding teams: {e}")
            raise


async def main():
    """Main entry point"""
    print("NFL Teams Data Seeder")
    print("=" * 60)

    try:
        await seed_teams()
        print("\n✓ Teams seeding completed successfully")
    except Exception as e:
        print(f"\n✗ Teams seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
