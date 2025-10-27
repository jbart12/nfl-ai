"""
Backfill Player Game Stats from ESPN

Fetches historical game-by-game player statistics from ESPN API and stores them in the database.
This is CRITICAL for the AI prediction system - we need historical performance data for RAG search.

Usage:
    # Backfill all players for 2024 season
    python -m scripts.backfill_player_stats --season 2024

    # Backfill specific player
    python -m scripts.backfill_player_stats --season 2024 --player-id "123456"

    # Backfill multiple seasons
    python -m scripts.backfill_player_stats --seasons 2023 2024 2025

    # Backfill only active players
    python -m scripts.backfill_player_stats --season 2024 --active-only
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Optional
import argparse
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import AsyncSessionLocal
from app.models.nfl import Player, PlayerGameStats, Game
from app.services.espn_game_stats import ESPNGameStatsService
import structlog

logger = structlog.get_logger()


class PlayerStatsBackfiller:
    """Backfill player game stats from ESPN"""

    def __init__(self):
        self.espn_service = ESPNGameStatsService()
        self.stats_created = 0
        self.stats_updated = 0
        self.stats_skipped = 0
        self.players_processed = 0
        self.players_failed = 0

    async def backfill_player(
        self,
        session: AsyncSession,
        player: Player,
        season: int
    ) -> bool:
        """
        Backfill game stats for a single player for a season.

        Args:
            session: Database session
            player: Player to backfill
            season: Season year

        Returns:
            True if successful, False otherwise
        """
        try:
            if not player.espn_id:
                logger.warning(
                    "player_missing_espn_id",
                    player_id=player.id,
                    player_name=player.name
                )
                return False

            logger.info(
                "fetching_player_stats",
                player=player.name,
                espn_id=player.espn_id,
                season=season
            )

            # Fetch game log from ESPN
            game_stats = await self.espn_service.get_player_game_log(
                player.espn_id,
                season
            )

            if not game_stats:
                logger.info(
                    "no_stats_found",
                    player=player.name,
                    season=season
                )
                return True  # Not an error, player may not have played

            logger.info(
                "received_game_stats",
                player=player.name,
                games_count=len(game_stats),
                season=season
            )

            # Store each game's stats
            for game_stat in game_stats:
                await self._store_game_stat(session, player, game_stat, season)

            await session.commit()

            logger.info(
                "player_backfill_complete",
                player=player.name,
                games=len(game_stats),
                season=season
            )

            return True

        except Exception as e:
            await session.rollback()
            logger.error(
                "player_backfill_error",
                player=player.name,
                season=season,
                error=str(e)
            )
            return False

    async def _store_game_stat(
        self,
        session: AsyncSession,
        player: Player,
        game_stat_data: dict,
        season: int
    ):
        """Store a single game stat record"""
        try:
            # Generate unique ID
            week = game_stat_data.get("week", 0)
            game_id = game_stat_data.get("game_id", f"{season}_week{week}_{player.id}")
            stat_id = f"{player.id}_{game_id}"

            # Check if stat already exists
            result = await session.execute(
                select(PlayerGameStats).where(PlayerGameStats.id == stat_id)
            )
            existing_stat = result.scalar_one_or_none()

            if existing_stat:
                self.stats_skipped += 1
                logger.debug(
                    "stat_already_exists",
                    player=player.name,
                    week=week,
                    season=season
                )
                return

            # Create new stat record
            stat = PlayerGameStats(
                id=stat_id,
                player_id=player.id,
                game_id=game_id,
                season=season,
                week=week,
                # Passing stats
                passing_completions=game_stat_data.get("passing_completions"),
                passing_attempts=game_stat_data.get("passing_attempts"),
                passing_yards=game_stat_data.get("passing_yards"),
                passing_touchdowns=game_stat_data.get("passing_touchdowns"),
                passing_long=game_stat_data.get("passing_long"),
                interceptions=game_stat_data.get("interceptions"),
                # Rushing stats
                rushing_attempts=game_stat_data.get("rushing_attempts"),
                rushing_yards=game_stat_data.get("rushing_yards"),
                rushing_touchdowns=game_stat_data.get("rushing_touchdowns"),
                rushing_long=game_stat_data.get("rushing_long"),
                # Receiving stats
                receiving_targets=game_stat_data.get("receiving_targets"),
                receiving_receptions=game_stat_data.get("receiving_receptions"),
                receiving_yards=game_stat_data.get("receiving_yards"),
                receiving_touchdowns=game_stat_data.get("receiving_touchdowns"),
                receiving_long=game_stat_data.get("receiving_long"),
                # Fantasy
                fantasy_points=game_stat_data.get("fantasy_points"),
                created_at=datetime.utcnow()
            )

            session.add(stat)
            self.stats_created += 1

            logger.debug(
                "stat_created",
                player=player.name,
                week=week,
                season=season
            )

        except Exception as e:
            logger.error(
                "store_game_stat_error",
                player=player.name,
                error=str(e)
            )
            raise

    async def backfill_all_players(
        self,
        session: AsyncSession,
        season: int,
        active_only: bool = False,
        player_ids: Optional[List[str]] = None
    ):
        """
        Backfill stats for all players (or filtered subset).

        Args:
            session: Database session
            season: Season year
            active_only: Only backfill active players
            player_ids: Specific player IDs to backfill
        """
        try:
            # Build query
            query = select(Player)

            if active_only:
                query = query.where(Player.status == "ACTIVE")

            if player_ids:
                query = query.where(Player.id.in_(player_ids))

            # Only backfill players with ESPN IDs
            query = query.where(Player.espn_id.isnot(None))

            # Execute query
            result = await session.execute(query)
            players = result.scalars().all()

            logger.info(
                "backfilling_players",
                count=len(players),
                season=season,
                active_only=active_only
            )

            print(f"\nBackfilling {len(players)} players for {season} season...")
            print("=" * 60)

            # Process each player
            for i, player in enumerate(players, 1):
                print(f"[{i}/{len(players)}] {player.name} ({player.player_position})...", end=" ")

                success = await self.backfill_player(session, player, season)

                if success:
                    self.players_processed += 1
                    print("✓")
                else:
                    self.players_failed += 1
                    print("✗")

                # Commit every 10 players to avoid long transactions
                if i % 10 == 0:
                    await session.commit()
                    print(f"  → Committed batch ({i} players processed)")

            # Final commit
            await session.commit()

            print("\n" + "=" * 60)
            print("Backfill Summary:")
            print(f"  Players processed: {self.players_processed}")
            print(f"  Players failed: {self.players_failed}")
            print(f"  Stats created: {self.stats_created}")
            print(f"  Stats skipped (already exist): {self.stats_skipped}")
            print("=" * 60)

        except Exception as e:
            await session.rollback()
            logger.error("backfill_all_players_error", error=str(e))
            raise


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Backfill player game stats from ESPN")
    parser.add_argument(
        "--season",
        type=int,
        help="Season year to backfill (e.g., 2024)"
    )
    parser.add_argument(
        "--seasons",
        type=int,
        nargs="+",
        help="Multiple season years to backfill (e.g., 2023 2024 2025)"
    )
    parser.add_argument(
        "--player-id",
        type=str,
        help="Specific player ID to backfill"
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="Only backfill active players"
    )

    args = parser.parse_args()

    # Determine seasons to backfill
    if args.seasons:
        seasons = args.seasons
    elif args.season:
        seasons = [args.season]
    else:
        # Default to current year
        seasons = [datetime.now().year]

    print("NFL Player Stats Backfiller")
    print("=" * 60)
    print(f"Seasons: {', '.join(map(str, seasons))}")
    if args.player_id:
        print(f"Player ID: {args.player_id}")
    if args.active_only:
        print("Mode: Active players only")
    print("=" * 60)

    try:
        async with AsyncSessionLocal() as session:
            for season in seasons:
                print(f"\n{'='*60}")
                print(f"Processing {season} season")
                print(f"{'='*60}")

                backfiller = PlayerStatsBackfiller()

                player_ids = [args.player_id] if args.player_id else None

                await backfiller.backfill_all_players(
                    session=session,
                    season=season,
                    active_only=args.active_only,
                    player_ids=player_ids
                )

        print("\n✓ Backfill completed successfully")

    except Exception as e:
        print(f"\n✗ Backfill failed: {e}")
        logger.error("backfill_failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
