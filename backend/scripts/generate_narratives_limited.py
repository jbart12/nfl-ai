"""
Generate Narratives and Embeddings for RAG - Limited/Batched Version

Processes game stats in batches to avoid API rate limits and costs.
Focus on 2025 season data first (most relevant for current predictions).
"""
import asyncio
import sys
from pathlib import Path
import argparse

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import AsyncSessionLocal
from app.models.nfl import Player, PlayerGameStats, Game
from app.services.rag_narrative import get_rag_service
from app.services.embeddings import get_embedding_service
from app.services.vector_store import get_vector_store_service
import structlog

logger = structlog.get_logger()


async def generate_narratives_for_stats(
    season: int = 2025,
    limit: int = None,
    positions: list = None
):
    """
    Generate narratives and embeddings for game stats.

    Args:
        season: Season to process (default: 2025)
        limit: Maximum number of stats to process (default: None = all)
        positions: List of positions to filter (e.g., ['QB', 'WR', 'RB'])
    """
    print("="*80)
    print("GAME NARRATIVE & EMBEDDING GENERATOR")
    print("="*80)
    print(f"Season: {season}")
    print(f"Limit: {limit if limit else 'All'}")
    print(f"Positions: {positions if positions else 'All'}")
    print("="*80)
    print()

    async with AsyncSessionLocal() as session:
        try:
            # Build query
            query = select(PlayerGameStats).join(Player).where(
                PlayerGameStats.season == season
            )

            if positions:
                query = query.where(Player.player_position.in_(positions))

            query = query.order_by(PlayerGameStats.week)

            if limit:
                query = query.limit(limit)

            result = await session.execute(query)
            stats = result.scalars().all()

            if not stats:
                print("✗ No game stats found matching criteria")
                return

            print(f"✓ Found {len(stats)} game stats to process")
            print()

            # Initialize services
            print("Initializing AI services...")
            narrative_service = get_rag_service()
            embedding_service = get_embedding_service()
            vector_store = get_vector_store_service()
            print("✓ Services initialized")
            print()

            # Process stats
            processed = 0
            skipped = 0
            errors = 0

            for i, stat in enumerate(stats, 1):
                try:
                    # Get player
                    player_result = await session.execute(
                        select(Player).where(Player.id == stat.player_id)
                    )
                    player = player_result.scalar_one_or_none()

                    if not player:
                        print(f"  [{i}/{len(stats)}] Skipped - player not found: {stat.player_id}")
                        skipped += 1
                        continue

                    print(f"  [{i}/{len(stats)}] Processing: {player.name} Week {stat.week}")

                    # Get game (optional - Sleeper doesn't always have it)
                    game = None  # We don't have game data for most stats

                    # Determine stat type and value based on position
                    stat_type, stat_value = _get_primary_stat(player, stat)

                    if not stat_value or stat_value == 0:
                        print(f"    ↳ Skipped - no {stat_type} data")
                        skipped += 1
                        continue

                    # Generate simplified narrative (we don't have game data from Sleeper)
                    narrative = _generate_simple_narrative(player, stat, stat_type, stat_value)

                    print(f"    ↳ Narrative: {narrative[:80]}...")

                    # Create embedding
                    embedding = await embedding_service.embed_text(narrative)

                    # Store in Qdrant
                    await vector_store.store_game_performance(
                        player_id=player.id,
                        player_name=player.name,
                        stat_type=stat_type,
                        stat_value=stat_value,
                        season=stat.season,
                        week=stat.week,
                        game_date=None,  # Sleeper doesn't provide game dates
                        opponent="Unknown",  # We don't have opponent data from Sleeper
                        narrative=narrative,
                        embedding=embedding,
                        metadata={
                            "position": player.player_position,
                            "team": player.team_id,
                        }
                    )

                    print(f"    ↳ ✓ Stored in Qdrant")
                    processed += 1

                    # Small delay to avoid rate limits
                    if i % 10 == 0:
                        print(f"\n  Progress: {processed} processed, {skipped} skipped, {errors} errors")
                        print(f"  Pausing briefly to avoid rate limits...\n")
                        await asyncio.sleep(2)

                except Exception as e:
                    logger.error("narrative_generation_error", error=str(e), player_id=stat.player_id)
                    print(f"    ↳ ✗ Error: {str(e)}")
                    errors += 1

            print()
            print("="*80)
            print("SUMMARY")
            print("="*80)
            print(f"✓ Processed: {processed}")
            print(f"  Skipped: {skipped}")
            print(f"  Errors: {errors}")
            print(f"  Total: {len(stats)}")
            print("="*80)

            logger.info(
                "narrative_generation_complete",
                processed=processed,
                skipped=skipped,
                errors=errors,
                total=len(stats)
            )

        except Exception as e:
            logger.error("generation_failed", error=str(e))
            print(f"\n✗ Error: {e}")
            raise


