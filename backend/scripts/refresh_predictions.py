"""
Refresh All Predictions

Complete refresh of prediction data:
1. Sync latest props from PrizePicks
2. Clean up stale predictions
3. Regenerate predictions with fresh data

This should be run:
- After any prediction logic changes
- Daily during game weeks
- When data quality issues are detected

Usage:
    python -m scripts.refresh_predictions
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import AsyncSessionLocal
from app.services.prediction_freshness import get_freshness_service
from app.services.batch_predictions import get_batch_prediction_service
from app.services.prizepicks import get_prizepicks_service
from sqlalchemy import select, func
from app.models.nfl import PrizePicksProjection, Prediction
import structlog

logger = structlog.get_logger()


async def refresh_all_predictions():
    """Complete prediction refresh workflow"""

    print("="*80)
    print("PREDICTION REFRESH - COMPLETE WORKFLOW")
    print("="*80)
    print()

    # Step 1: Sync PrizePicks props
    print("Step 1: Syncing latest props from PrizePicks...")
    from scripts.sync_prizepicks_props import sync_prizepicks_props
    await sync_prizepicks_props()
    print()

    # Step 2: Clean up stale predictions
    print("Step 2: Cleaning up stale predictions...")
    async with AsyncSessionLocal() as db:
        freshness_service = get_freshness_service()
        stats = await freshness_service.cleanup_stale_predictions(db)

        print(f"  Deactivated predictions:")
        print(f"    - Past game time: {stats['past_game_time']}")
        print(f"    - Too old (>24h): {stats['too_old']}")
        print(f"    - Wrong version: {stats['wrong_version']}")
        print(f"    - Total: {stats['total']}")
    print()

    # Step 3: Check current state
    print("Step 3: Checking current prediction state...")
    async with AsyncSessionLocal() as db:
        # Count active predictions
        result = await db.execute(
            select(func.count(Prediction.id)).where(Prediction.is_active == True)
        )
        active_count = result.scalar()

        # Count PrizePicks props
        result = await db.execute(
            select(func.count(PrizePicksProjection.id)).where(PrizePicksProjection.is_active == True)
        )
        props_count = result.scalar()

        print(f"  Active predictions: {active_count}")
        print(f"  Available PrizePicks props: {props_count}")
    print()

    # Step 4: Regenerate predictions
    print("Step 4: Generating predictions with real PrizePicks lines...")
    async with AsyncSessionLocal() as db:
        batch_service = get_batch_prediction_service()
        result = await batch_service.generate_weekly_predictions(
            db=db,
            week=9,  # Current week
            season=2025
        )

        print(f"  Predictions generated: {result['predictions_generated']}")
        print(f"  Predictions failed: {result['predictions_failed']}")
        print(f"  Games processed: {result['games_found']}")
        print(f"  Players processed: {result['players_processed']}")
    print()

    # Step 5: Final validation
    print("Step 5: Validating refresh...")
    async with AsyncSessionLocal() as db:
        freshness_service = get_freshness_service()
        stats = await freshness_service.get_prediction_freshness_stats(db)

        print(f"  Freshness stats:")
        print(f"    - Total active: {stats['total_active']}")
        print(f"    - Fresh (<24h): {stats['fresh']}")
        print(f"    - Stale but active: {stats['stale_but_active']}")
        print(f"    - Past game time: {stats['past_game_time']}")
        print(f"    - Wrong version: {stats['wrong_version']}")
        print(f"    - Current version: {stats['current_version']}")

        if stats['stale_but_active'] > 0 or stats['wrong_version'] > 0:
            print()
            print(f"  ⚠️  WARNING: {stats['stale_but_active'] + stats['wrong_version']} stale predictions still active!")
        else:
            print()
            print("  ✅ All predictions are fresh and up-to-date!")
    print()

    print("="*80)
    print("REFRESH COMPLETE")
    print("="*80)


if __name__ == "__main__":
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )

    asyncio.run(refresh_all_predictions())
