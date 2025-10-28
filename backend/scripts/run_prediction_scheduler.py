"""
Prediction Scheduler

Automated scheduler that generates predictions for upcoming games.
Runs every 6 hours to keep the opportunities feed fresh.

Usage:
    python -m scripts.run_prediction_scheduler
"""
import asyncio
import structlog
from datetime import datetime, timedelta
from sqlalchemy import select, and_
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import AsyncSessionLocal
from app.models.nfl import Game
from app.services.batch_predictions import get_batch_prediction_service
from app.services.sleeper_stats import get_sleeper_stats_service

logger = structlog.get_logger()


async def run_scheduler_iteration():
    """Run one iteration of the scheduler"""
    logger.info("scheduler_iteration_start", timestamp=datetime.utcnow())

    async with AsyncSessionLocal() as db:
        try:
            # Get current NFL state
            sleeper_service = get_sleeper_stats_service()
            nfl_state = await sleeper_service.get_nfl_state()
            current_week = nfl_state.get("week")
            current_season = nfl_state.get("season", "2025")

            logger.info(
                "nfl_state_fetched",
                week=current_week,
                season=current_season,
                season_type=nfl_state.get("season_type")
            )

            # Check if we have games for this week
            games_query = select(Game).where(
                and_(
                    Game.week == current_week,
                    Game.season == int(current_season),
                    Game.is_completed == False
                )
            )

            result = await db.execute(games_query)
            games = result.scalars().all()

            if not games:
                logger.warning(
                    "no_upcoming_games",
                    week=current_week,
                    message="No games scheduled. May need to fetch schedule."
                )
                return

            logger.info("upcoming_games_found", count=len(games), week=current_week)

            # Generate predictions for current week
            batch_service = get_batch_prediction_service()

            result = await batch_service.generate_weekly_predictions(
                db=db,
                week=current_week,
                season=int(current_season)
            )

            logger.info(
                "scheduler_iteration_complete",
                week=current_week,
                predictions_generated=result.get("predictions_generated"),
                predictions_failed=result.get("predictions_failed"),
                games_processed=result.get("games_found")
            )

        except Exception as e:
            logger.error("scheduler_iteration_error", error=str(e))
            raise


async def run_scheduler_loop(interval_hours: int = 6):
    """
    Run the scheduler in a continuous loop.

    Args:
        interval_hours: Hours between each run
    """
    logger.info(
        "scheduler_started",
        interval_hours=interval_hours,
        next_run=datetime.utcnow() + timedelta(hours=interval_hours)
    )

    while True:
        try:
            await run_scheduler_iteration()

            # Wait for next iteration
            wait_seconds = interval_hours * 3600
            logger.info(
                "scheduler_sleeping",
                hours=interval_hours,
                next_run=(datetime.utcnow() + timedelta(seconds=wait_seconds)).isoformat()
            )

            await asyncio.sleep(wait_seconds)

        except KeyboardInterrupt:
            logger.info("scheduler_shutdown", reason="keyboard_interrupt")
            break
        except Exception as e:
            logger.error("scheduler_loop_error", error=str(e))
            # Wait 30 minutes before retrying on error
            logger.info("scheduler_retry", retry_in_minutes=30)
            await asyncio.sleep(1800)


async def run_once():
    """Run the scheduler once (for manual triggering)"""
    logger.info("running_scheduler_once")
    await run_scheduler_iteration()
    logger.info("scheduler_run_complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NFL Prediction Scheduler")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (instead of continuous loop)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=6,
        help="Hours between runs (default: 6)"
    )

    args = parser.parse_args()

    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )

    if args.once:
        asyncio.run(run_once())
    else:
        asyncio.run(run_scheduler_loop(interval_hours=args.interval))