def _get_primary_stat(player: Player, stat: PlayerGameStats):
    """Determine primary stat for player based on position"""
    if player.player_position == "QB":
        return "passing_yards", stat.passing_yards
    elif player.player_position == "RB":
        return "rushing_yards", stat.rushing_yards
    elif player.player_position in ["WR", "TE"]:
        return "receiving_yards", stat.receiving_yards
    else:
        # Default to fantasy points
        return "fantasy_points", stat.fantasy_points


def _generate_simple_narrative(player: Player, stat: PlayerGameStats, stat_type: str, stat_value: float) -> str:
    """Generate a simplified narrative without game data"""
    position = player.player_position
    team = player.team_id or "Unknown Team"

    # Position-specific narratives
    if position == "QB":
        narrative = f"{player.name} ({team} QB) completed {stat.passing_completions or 0}/{stat.passing_attempts or 0} passes for {stat.passing_yards or 0} yards"
        if stat.passing_touchdowns:
            narrative += f" and {stat.passing_touchdowns} TD{'s' if stat.passing_touchdowns > 1 else ''}"
        if stat.interceptions:
            narrative += f" with {stat.interceptions} interception{'s' if stat.interceptions > 1 else ''}"
        if stat.rushing_yards and stat.rushing_yards > 15:
            narrative += f". Added {stat.rushing_yards} rushing yards"
        narrative += f" in Week {stat.week} of the {stat.season} season."

    elif position == "RB":
        narrative = f"{player.name} ({team} RB) carried {stat.rushing_attempts or 0} times for {stat.rushing_yards or 0} yards"
        if stat.rushing_touchdowns:
            narrative += f" and {stat.rushing_touchdowns} TD{'s' if stat.rushing_touchdowns > 1 else ''}"
        if stat.receiving_yards and stat.receiving_yards > 20:
            narrative += f". Caught {stat.receiving_receptions}/{stat.receiving_targets} targets for {stat.receiving_yards} receiving yards"
            if stat.receiving_touchdowns:
                narrative += f" and {stat.receiving_touchdowns} receiving TD{'s' if stat.receiving_touchdowns > 1 else ''}"
        narrative += f" in Week {stat.week} of the {stat.season} season."

    elif position in ["WR", "TE"]:
        narrative = f"{player.name} ({team} {position}) caught {stat.receiving_receptions or 0}/{stat.receiving_targets or 0} targets for {stat.receiving_yards or 0} yards"
        if stat.receiving_touchdowns:
            narrative += f" and {stat.receiving_touchdowns} TD{'s' if stat.receiving_touchdowns > 1 else ''}"
        if stat.receiving_long:
            narrative += f" with a long of {stat.receiving_long} yards"
        if stat.rushing_yards and stat.rushing_yards > 10:
            narrative += f". Also rushed for {stat.rushing_yards} yards"
        narrative += f" in Week {stat.week} of the {stat.season} season."
    else:
        narrative = f"{player.name} ({team} {position}) scored {stat.fantasy_points or 0} fantasy points in Week {stat.week} of the {stat.season} season."

    # Add snap percentage if available
    if stat.snap_percentage and stat.snap_percentage > 0:
        narrative += f" Played {stat.snap_percentage:.0f}% of snaps."

    return narrative


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate narratives and embeddings for RAG")
    parser.add_argument("--season", type=int, default=2025, help="Season to process (default: 2025)")
    parser.add_argument("--limit", type=int, help="Max number of stats to process")
    parser.add_argument("--positions", nargs="+", help="Positions to include (e.g., QB WR RB)")

    args = parser.parse_args()

    asyncio.run(generate_narratives_for_stats(
        season=args.season,
        limit=args.limit,
        positions=args.positions
    ))
