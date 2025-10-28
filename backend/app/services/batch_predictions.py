"""
Batch Prediction Service

Generates predictions for multiple players/props at once.
Used by the scheduler to populate the opportunities feed.
"""
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import uuid
import json

from app.models.nfl import Player, Game, Prediction
from app.services.claude_prediction import get_claude_service
from app.services.rag_narrative import get_rag_service

logger = structlog.get_logger()


# Define common prop lines for each position and stat type
NOTABLE_PROPS = {
    "QB": {
        "passing_yards": [225.5, 250.5, 275.5],
        "passing_touchdowns": [1.5, 2.5],
        "interceptions": [0.5, 1.5],
    },
    "RB": {
        "rushing_yards": [50.5, 75.5, 100.5],
        "rushing_touchdowns": [0.5],
        "receptions": [2.5, 3.5, 4.5],
    },
    "WR": {
        "receiving_yards": [50.5, 75.5, 100.5],
        "receptions": [3.5, 4.5, 5.5, 6.5],
        "receiving_touchdowns": [0.5],
    },
    "TE": {
        "receiving_yards": [35.5, 50.5, 65.5],
        "receptions": [2.5, 3.5, 4.5],
        "receiving_touchdowns": [0.5],
    }
}


class BatchPredictionService:
    """Service for generating predictions in batch"""

    def __init__(self):
        self.claude_service = get_claude_service()
        self.rag_service = get_rag_service()

    async def generate_weekly_predictions(
        self,
        db: AsyncSession,
        week: int,
        season: int = 2025,
        max_players: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate predictions for all notable props in the given week.

        Args:
            db: Database session
            week: Week number
            season: Season year
            max_players: Limit number of players (for testing)

        Returns:
            Summary of predictions generated
        """
        logger.info("batch_predictions_start", week=week, season=season)

        # Get games for this week
        games_query = select(Game).where(
            and_(
                Game.week == week,
                Game.season == season,
                Game.is_completed == False
            )
        )
        result = await db.execute(games_query)
        games = result.scalars().all()

        if not games:
            logger.warning("no_games_found", week=week, season=season)
            return {"predictions_generated": 0, "games_found": 0}

        logger.info("games_found", count=len(games), week=week)

        # Get all players from these games
        team_ids = set()
        for game in games:
            team_ids.add(game.home_team_id)
            team_ids.add(game.away_team_id)

        # Get notable players (those with recent stats)
        players_query = select(Player).where(
            and_(
                Player.team_id.in_(team_ids),
                Player.player_position.in_(["QB", "RB", "WR", "TE"]),
                Player.status == "ACTIVE"
            )
        )

        if max_players:
            players_query = players_query.limit(max_players)

        result = await db.execute(players_query)
        players = result.scalars().all()

        logger.info("players_found", count=len(players))

        # Generate predictions for each player/prop combination
        predictions_generated = 0
        predictions_failed = 0

        for player in players:
            position = player.player_position
            if position not in NOTABLE_PROPS:
                continue

            # Find this player's game
            player_game = None
            opponent = None
            for game in games:
                if game.home_team_id == player.team_id:
                    player_game = game
                    opponent = game.away_team_id
                    break
                elif game.away_team_id == player.team_id:
                    player_game = game
                    opponent = game.home_team_id
                    break

            if not player_game:
                continue

            # Generate predictions for each notable prop for this position
            for stat_type, lines in NOTABLE_PROPS[position].items():
                for line_score in lines:
                    try:
                        # Check if prediction already exists
                        existing_query = select(Prediction).where(
                            and_(
                                Prediction.player_id == str(player.id),
                                Prediction.stat_type == stat_type,
                                Prediction.line_score == line_score,
                                Prediction.week == week,
                                Prediction.is_active == True
                            )
                        )
                        result = await db.execute(existing_query)
                        existing = result.scalar_one_or_none()

                        if existing:
                            logger.debug(
                                "prediction_exists_skipping",
                                player=player.name,
                                stat_type=stat_type,
                                line=line_score
                            )
                            continue

                        # Generate prediction
                        prediction_result = await self._generate_single_prediction(
                            db=db,
                            player=player,
                            stat_type=stat_type,
                            line_score=line_score,
                            opponent=opponent,
                            week=week,
                            game_time=player_game.game_time
                        )

                        if prediction_result:
                            predictions_generated += 1
                            logger.info(
                                "prediction_generated",
                                player=player.name,
                                stat_type=stat_type,
                                line=line_score,
                                prediction=prediction_result.get("prediction"),
                                confidence=prediction_result.get("confidence")
                            )
                        else:
                            predictions_failed += 1

                        # Rate limiting - don't overwhelm the APIs
                        await asyncio.sleep(0.5)

                    except Exception as e:
                        predictions_failed += 1
                        logger.error(
                            "prediction_generation_error",
                            player=player.name,
                            stat_type=stat_type,
                            error=str(e)
                        )

        logger.info(
            "batch_predictions_complete",
            week=week,
            generated=predictions_generated,
            failed=predictions_failed
        )

        return {
            "predictions_generated": predictions_generated,
            "predictions_failed": predictions_failed,
            "games_found": len(games),
            "players_processed": len(players)
        }

    async def _generate_single_prediction(
        self,
        db: AsyncSession,
        player: Player,
        stat_type: str,
        line_score: float,
        opponent: str,
        week: int,
        game_time: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate a single prediction and save it to the database"""
        try:
            # Import here to avoid circular dependencies
            from app.api.endpoints.predictions import (
                _get_current_season_stats,
                _get_matchup_context,
                _get_injury_context,
                _build_context_description
            )

            # Gather context data
            current_stats = await _get_current_season_stats(db, player.id, stat_type)
            matchup_context = await _get_matchup_context(db, player, opponent)
            matchup_context["week"] = week
            matchup_context["game_time"] = game_time
            injury_context = await _get_injury_context(db, player.id)

            # RAG: Find similar situations
            similar_situations = []
            try:
                context_description = _build_context_description(
                    current_stats=current_stats,
                    matchup_context=matchup_context,
                    injury_context=injury_context
                )

                similar_situations = await self.rag_service.find_similar_performances(
                    db=db,
                    player_id=player.id,
                    stat_type=stat_type,
                    context_description=context_description,
                    limit=10
                )
            except Exception as e:
                logger.warning("rag_unavailable", player=player.name, error=str(e))

            # Build prop context
            prop_context = {
                "player": player.name,
                "stat_type": stat_type,
                "line": line_score,
                "opponent": opponent or "Unknown",
                "week": week
            }

            # Get Claude prediction
            prediction_result = await self.claude_service.predict_prop(
                prop=prop_context,
                current_stats=current_stats,
                matchup_context=matchup_context,
                injury_context=injury_context,
                similar_situations=similar_situations
            )

            # Calculate edge
            edge = prediction_result["projected_value"] - line_score

            # Save to database
            prediction_id = str(uuid.uuid4())
            db_prediction = Prediction(
                id=prediction_id,
                prop_id=None,
                player_id=str(player.id),
                player_name=player.name,
                player_position=player.player_position,
                team=player.team_id,
                opponent=opponent,
                week=week,
                season=2025,
                game_time=game_time,
                stat_type=stat_type,
                line_score=line_score,
                prediction=prediction_result["prediction"],
                confidence=prediction_result["confidence"],
                projected_value=prediction_result["projected_value"],
                edge=edge,
                reasoning=prediction_result["reasoning"],
                key_factors=json.dumps(prediction_result.get("key_factors", [])),
                risk_factors=json.dumps(prediction_result.get("risk_factors", [])),
                comparable_game=prediction_result.get("comparable_game"),
                model_version=prediction_result["model"],
                similar_situations_count=len(similar_situations),
                is_active=True,
                is_archived=False
            )

            db.add(db_prediction)
            await db.commit()

            return {
                "prediction": prediction_result["prediction"],
                "confidence": prediction_result["confidence"],
                "edge": edge
            }

        except Exception as e:
            logger.error("single_prediction_error", player=player.name, error=str(e))
            await db.rollback()
            return None


# Global instance
_batch_prediction_service = None


def get_batch_prediction_service() -> BatchPredictionService:
    """Get the global batch prediction service instance"""
    global _batch_prediction_service
    if _batch_prediction_service is None:
        _batch_prediction_service = BatchPredictionService()
    return _batch_prediction_service
