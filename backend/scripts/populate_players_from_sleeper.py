"""
Populate All NFL Players from Sleeper API

Fetches all active NFL players from Sleeper and adds them to our database.
This is the PRIMARY source for player data - always current and free.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.nfl import Player
from app.services.sleeper_stats import get_sleeper_stats_service
import structlog

logger = structlog.get_logger()


async def populate_players():
    """Populate all NFL players from Sleeper API"""
    print("NFL Player Population - Sleeper API")
    print("="*60)

    async with AsyncSessionLocal() as session:
        try:
            sleeper_service = get_sleeper_stats_service()

            print("Fetching all NFL players from Sleeper...")
            all_players = await sleeper_service.get_all_players()

            print(f"Found {len(all_players)} total players from Sleeper")
            print()

            # Filter for active NFL players only
            nfl_players = []
            for sleeper_id, player_data in all_players.items():
                # Skip non-NFL players
                if player_data.get("sport") != "nfl":
                    continue

                # Skip inactive players
                if player_data.get("active") is False:
                    continue

                # Skip players without a position
                position = player_data.get("position")
                if not position or position in ["DEF", "K", "P"]:  # Skip defense and special teams for now
                    continue

                nfl_players.append((sleeper_id, player_data))

            print(f"Filtered to {len(nfl_players)} active NFL position players")
            print()

            added = 0
            updated = 0
            skipped = 0

            for sleeper_id, player_data in nfl_players:
                first_name = player_data.get("first_name", "")
                last_name = player_data.get("last_name", "")
                full_name = f"{first_name} {last_name}".strip()

                if not full_name:
                    skipped += 1
                    continue

                position = player_data.get("position")
                team = player_data.get("team")  # Can be None for free agents

                # Create player ID (use Sleeper ID as base, but make it readable)
                player_id = f"{last_name.lower().replace(' ', '_')}_{first_name.lower()[:1]}_{sleeper_id}"[:50]

                # Check if player exists by Sleeper ID
                result = await session.execute(
                    select(Player).where(Player.sleeper_id == sleeper_id)
                )
                existing_player = result.scalar_one_or_none()

                if existing_player:
                    # Update existing player
                    existing_player.name = full_name
                    existing_player.player_position = position
                    existing_player.team_id = team
                    existing_player.status = "ACTIVE"
                    updated += 1
                else:
                    # Create new player
                    new_player = Player(
                        id=player_id,
                        name=full_name,
                        player_position=position,
                        team_id=team,
                        sleeper_id=sleeper_id,
                        status="ACTIVE"
                    )
                    session.add(new_player)
                    added += 1

                # Commit in batches of 100
                if (added + updated) % 100 == 0:
                    await session.commit()
                    print(f"  Progress: {added + updated}/{len(nfl_players)} players processed...")

            # Final commit
            await session.commit()

            print()
            print("="*60)
            print(f"✓ Player population complete")
            print(f"  Players added: {added}")
            print(f"  Players updated: {updated}")
            print(f"  Players skipped: {skipped}")
            print("="*60)

            logger.info(
                "players_populated",
                added=added,
                updated=updated,
                skipped=skipped
            )

        except Exception as e:
            logger.error("populate_players_error", error=str(e))
            print(f"\n✗ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(populate_players())
