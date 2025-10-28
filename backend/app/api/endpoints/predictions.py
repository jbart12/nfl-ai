"""
Prediction Endpoints

New AI-powered prediction system using Claude + RAG.
Orchestrates the full prediction flow: data gathering → RAG search → Claude analysis.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from typing import Dict, Any, Optional, List
from datetime import datetime, date
import structlog
import uuid
import json

from app.core.database import get_db
from app.models.nfl import (
    PrizePicksProjection,
    Player,
    Game,
    PlayerGameStats,
    TeamDefensiveStats,
    Prediction
)
from app.services.claude_prediction import get_claude_service
from app.services.rag_narrative import get_rag_service
from app.services.sleeper_stats import get_sleeper_stats_service
from app.services.batch_predictions import get_batch_prediction_service
from pydantic import BaseModel

logger = structlog.get_logger()

router = APIRouter()


# Request/Response Models
class PredictionRequest(BaseModel):
    """Request to predict a specific prop"""
    prop_id: Optional[str] = None
    player_name: Optional[str] = None
    stat_type: Optional[str] = None
    line_score: Optional[float] = None
    opponent: Optional[str] = None


class CurrentStats(BaseModel):
    """Current season statistics"""
    games_played: int
    avg_per_game: float
    last_3_games: List[float]
    min: float
    max: float
    std_dev: float


class SimilarSituation(BaseModel):
    """Similar historical situation"""
    similarity_score: float
    player_name: str
    game_info: str
    result: str
    narrative: str


class PredictionResponse(BaseModel):
    """Response with AI prediction"""
    prop_id: Optional[str]
    player_name: str
    player_id: str
    position: str
    team: str
    opponent: str
    week: int
    stat_type: str
    line_score: float
    prediction: str  # "OVER" or "UNDER"
    confidence: int  # 0-100
    projected_value: float
    reasoning: str
    key_factors: List[str]
    risk_factors: List[str]
    comparable_game: Optional[str]
    current_stats: CurrentStats
    similar_situations: List[SimilarSituation]
    similar_situations_count: int
    model: str
    generated_at: datetime


@router.post("/predict", response_model=PredictionResponse)
async def predict_prop(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI prediction for a prop using Claude + RAG.

    This endpoint orchestrates the full prediction flow:
    1. Gather structured data from PostgreSQL
    2. Use RAG to find similar historical situations
    3. Send comprehensive context to Claude
    4. Return prediction with reasoning
    """
    try:
        # Get prop details
        prop_data = await _get_prop_data(db, request)
        if not prop_data:
            raise HTTPException(status_code=404, detail="Prop or player not found")

        player = prop_data["player"]
        stat_type = prop_data["stat_type"]
        line_score = prop_data["line_score"]
        opponent = prop_data.get("opponent")

        # CRITICAL: Validate opponent against schedule
        validated_opponent_data = await _validate_and_get_opponent(db, player, opponent)
        if "error" in validated_opponent_data:
            raise HTTPException(status_code=400, detail=validated_opponent_data["error"])

        opponent = validated_opponent_data["opponent"]
        current_week = validated_opponent_data["week"]

        logger.info(
            "prediction_request",
            player=player.name,
            stat_type=stat_type,
            line=line_score
        )

        # Gather all context data
        current_stats = await _get_current_season_stats(db, player.id, stat_type)
        matchup_context = await _get_matchup_context(db, player, opponent)
        injury_context = await _get_injury_context(db, player.id)

        # RAG: Find similar historical situations (optional - gracefully degrades if embeddings unavailable)
        similar_situations = []
        try:
            rag_service = get_rag_service()
            context_description = _build_context_description(
                current_stats=current_stats,
                matchup_context=matchup_context,
                injury_context=injury_context
            )

            similar_situations = await rag_service.find_similar_performances(
                db=db,
                player_id=player.id,
                stat_type=stat_type,
                context_description=context_description,
                limit=10
            )

            logger.info(
                "similar_situations_found",
                player=player.name,
                count=len(similar_situations)
            )
        except Exception as e:
            logger.warning(
                "rag_unavailable_continuing_without",
                player=player.name,
                error=str(e)
            )

        # Build prop context for Claude
        prop_context = {
            "player": player.name,
            "stat_type": stat_type,
            "line": line_score,
            "opponent": opponent or "Unknown",
            "week": matchup_context.get("week", "N/A")
        }

        # Get Claude prediction
        claude_service = get_claude_service()
        prediction_result = await claude_service.predict_prop(
            prop=prop_context,
            current_stats=current_stats,
            matchup_context=matchup_context,
            injury_context=injury_context,
            similar_situations=similar_situations
        )

        logger.info(
            "prediction_generated",
            player=player.name,
            prediction=prediction_result["prediction"],
            confidence=prediction_result["confidence"]
        )

        # Format current stats for response
        current_stats_response = CurrentStats(
            games_played=current_stats.get("games_played", 0),
            avg_per_game=current_stats.get("avg_per_game", 0.0),
            last_3_games=current_stats.get("last_3_games", []),
            min=current_stats.get("min", 0.0),
            max=current_stats.get("max", 0.0),
            std_dev=current_stats.get("std_dev", 0.0)
        )

        # Format similar situations for response
        similar_situations_response = [
            SimilarSituation(
                similarity_score=sit.get("similarity_score", 0.0),
                player_name=sit.get("player_name", "Unknown"),
                game_info=sit.get("game_info", ""),
                result=sit.get("result", ""),
                narrative=sit.get("narrative", "")
            )
            for sit in similar_situations
        ]

        # Calculate edge
        edge = prediction_result["projected_value"] - line_score

        # Save prediction to database
        prediction_id = str(uuid.uuid4())
        db_prediction = Prediction(
            id=prediction_id,
            prop_id=request.prop_id,
            player_id=str(player.id),
            player_name=player.name,
            player_position=player.player_position or "Unknown",
            team=player.team_id or "Unknown",
            opponent=opponent or "Unknown",
            week=matchup_context.get("week", 0),
            season=2025,
            game_time=matchup_context.get("game_time"),
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

        logger.info(
            "prediction_saved",
            prediction_id=prediction_id,
            player=player.name,
            edge=edge
        )

        # Format response
        response = PredictionResponse(
            prop_id=request.prop_id,
            player_name=player.name,
            player_id=str(player.id),
            position=player.player_position or "Unknown",
            team=player.team_id or "Unknown",
            opponent=opponent or "Unknown",
            week=matchup_context.get("week", 0),
            stat_type=stat_type,
            line_score=line_score,
            prediction=prediction_result["prediction"],
            confidence=prediction_result["confidence"],
            projected_value=prediction_result["projected_value"],
            reasoning=prediction_result["reasoning"],
            key_factors=prediction_result.get("key_factors", []),
            risk_factors=prediction_result.get("risk_factors", []),
            comparable_game=prediction_result.get("comparable_game"),
            current_stats=current_stats_response,
            similar_situations=similar_situations_response,
            similar_situations_count=len(similar_situations),
            model=prediction_result["model"],
            generated_at=datetime.utcnow()
        )

        return response

    except Exception as e:
        logger.error(
            "prediction_error",
            error=str(e),
            player=request.player_name
        )
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/opportunities")
async def get_opportunities(
    position: Optional[str] = Query(None, description="Filter by position (QB, RB, WR, TE)"),
    stat_type: Optional[str] = Query(None, description="Filter by stat type"),
    min_confidence: int = Query(0, ge=0, le=100, description="Minimum confidence threshold"),
    min_edge: float = Query(0.0, description="Minimum edge threshold"),
    sort_by: str = Query("edge", description="Sort by: edge, confidence, game_time"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Get best betting opportunities from cached predictions.

    Returns predictions sorted by edge or confidence, with optional filters.
    This is the main discovery endpoint for the opportunities feed.
    """
    try:
        # Base query - only active predictions
        query = select(Prediction).where(
            and_(
                Prediction.is_active == True,
                Prediction.is_archived == False
            )
        )

        # Apply filters
        if position:
            query = query.where(Prediction.player_position == position)

        if stat_type:
            query = query.where(Prediction.stat_type == stat_type)

        if min_confidence > 0:
            query = query.where(Prediction.confidence >= min_confidence)

        if min_edge > 0:
            query = query.where(Prediction.edge >= min_edge)

        # Apply sorting
        if sort_by == "edge":
            query = query.order_by(desc(Prediction.edge))
        elif sort_by == "confidence":
            query = query.order_by(desc(Prediction.confidence))
        elif sort_by == "game_time":
            query = query.order_by(Prediction.game_time)
        else:
            query = query.order_by(desc(Prediction.edge))

        # Limit results
        query = query.limit(limit)

        # Execute query
        result = await db.execute(query)
        predictions = result.scalars().all()

        logger.info(
            "opportunities_fetched",
            count=len(predictions),
            filters={"position": position, "stat_type": stat_type, "min_confidence": min_confidence}
        )

        # Format response
        return {
            "opportunities": [
                {
                    "id": pred.id,
                    "player_name": pred.player_name,
                    "player_position": pred.player_position,
                    "team": pred.team,
                    "opponent": pred.opponent,
                    "week": pred.week,
                    "game_time": pred.game_time,
                    "stat_type": pred.stat_type,
                    "line_score": pred.line_score,
                    "prediction": pred.prediction,
                    "confidence": pred.confidence,
                    "projected_value": pred.projected_value,
                    "edge": pred.edge,
                    "reasoning": pred.reasoning,
                    "key_factors": json.loads(pred.key_factors) if pred.key_factors else [],
                    "risk_factors": json.loads(pred.risk_factors) if pred.risk_factors else [],
                    "comparable_game": pred.comparable_game,
                    "similar_situations_count": pred.similar_situations_count,
                    "model": pred.model_version,
                    "created_at": pred.created_at
                }
                for pred in predictions
            ],
            "count": len(predictions),
            "filters_applied": {
                "position": position,
                "stat_type": stat_type,
                "min_confidence": min_confidence,
                "min_edge": min_edge,
                "sort_by": sort_by
            }
        }

    except Exception as e:
        logger.error("get_opportunities_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-props")
async def get_active_props(
    limit: int = Query(50, ge=1, le=200),
    stat_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get active props that are ready for prediction.
    """
    try:
        query = select(PrizePicksProjection).where(
            PrizePicksProjection.is_active == True
        )

        if stat_type:
            query = query.where(PrizePicksProjection.stat_type == stat_type)

        query = query.order_by(PrizePicksProjection.game_time).limit(limit)

        result = await db.execute(query)
        props = result.scalars().all()

        return {
            "props": [
                {
                    "id": prop.id,
                    "player_name": prop.player_name,
                    "stat_type": prop.stat_type,
                    "line_score": prop.line_score,
                    "game_time": prop.game_time,
                    "league": prop.league
                }
                for prop in props
            ],
            "count": len(props)
        }

    except Exception as e:
        logger.error("get_active_props_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-batch")
async def generate_batch_predictions(
    week: int = Query(..., description="Week number to generate predictions for"),
    season: int = Query(2025, description="Season year"),
    max_players: Optional[int] = Query(None, description="Limit number of players (for testing)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate predictions for all notable props in the given week.

    This endpoint triggers batch prediction generation for a full week.
    Used by the scheduler or can be triggered manually.
    """
    try:
        batch_service = get_batch_prediction_service()

        logger.info("batch_generation_triggered", week=week, season=season)

        result = await batch_service.generate_weekly_predictions(
            db=db,
            week=week,
            season=season,
            max_players=max_players
        )

        return {
            "status": "success",
            "week": week,
            "season": season,
            **result
        }

    except Exception as e:
        logger.error("batch_generation_error", error=str(e), week=week)
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")


# Helper functions

async def _get_prop_data(db: AsyncSession, request: PredictionRequest) -> Optional[Dict[str, Any]]:
    """Get prop data from request or database"""
    try:
        if request.prop_id:
            # Fetch from PrizePicks projections
            prop = await db.get(PrizePicksProjection, request.prop_id)
            if not prop:
                return None

            # Find matching player
            query = select(Player).where(Player.name == prop.player_name)
            result = await db.execute(query)
            player = result.scalar_one_or_none()

            if not player:
                return None

            return {
                "player": player,
                "stat_type": prop.stat_type,
                "line_score": prop.line_score,
                "opponent": None  # Would need to extract from game data
            }

        elif request.player_name and request.stat_type and request.line_score:
            # Manual prop entry
            query = select(Player).where(Player.name == request.player_name)
            result = await db.execute(query)
            player = result.scalar_one_or_none()

            if not player:
                return None

            return {
                "player": player,
                "stat_type": request.stat_type,
                "line_score": request.line_score,
                "opponent": request.opponent
            }

        return None

    except Exception as e:
        logger.error("get_prop_data_error", error=str(e))
        return None


async def _get_current_season_stats(
    db: AsyncSession,
    player_id: str,
    stat_type: str
) -> Dict[str, Any]:
    """Get player's current season statistics"""
    try:
        # Get current season (assuming 2025)
        current_season = 2025

        # Get all games this season
        query = select(PlayerGameStats).where(
            and_(
                PlayerGameStats.player_id == player_id,
                PlayerGameStats.season == current_season
            )
        ).order_by(desc(PlayerGameStats.week))

        result = await db.execute(query)
        game_stats = result.scalars().all()

        if not game_stats:
            return {
                "games_played": 0,
                "avg_per_game": 0.0,
                "last_3_games": [],
                "std_dev": 0.0,
                "season": current_season
            }

        # Extract stat values
        stat_values = []
        for game in game_stats:
            value = _extract_stat_value(game, stat_type)
            if value is not None:
                stat_values.append(value)

        if not stat_values:
            return {
                "games_played": len(game_stats),
                "avg_per_game": 0.0,
                "last_3_games": [],
                "std_dev": 0.0,
                "season": current_season
            }

        # Calculate stats
        avg = sum(stat_values) / len(stat_values)
        variance = sum((x - avg) ** 2 for x in stat_values) / len(stat_values)
        std_dev = variance ** 0.5

        return {
            "games_played": len(game_stats),
            "avg_per_game": round(avg, 2),
            "last_3_games": stat_values[:3],
            "std_dev": round(std_dev, 2),
            "season": current_season,
            "min": min(stat_values),
            "max": max(stat_values)
        }

    except Exception as e:
        logger.error("get_current_season_stats_error", error=str(e), player_id=player_id)
        return {}


async def _get_matchup_context(
    db: AsyncSession,
    player: Player,
    opponent: Optional[str]
) -> Dict[str, Any]:
    """Get matchup context (opponent defense, weather, vegas lines)"""
    try:
        context = {
            "opponent": opponent or "Unknown",
            "location": "Unknown"
        }

        if not opponent:
            return context

        # Get defensive stats for opponent vs player's position
        position_map = {
            "WR": "WR",
            "RB": "RB",
            "TE": "TE",
            "QB": "QB"
        }

        defensive_position = position_map.get(player.player_position)
        if defensive_position:
            query = select(TeamDefensiveStats).where(
                and_(
                    TeamDefensiveStats.team_id == opponent,
                    TeamDefensiveStats.defensive_position == defensive_position,
                    TeamDefensiveStats.week == 0  # Season average
                )
            )

            result = await db.execute(query)
            def_stat = result.scalar_one_or_none()

            if def_stat:
                context["opponent_rank_vs_position"] = def_stat.rank_vs_position
                context["opponent_avg_points_allowed"] = def_stat.avg_points_allowed

        # TODO: Add weather and vegas lines when available

        return context

    except Exception as e:
        logger.error("get_matchup_context_error", error=str(e))
        return {"opponent": opponent or "Unknown"}


async def _get_injury_context(
    db: AsyncSession,
    player_id: str
) -> Dict[str, Any]:
    """Get injury context for player and key teammates"""
    try:
        # TODO: Implement once PlayerInjury model is added
        # For now, return placeholder
        return {
            "player_status": "ACTIVE",
            "injury_type": None,
            "description": "No injury data available (Sleeper integration pending)"
        }

    except Exception as e:
        logger.error("get_injury_context_error", error=str(e))
        return {"player_status": "UNKNOWN"}


def _build_context_description(
    current_stats: Dict[str, Any],
    matchup_context: Dict[str, Any],
    injury_context: Dict[str, Any]
) -> str:
    """Build description of context for RAG search"""
    parts = []

    # Recent performance
    if current_stats.get("last_3_games"):
        last_3 = current_stats["last_3_games"]
        parts.append(f"recent games: {', '.join(map(str, last_3))}")

    # Opponent difficulty
    if matchup_context.get("opponent_rank_vs_position"):
        rank = matchup_context["opponent_rank_vs_position"]
        if rank <= 10:
            parts.append("tough defensive matchup")
        elif rank >= 25:
            parts.append("favorable defensive matchup")

    # Injury status
    if injury_context.get("player_status") not in ["ACTIVE", "UNKNOWN"]:
        parts.append(f"{injury_context['player_status']} injury status")

    return ", ".join(parts) if parts else "similar recent performances"


async def _validate_and_get_opponent(
    db: AsyncSession,
    player: Player,
    provided_opponent: Optional[str]
) -> Dict[str, Any]:
    """
    CRITICAL: Validate opponent against schedule or auto-lookup from schedule.

    This prevents the critical issue of making predictions against wrong opponents.

    Returns:
        {"opponent": str, "week": int} on success
        {"error": str} on failure
    """
    try:
        # Get current NFL state
        sleeper_service = get_sleeper_stats_service()
        nfl_state = await sleeper_service.get_nfl_state()
        current_week = nfl_state.get("week")
        current_season = nfl_state.get("season")

        # Get player's team
        player_team = player.team_id
        if not player_team:
            return {"error": f"Player {player.name} does not have a team assigned"}

        # Look up game in schedule
        query = select(Game).where(
            and_(
                Game.season == int(current_season),
                Game.week == current_week,
                or_(
                    Game.home_team_id == player_team,
                    Game.away_team_id == player_team
                )
            )
        )

        result = await db.execute(query)
        game = result.scalar_one_or_none()

        if not game:
            return {
                "error": f"No game scheduled for {player_team} in Week {current_week}. "
                        f"Please run: python -m scripts.fetch_nfl_schedule"
            }

        # Check if game already started
        if game.is_completed:
            return {
                "error": f"Game already completed (Week {current_week}: "
                        f"{game.away_team_id} @ {game.home_team_id})"
            }

        # Determine actual opponent
        actual_opponent = game.away_team_id if game.home_team_id == player_team else game.home_team_id

        # If opponent was provided, validate it matches schedule
        if provided_opponent:
            if provided_opponent.upper() != actual_opponent.upper():
                return {
                    "error": f"Opponent mismatch for Week {current_week}. "
                            f"{player.name}'s team ({player_team}) plays {actual_opponent}, not {provided_opponent}. "
                            f"Game: {game.away_team_id} @ {game.home_team_id}"
                }

        logger.info(
            "opponent_validated",
            player=player.name,
            team=player_team,
            opponent=actual_opponent,
            week=current_week,
            provided=provided_opponent
        )

        return {
            "opponent": actual_opponent,
            "week": current_week
        }

    except Exception as e:
        logger.error("opponent_validation_error", error=str(e), player=player.name)
        return {"error": f"Failed to validate opponent: {str(e)}"}


def _extract_stat_value(game_stat: PlayerGameStats, stat_type: str) -> Optional[float]:
    """Extract specific stat value from game stat"""
    stat_mapping = {
        "receiving_yards": game_stat.receiving_yards,
        "receiving_receptions": game_stat.receiving_receptions,
        "receiving_touchdowns": game_stat.receiving_touchdowns,
        "rushing_yards": game_stat.rushing_yards,
        "rushing_attempts": game_stat.rushing_attempts,
        "rushing_touchdowns": game_stat.rushing_touchdowns,
        "passing_yards": game_stat.passing_yards,
        "passing_touchdowns": game_stat.passing_touchdowns,
        "passing_completions": game_stat.passing_completions,
        "interceptions": game_stat.interceptions,
        "fantasy_points": game_stat.fantasy_points,
    }

    return stat_mapping.get(stat_type)
