"""
RAG Narrative Generator Service

Generates rich narrative descriptions of game performances for embedding and RAG search.
Ties together game data, player stats, and contextual information into searchable narratives.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models.nfl import PlayerGameStats, Game, Player
from app.services.embeddings import get_embedding_service
from app.services.vector_store import get_vector_store_service

logger = structlog.get_logger()


class RAGNarrativeService:
    """Service for generating and managing game performance narratives"""

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store_service()

    async def generate_game_narrative(
        self,
        player_game_stat: PlayerGameStats,
        game: Game,
        player: Player,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a rich narrative description of a game performance.

        Args:
            player_game_stat: Player's game statistics
            game: Game information
            player: Player information
            additional_context: Additional context (weather, injuries, etc.)

        Returns:
            Narrative string describing the performance
        """
        try:
            # Extract key stats based on player position
            position = player.player_position
            stat_summary = self._format_stat_summary(player_game_stat, position)

            # Game context
            game_context = self._format_game_context(game, additional_context)

            # Build narrative
            narrative = f"""
Player: {player.name}
Position: {position}
Game: Week {game.week}, {game.season} vs {game.opponent_team_id}
Date: {game.game_date}
Location: {'Home' if game.home_team_id == player.team_id else 'Away'}

PERFORMANCE:
{stat_summary}

GAME CONTEXT:
{game_context}

ANALYSIS:
{self._generate_analysis(player_game_stat, game, position)}
""".strip()

            logger.debug(
                "narrative_generated",
                player=player.name,
                week=game.week,
                length=len(narrative)
            )

            return narrative

        except Exception as e:
            logger.error(
                "narrative_generation_error",
                error=str(e),
                player_id=player.id
            )
            raise

    def _format_stat_summary(self, stats: PlayerGameStats, position: str) -> str:
        """Format stat summary based on position"""
        lines = []

        # Common stats
        if stats.snap_count:
            lines.append(f"Snaps: {stats.snap_count} ({stats.snap_percentage:.1f}%)")

        # Position-specific stats
        if position in ["WR", "TE"]:
            if stats.receiving_targets is not None:
                catch_rate = (stats.receiving_receptions / stats.receiving_targets * 100) if stats.receiving_targets > 0 else 0
                lines.append(f"Receiving: {stats.receiving_receptions}/{stats.receiving_targets} targets, {stats.receiving_yards} yards, {stats.receiving_touchdowns} TDs")
                lines.append(f"Catch Rate: {catch_rate:.1f}%")
                if stats.receiving_long:
                    lines.append(f"Longest Reception: {stats.receiving_long} yards")

        elif position in ["RB"]:
            if stats.rushing_attempts is not None:
                lines.append(f"Rushing: {stats.rushing_attempts} carries, {stats.rushing_yards} yards, {stats.rushing_touchdowns} TDs")
                if stats.rushing_attempts > 0:
                    avg = stats.rushing_yards / stats.rushing_attempts
                    lines.append(f"Average: {avg:.1f} yards per carry")
                if stats.rushing_long:
                    lines.append(f"Longest Rush: {stats.rushing_long} yards")

            # RBs also catch passes
            if stats.receiving_targets and stats.receiving_targets > 0:
                lines.append(f"Receiving: {stats.receiving_receptions}/{stats.receiving_targets} targets, {stats.receiving_yards} yards")

        elif position == "QB":
            if stats.passing_attempts is not None:
                comp_pct = (stats.passing_completions / stats.passing_attempts * 100) if stats.passing_attempts > 0 else 0
                lines.append(f"Passing: {stats.passing_completions}/{stats.passing_attempts} ({comp_pct:.1f}%), {stats.passing_yards} yards")
                lines.append(f"TDs: {stats.passing_touchdowns}, INTs: {stats.interceptions}")
                if stats.passing_long:
                    lines.append(f"Longest Pass: {stats.passing_long} yards")

            # QBs sometimes rush
            if stats.rushing_attempts and stats.rushing_attempts > 0:
                lines.append(f"Rushing: {stats.rushing_attempts} carries, {stats.rushing_yards} yards, {stats.rushing_touchdowns} TDs")

        # Fantasy points if available
        if stats.fantasy_points:
            lines.append(f"Fantasy Points: {stats.fantasy_points:.1f}")

        return "\n".join(lines) if lines else "No detailed stats available"

    def _format_game_context(self, game: Game, additional_context: Optional[Dict[str, Any]] = None) -> str:
        """Format game context information"""
        lines = []

        # Score and outcome
        if game.home_score is not None and game.away_score is not None:
            lines.append(f"Final Score: {game.home_team_id} {game.home_score} - {game.away_team_id} {game.away_score}")

        # Weather
        if game.weather_description:
            weather = f"Weather: {game.weather_description}"
            if game.temperature:
                weather += f", {game.temperature}°F"
            if game.wind_speed:
                weather += f", {game.wind_speed}mph wind"
            lines.append(weather)
        elif game.is_dome:
            lines.append("Weather: Indoor (Dome)")

        # Vegas lines
        if game.vegas_line:
            lines.append(f"Spread: {game.vegas_line}")
        if game.over_under:
            lines.append(f"Over/Under: {game.over_under}")

        # Additional context from caller
        if additional_context:
            for key, value in additional_context.items():
                formatted_key = key.replace("_", " ").title()
                lines.append(f"{formatted_key}: {value}")

        return "\n".join(lines) if lines else "No game context available"

    def _generate_analysis(self, stats: PlayerGameStats, game: Game, position: str) -> str:
        """Generate analytical notes about the performance"""
        notes = []

        # Snap percentage analysis
        if stats.snap_percentage is not None:
            if stats.snap_percentage > 80:
                notes.append("High snap count indicates featured role in game plan.")
            elif stats.snap_percentage < 50:
                notes.append("Limited snap count may indicate injury, matchup, or game script.")

        # Game script analysis
        if game.home_score is not None and game.away_score is not None:
            score_diff = abs(game.home_score - game.away_score)
            if score_diff > 14:
                notes.append(f"Blowout game (margin: {score_diff} points) likely affected usage patterns.")
            elif score_diff <= 7:
                notes.append("Close game likely maintained normal usage throughout.")

        # Weather impact
        if game.wind_speed and game.wind_speed > 15:
            notes.append(f"High wind ({game.wind_speed}mph) may have limited deep passing game.")
        if game.temperature and game.temperature < 32:
            notes.append(f"Cold weather ({game.temperature}°F) may have affected ball handling.")

        # Position-specific notes
        if position in ["WR", "TE"] and stats.receiving_targets is not None:
            if stats.receiving_targets > 10:
                notes.append("High target volume indicates strong QB trust and opportunity.")
            elif stats.receiving_targets < 5:
                notes.append("Low target volume may indicate coverage focus or game script.")

        if position == "RB" and stats.rushing_attempts is not None:
            if stats.rushing_attempts > 20:
                notes.append("Heavy workload suggests featured back role.")
            elif stats.rushing_attempts < 10:
                notes.append("Limited carries may indicate committee approach or trailing game script.")

        return "\n".join(notes) if notes else "Standard performance within normal parameters."

    async def process_and_store_game(
        self,
        db: AsyncSession,
        player_game_stat: PlayerGameStats,
        stat_type: str
    ) -> Optional[str]:
        """
        Process a game performance and store it in the vector database.

        Args:
            db: Database session
            player_game_stat: Player's game statistics
            stat_type: Type of stat to track (receiving_yards, rushing_yards, etc.)

        Returns:
            Point ID if stored successfully, None otherwise
        """
        try:
            # Get related data
            game = await db.get(Game, player_game_stat.game_id)
            player = await db.get(Player, player_game_stat.player_id)

            if not game or not player:
                logger.warning(
                    "missing_related_data",
                    player_id=player_game_stat.player_id,
                    game_id=player_game_stat.game_id
                )
                return None

            # Generate narrative
            narrative = await self.generate_game_narrative(
                player_game_stat=player_game_stat,
                game=game,
                player=player
            )

            # Generate embedding
            embedding = await self.embedding_service.embed_text(narrative)

            # Get stat value based on stat_type
            stat_value = self._extract_stat_value(player_game_stat, stat_type)
            if stat_value is None:
                logger.warning(
                    "stat_value_not_found",
                    stat_type=stat_type,
                    player_id=player.id
                )
                return None

            # Store in vector database
            point_id = await self.vector_store.store_game_performance(
                player_id=player.id,
                player_name=player.name,
                stat_type=stat_type,
                stat_value=stat_value,
                game_date=game.game_date.isoformat() if game.game_date else "unknown",
                week=game.week,
                season=game.season,
                opponent=game.opponent_team_id or "unknown",
                narrative=narrative,
                embedding=embedding,
                metadata={
                    "position": player.player_position,
                    "team": player.team_id,
                    "snap_percentage": player_game_stat.snap_percentage,
                    "fantasy_points": player_game_stat.fantasy_points
                }
            )

            logger.info(
                "game_processed_and_stored",
                point_id=point_id,
                player=player.name,
                stat_type=stat_type,
                stat_value=stat_value
            )

            return point_id

        except Exception as e:
            logger.error(
                "process_and_store_error",
                error=str(e),
                player_id=player_game_stat.player_id
            )
            return None

    def _extract_stat_value(self, stats: PlayerGameStats, stat_type: str) -> Optional[float]:
        """Extract the specific stat value based on stat_type"""
        stat_mapping = {
            "receiving_yards": stats.receiving_yards,
            "receiving_receptions": stats.receiving_receptions,
            "receiving_touchdowns": stats.receiving_touchdowns,
            "rushing_yards": stats.rushing_yards,
            "rushing_attempts": stats.rushing_attempts,
            "rushing_touchdowns": stats.rushing_touchdowns,
            "passing_yards": stats.passing_yards,
            "passing_touchdowns": stats.passing_touchdowns,
            "passing_completions": stats.passing_completions,
            "interceptions": stats.interceptions,
            "fantasy_points": stats.fantasy_points,
        }

        return stat_mapping.get(stat_type)

    async def find_similar_performances(
        self,
        db: AsyncSession,
        player_id: str,
        stat_type: str,
        context_description: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find similar historical performances using RAG search.

        Args:
            db: Database session
            player_id: Player ID to search for
            stat_type: Type of stat
            context_description: Description of the situation we're looking for
            limit: Maximum number of results

        Returns:
            List of similar performances
        """
        try:
            # Get player info
            player = await db.get(Player, player_id)
            if not player:
                logger.warning("player_not_found", player_id=player_id)
                return []

            # Build search query
            query_text = f"""
Looking for: {player.name} {stat_type.replace('_', ' ')} performances
Similar to: {context_description}
"""

            # Generate query embedding
            query_embedding = await self.embedding_service.embed_text(query_text)

            # Search vector store
            similar_performances = await self.vector_store.search_similar_performances(
                query_embedding=query_embedding,
                player_id=player_id,
                stat_type=stat_type,
                limit=limit,
                score_threshold=0.7
            )

            logger.info(
                "similar_performances_found",
                player=player.name,
                stat_type=stat_type,
                count=len(similar_performances)
            )

            return similar_performances

        except Exception as e:
            logger.error(
                "find_similar_performances_error",
                error=str(e),
                player_id=player_id
            )
            return []


# Singleton instance
_rag_service = None


def get_rag_service() -> RAGNarrativeService:
    """Get or create RAG service singleton"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGNarrativeService()
    return _rag_service
