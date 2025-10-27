"""
Populate NFL Teams

Creates all 32 NFL teams in the database.
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

# All 32 NFL Teams
NFL_TEAMS = [
    # AFC East
    {"id": "BUF", "name": "Buffalo Bills", "conference": "AFC", "division": "East"},
    {"id": "MIA", "name": "Miami Dolphins", "conference": "AFC", "division": "East"},
    {"id": "NE", "name": "New England Patriots", "conference": "AFC", "division": "East"},
    {"id": "NYJ", "name": "New York Jets", "conference": "AFC", "division": "East"},

    # AFC North
    {"id": "BAL", "name": "Baltimore Ravens", "conference": "AFC", "division": "North"},
    {"id": "CIN", "name": "Cincinnati Bengals", "conference": "AFC", "division": "North"},
    {"id": "CLE", "name": "Cleveland Browns", "conference": "AFC", "division": "North"},
    {"id": "PIT", "name": "Pittsburgh Steelers", "conference": "AFC", "division": "North"},

    # AFC South
    {"id": "HOU", "name": "Houston Texans", "conference": "AFC", "division": "South"},
    {"id": "IND", "name": "Indianapolis Colts", "conference": "AFC", "division": "South"},
    {"id": "JAX", "name": "Jacksonville Jaguars", "conference": "AFC", "division": "South"},
    {"id": "TEN", "name": "Tennessee Titans", "conference": "AFC", "division": "South"},

    # AFC West
    {"id": "DEN", "name": "Denver Broncos", "conference": "AFC", "division": "West"},
    {"id": "KC", "name": "Kansas City Chiefs", "conference": "AFC", "division": "West"},
    {"id": "LV", "name": "Las Vegas Raiders", "conference": "AFC", "division": "West"},
    {"id": "LAC", "name": "Los Angeles Chargers", "conference": "AFC", "division": "West"},

    # NFC East
    {"id": "DAL", "name": "Dallas Cowboys", "conference": "NFC", "division": "East"},
    {"id": "NYG", "name": "New York Giants", "conference": "NFC", "division": "East"},
    {"id": "PHI", "name": "Philadelphia Eagles", "conference": "NFC", "division": "East"},
    {"id": "WSH", "name": "Washington Commanders", "conference": "NFC", "division": "East"},

    # NFC North
    {"id": "CHI", "name": "Chicago Bears", "conference": "NFC", "division": "North"},
    {"id": "DET", "name": "Detroit Lions", "conference": "NFC", "division": "North"},
    {"id": "GB", "name": "Green Bay Packers", "conference": "NFC", "division": "North"},
    {"id": "MIN", "name": "Minnesota Vikings", "conference": "NFC", "division": "North"},

    # NFC South
    {"id": "ATL", "name": "Atlanta Falcons", "conference": "NFC", "division": "South"},
    {"id": "CAR", "name": "Carolina Panthers", "conference": "NFC", "division": "South"},
    {"id": "NO", "name": "New Orleans Saints", "conference": "NFC", "division": "South"},
    {"id": "TB", "name": "Tampa Bay Buccaneers", "conference": "NFC", "division": "South"},

    # NFC West
    {"id": "ARI", "name": "Arizona Cardinals", "conference": "NFC", "division": "West"},
    {"id": "LA", "name": "Los Angeles Rams", "conference": "NFC", "division": "West"},
    {"id": "SF", "name": "San Francisco 49ers", "conference": "NFC", "division": "West"},
    {"id": "SEA", "name": "Seattle Seahawks", "conference": "NFC", "division": "West"},
]


async def populate_teams():
    """Populate all NFL teams"""
    print("NFL Teams Population")
    print("="*60)

    async with AsyncSessionLocal() as session:
        try:
            added = 0
            skipped = 0

            for team_data in NFL_TEAMS:
                # Check if team exists
                existing = await session.get(Team, team_data["id"])

                if existing:
                    skipped += 1
                    continue

                # Create new team
                new_team = Team(**team_data)
                session.add(new_team)
                added += 1

            await session.commit()

            print(f"✓ Teams added: {added}")
            print(f"✓ Teams skipped (already exist): {skipped}")
            print("="*60)

            logger.info("teams_populated", added=added, skipped=skipped)

        except Exception as e:
            logger.error("populate_teams_error", error=str(e))
            print(f"\n✗ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(populate_teams())
