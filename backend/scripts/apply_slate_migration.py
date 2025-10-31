"""Apply slate migration and backfill slate values for existing games"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models.nfl import Game, Prediction
from app.utils.slate import determine_slate
import structlog

logger = structlog.get_logger()


async def apply_migration():
    """Apply slate migration and backfill values"""
    print("Applying Slate Migration")
    print("="*60)

    async with AsyncSessionLocal() as session:
        try:
            # Add slate column to games table
            print("Adding slate column to games table...")
            await session.execute(text("""
                ALTER TABLE games
                ADD COLUMN IF NOT EXISTS slate VARCHAR
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_games_slate ON games(slate)
            """))

            # Add slate column to predictions table
            print("Adding slate column to predictions table...")
            await session.execute(text("""
                ALTER TABLE predictions
                ADD COLUMN IF NOT EXISTS slate VARCHAR
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_predictions_slate ON predictions(slate)
            """))

            await session.commit()
            print("✓ Columns added successfully")
            print()

            # Backfill slates for existing games
            print("Backfilling slates for existing games...")
            from sqlalchemy import select

            result = await session.execute(select(Game))
            games = result.scalars().all()

            games_updated = 0
            for game in games:
                if game.game_time and not game.slate:
                    slate = determine_slate(game.game_time)
                    game.slate = slate
                    games_updated += 1

            await session.commit()
            print(f"✓ Updated {games_updated} games with slate information")
            print()

            # Backfill slates for existing predictions
            print("Backfilling slates for existing predictions...")
            result = await session.execute(select(Prediction))
            predictions = result.scalars().all()

            predictions_updated = 0
            for pred in predictions:
                if pred.game_time and not pred.slate:
                    slate = determine_slate(pred.game_time)
                    pred.slate = slate
                    predictions_updated += 1

            await session.commit()
            print(f"✓ Updated {predictions_updated} predictions with slate information")
            print()

            print("="*60)
            print("✓ Migration complete!")
            print(f"  Games updated: {games_updated}")
            print(f"  Predictions updated: {predictions_updated}")
            print("="*60)

            logger.info(
                "slate_migration_complete",
                games_updated=games_updated,
                predictions_updated=predictions_updated
            )

        except Exception as e:
            logger.error("migration_error", error=str(e))
            print(f"\n✗ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(apply_migration())
