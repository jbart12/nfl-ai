"""
Clear Old Predictions

Deactivates old predictions that were generated with hardcoded lines
before PrizePicks integration.

Usage:
    python -m scripts.clear_old_predictions
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import update
from app.core.database import AsyncSessionLocal
from app.models.nfl import Prediction


async def clear_old_predictions():
    """Deactivate all old predictions to prepare for regeneration with real lines"""

    async with AsyncSessionLocal() as db:
        print("Deactivating old predictions...")

        # Deactivate all active predictions
        result = await db.execute(
            update(Prediction)
            .where(Prediction.is_active == True)
            .values(is_active=False, updated_at=datetime.utcnow())
        )

        await db.commit()

        print(f"✓ Deactivated all existing predictions")
        print("  Run the prediction scheduler to generate new predictions with real PrizePicks lines")


if __name__ == "__main__":
    asyncio.run(clear_old_predictions())
