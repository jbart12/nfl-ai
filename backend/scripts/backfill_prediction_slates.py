"""
Backfill slate values for existing predictions based on game_time

Usage:
    python -m scripts.backfill_prediction_slates
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.nfl import Prediction
from app.utils.slate import determine_slate
import pytz


async def backfill_slates():
    """Backfill game_time and slate values for predictions from games table"""
    from app.models.nfl import Game

    async with AsyncSessionLocal() as db:
        # Get all predictions with null slate
        result = await db.execute(
            select(Prediction).where(Prediction.slate.is_(None))
        )
        predictions = result.scalars().all()

        print(f"Found {len(predictions)} predictions to update")

        # Build a mapping of (team, opponent, week) -> game
        games_result = await db.execute(select(Game))
        games = games_result.scalars().all()

        game_map = {}
        for game in games:
            # Map for home team
            key = (game.home_team_id, game.away_team_id, game.week, game.season)
            game_map[key] = game
            # Map for away team
            key = (game.away_team_id, game.home_team_id, game.week, game.season)
            game_map[key] = game

        print(f"Built game mapping with {len(games)} games")

        updated = 0
        skipped = 0
        for pred in predictions:
            # Find the matching game
            key = (pred.team, pred.opponent, pred.week, pred.season)
            game = game_map.get(key)

            if game and game.game_time and game.slate:
                pred.game_time = game.game_time
                pred.slate = game.slate
                updated += 1

                if updated % 100 == 0:
                    print(f"Updated {updated} predictions...")
            else:
                skipped += 1

        await db.commit()
        print(f"✓ Successfully updated {updated} predictions with game_time and slate")
        print(f"  Skipped {skipped} predictions (no matching game found)")

        # Show breakdown by slate
        result = await db.execute(
            select(Prediction.slate, func.count(Prediction.id))
            .group_by(Prediction.slate)
        )
        print("\nSlate breakdown:")
        for slate, count in result.all():
            print(f"  {slate or 'NULL'}: {count}")


if __name__ == "__main__":
    asyncio.run(backfill_slates())
