"""
Test Main Line Detection

Validates that our smart main line detection picks the correct lines.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.nfl import PrizePicksProjection
from app.services.batch_predictions import BatchPredictionService


async def test_main_line_detection():
    """Test main line detection with real PrizePicks data"""

    service = BatchPredictionService()

    async with AsyncSessionLocal() as db:
        # Get all props for a test player
        test_players = [
            "Jaxon Smith-Njigba",
            "CeeDee Lamb",
            "Patrick Mahomes",
            "Derrick Henry",
        ]

        for player_name in test_players:
            print(f"\n{'='*80}")
            print(f"Testing: {player_name}")
            print(f"{'='*80}")

            # Get props for this player
            result = await db.execute(
                select(PrizePicksProjection).where(
                    PrizePicksProjection.player_name == player_name,
                    PrizePicksProjection.is_active == True
                )
            )
            props = result.scalars().all()

            if not props:
                print(f"❌ No props found for {player_name}")
                continue

            # Group by stat type
            props_by_stat = {}
            for prop in props:
                if prop.stat_type not in props_by_stat:
                    props_by_stat[prop.stat_type] = []
                props_by_stat[prop.stat_type].append(prop.line_score)

            # Get all lines for each stat type (for frequency analysis)
            all_lines_by_stat = {}
            for stat_type in props_by_stat.keys():
                result = await db.execute(
                    select(PrizePicksProjection.line_score).where(
                        PrizePicksProjection.stat_type == stat_type,
                        PrizePicksProjection.is_active == True
                    )
                )
                all_lines_by_stat[stat_type] = [r[0] for r in result.all()]

            # Test main line detection for each stat type
            for stat_type, lines in sorted(props_by_stat.items()):
                sorted_lines = sorted(lines)
                median_line = sorted_lines[len(sorted_lines) // 2]

                main_line = service._detect_main_line(
                    lines,
                    all_lines_by_stat.get(stat_type, [])
                )

                print(f"\n{stat_type}:")
                print(f"  All lines: {sorted_lines}")
                print(f"  Simple median: {median_line}")
                print(f"  Smart detection: {main_line} ✓")

                # Show if they differ
                if main_line != median_line:
                    print(f"  → Smart algorithm picked different line!")


if __name__ == "__main__":
    asyncio.run(test_main_line_detection())
