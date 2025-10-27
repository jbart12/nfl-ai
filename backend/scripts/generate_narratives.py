"""
Generate Narratives and Embeddings for RAG

Creates game narratives and stores embeddings in Qdrant for similar situation retrieval.
This enables the RAG (Retrieval-Augmented Generation) system.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.nfl import Player, PlayerGameStats, Game
from app.services.rag_narrative import get_rag_service
from app.services.embeddings import get_embedding_service
from app.services.vector_store import get_vector_store_service
import structlog

logger = structlog.get_logger()


async def generate_narratives_for_stats():
    """Generate narratives and embeddings for all game stats"""
    print("Game Narrative & Embedding Generator")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            # Get all player game stats
            result = await session.execute(
                select(PlayerGameStats).order_by(PlayerGameStats.season, PlayerGameStats.week)
            )
            stats = result.scalars().all()

            if not stats:
                print("\n✗ No game stats found. Run seed_test_stats.py first.")
                return

            print(f"Found {len(stats)} game stats to process")
            print()

            # Initialize services
            narrative_service = get_rag_service()
            embedding_service = get_embedding_service()
            vector_store = get_vector_store_service()

            # Collection is automatically created in VectorStoreService.__init__
            logger.info("qdrant_collection_ready")

            narratives_created = 0
            embeddings_stored = 0

            for i, stat in enumerate(stats, 1):
                # Get player info
                player = await session.get(Player, stat.player_id)
                if not player:
                    logger.warning("player_not_found", stat_id=stat.id)
                    continue

                # Get game info
                game = await session.get(Game, stat.game_id)
                if not game:
                    logger.warning("game_not_found", stat_id=stat.id)
                    continue

                print(f"[{i}/{len(stats)}] {player.name} - Week {stat.week} vs {game.opponent_team_id}...", end=" ")

                try:
                    # Generate narrative
                    narrative = await narrative_service.generate_game_narrative(
                        player_game_stat=stat,
                        game=game,
                        player=player
                    )

                    if not narrative:
                        print("✗ (no narrative)")
                        continue

                    narratives_created += 1
                    logger.info("narrative_generated", player=player.name, week=stat.week)

                    # Generate embedding
                    embedding = await embedding_service.embed_text(narrative)

                    # Determine stat type and value
                    if stat.passing_yards:
                        stat_type = "passing_yards"
                        stat_value = stat.passing_yards
                    else:
                        stat_type = "receiving_yards"
                        stat_value = stat.receiving_yards or 0

                    # Store in Qdrant
                    await vector_store.store_game_performance(
                        player_id=player.id,
                        player_name=player.name,
                        stat_type=stat_type,
                        stat_value=stat_value,
                        game_date=game.game_date.isoformat(),
                        week=stat.week,
                        season=stat.season,
                        opponent=game.opponent_team_id,
                        narrative=narrative,
                        embedding=embedding,
                        metadata={
                            "passing_yards": stat.passing_yards,
                            "passing_tds": stat.passing_touchdowns,
                            "receiving_yards": stat.receiving_yards,
                            "receiving_tds": stat.receiving_touchdowns,
                            "game_id": game.id
                        }
                    )

                    embeddings_stored += 1
                    print("✓")

                except Exception as e:
                    print(f"✗ ({str(e)[:50]})")
                    logger.error("narrative_generation_error", error=str(e), stat_id=stat.id)
                    continue

            print()
            print("=" * 60)
            print(f"✓ Narratives generated: {narratives_created}")
            print(f"✓ Embeddings stored: {embeddings_stored}")
            print()
            print("RAG system is now ready!")
            print("Try making a prediction to see similar situations in action.")

        except Exception as e:
            logger.error("generation_failed", error=str(e))
            print(f"\n✗ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(generate_narratives_for_stats())
