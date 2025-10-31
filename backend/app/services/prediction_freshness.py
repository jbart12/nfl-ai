"""
Prediction Freshness Service

Ensures predictions are always up-to-date and automatically deactivates stale data.

This service:
1. Deactivates predictions past game time
2. Deactivates predictions older than 24 hours
3. Provides version tracking to invalidate old prediction logic
4. Ensures only fresh predictions are shown to users
"""
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from datetime import datetime, timedelta
from typing import Dict, Any

from app.models.nfl import Prediction

logger = structlog.get_logger()

# Version tracking - increment this when prediction logic changes
CURRENT_PREDICTION_VERSION = "v2_prizepicks"  # v2 = PrizePicks integration


class PredictionFreshnessService:
    """Service to maintain prediction freshness"""

    def __init__(self):
        self.max_age_hours = 24  # Predictions older than 24h are stale

    async def cleanup_stale_predictions(self, db: AsyncSession) -> Dict[str, int]:
        """
        Deactivate stale predictions.

        Deactivates predictions that are:
        1. Past their game time
        2. Older than 24 hours
        3. From old prediction versions

        Returns:
            Dictionary with counts of deactivated predictions
        """
        now = datetime.utcnow()
        cutoff_time = now - timedelta(hours=self.max_age_hours)

        deactivated_counts = {
            "past_game_time": 0,
            "too_old": 0,
            "wrong_version": 0,
            "total": 0
        }

        # 1. Deactivate predictions past game time
        result = await db.execute(
            update(Prediction)
            .where(
                and_(
                    Prediction.is_active == True,
                    Prediction.game_time.isnot(None),
                    Prediction.game_time < now
                )
            )
            .values(is_active=False, updated_at=now)
        )
        deactivated_counts["past_game_time"] = result.rowcount

        # 2. Deactivate predictions older than 24 hours
        result = await db.execute(
            update(Prediction)
            .where(
                and_(
                    Prediction.is_active == True,
                    Prediction.created_at < cutoff_time
                )
            )
            .values(is_active=False, updated_at=now)
        )
        deactivated_counts["too_old"] = result.rowcount

        # 3. Deactivate predictions from old versions
        result = await db.execute(
            update(Prediction)
            .where(
                and_(
                    Prediction.is_active == True,
                    Prediction.model_version != CURRENT_PREDICTION_VERSION
                )
            )
            .values(is_active=False, updated_at=now)
        )
        deactivated_counts["wrong_version"] = result.rowcount

        await db.commit()

        deactivated_counts["total"] = (
            deactivated_counts["past_game_time"] +
            deactivated_counts["too_old"] +
            deactivated_counts["wrong_version"]
        )

        if deactivated_counts["total"] > 0:
            logger.info(
                "stale_predictions_deactivated",
                **deactivated_counts
            )

        return deactivated_counts

    async def get_prediction_freshness_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Get statistics about prediction freshness.

        Returns:
            Dictionary with freshness metrics
        """
        now = datetime.utcnow()
        cutoff_time = now - timedelta(hours=self.max_age_hours)

        # Count active predictions
        result = await db.execute(
            select(Prediction)
            .where(Prediction.is_active == True)
        )
        active_predictions = result.scalars().all()

        stats = {
            "total_active": len(active_predictions),
            "fresh": 0,
            "stale_but_active": 0,
            "past_game_time": 0,
            "wrong_version": 0,
            "current_version": CURRENT_PREDICTION_VERSION
        }

        for pred in active_predictions:
            # Check if stale
            if pred.created_at < cutoff_time:
                stats["stale_but_active"] += 1
            else:
                stats["fresh"] += 1

            # Check if past game time
            if pred.game_time and pred.game_time < now:
                stats["past_game_time"] += 1

            # Check version
            if pred.model_version != CURRENT_PREDICTION_VERSION:
                stats["wrong_version"] += 1

        return stats


# Global instance
_freshness_service = None


def get_freshness_service() -> PredictionFreshnessService:
    """Get the global freshness service instance"""
    global _freshness_service
    if _freshness_service is None:
        _freshness_service = PredictionFreshnessService()
    return _freshness_service
