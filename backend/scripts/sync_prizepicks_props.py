"""
Sync PrizePicks Props

Fetches current player prop lines from PrizePicks and stores them in the database.
This provides real betting lines instead of hardcoded values.

Usage:
    python -m scripts.sync_prizepicks_props
"""
import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any
import structlog

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select, update, delete, func
from app.core.database import AsyncSessionLocal
from app.models.nfl import PrizePicksProjection
from app.services.prizepicks import get_prizepicks_service

logger = structlog.get_logger()


async def sync_prizepicks_props():
    """
    Sync current PrizePicks props to database.

    This replaces all active props with the latest from PrizePicks API.
    """
    logger.info("sync_start", timestamp=datetime.utcnow())

    # Fetch latest props from PrizePicks
    pp_service = get_prizepicks_service()
    projections = await pp_service.fetch_nfl_projections()

    if not projections:
        logger.error("no_projections_fetched")
        print("❌ Failed to fetch projections from PrizePicks")
        return

    print(f"✓ Fetched {len(projections)} projections from PrizePicks")

    async with AsyncSessionLocal() as db:
        try:
            # Deactivate all existing projections
            await db.execute(
                update(PrizePicksProjection)
                .values(is_active=False)
            )

            # Add new projections
            new_count = 0
            updated_count = 0

            for proj in projections:
                # Check if projection already exists
                result = await db.execute(
                    select(PrizePicksProjection).where(
                        PrizePicksProjection.external_id == proj['prizepicks_id']
                    )
                )
                existing = result.scalar_one_or_none()

                game_time = None
                if proj.get('start_time'):
                    try:
                        game_time = datetime.fromisoformat(
                            proj['start_time'].replace('Z', '+00:00')
                        )
                        # Convert to naive datetime for database storage
                        game_time = game_time.replace(tzinfo=None)
                    except:
                        pass

                if existing:
                    # Update existing projection
                    existing.line_score = proj['line_score']
                    existing.game_time = game_time
                    existing.is_active = True
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new projection
                    new_proj = PrizePicksProjection(
                        id=proj['prizepicks_id'],
                        external_id=proj['prizepicks_id'],
                        player_name=proj['player_name'],
                        stat_type=proj['stat_type'],
                        line_score=proj['line_score'],
                        league='NFL',
                        game_time=game_time,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(new_proj)
                    new_count += 1

            await db.commit()

            print(f"✓ Synced projections:")
            print(f"  - New: {new_count}")
            print(f"  - Updated: {updated_count}")
            print(f"  - Total active: {new_count + updated_count}")

            logger.info(
                "sync_complete",
                new=new_count,
                updated=updated_count,
                total=new_count + updated_count
            )

            # Show breakdown by stat type
            result = await db.execute(
                select(
                    PrizePicksProjection.stat_type,
                    func.count(PrizePicksProjection.id)
                )
                .where(PrizePicksProjection.is_active == True)
                .group_by(PrizePicksProjection.stat_type)
            )

            print("\nProps by stat type:")
            for stat_type, count in result.all():
                print(f"  {stat_type}: {count}")

        except Exception as e:
            await db.rollback()
            logger.error("sync_error", error=str(e))
            print(f"❌ Error: {e}")
            raise


if __name__ == "__main__":
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )

    asyncio.run(sync_prizepicks_props())
