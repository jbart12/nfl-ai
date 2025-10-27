"""
Demo: AI Prediction with Schedule Validation

Demonstrates the complete prediction flow with validated opponent.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.nfl import Player, PlayerGameStats
from app.services.claude_prediction import get_claude_service
from app.services.rag_narrative import get_rag_service
from app.api.endpoints.predictions import (
    _validate_and_get_opponent,
    _get_current_season_stats,
    _get_matchup_context,
    _get_injury_context,
    _build_context_description
)
import structlog

logger = structlog.get_logger()


async def run_prediction():
    """Run a complete prediction for Patrick Mahomes vs WSH"""

    print("="*80)
    print("NFL AI PREDICTION SYSTEM - DEMO")
    print("="*80)
    print()

    async with AsyncSessionLocal() as db:
        # 1. Get player
        print("1. Looking up player...")
        query = select(Player).where(Player.name == "Patrick Mahomes")
        result = await db.execute(query)
        player = result.scalar_one_or_none()

        if not player:
            print("✗ Patrick Mahomes not found")
            return

        print(f"   ✓ Found: {player.name} ({player.player_position}, {player.team_id})")
        print()

        # 2. Validate opponent
        print("2. Validating opponent against schedule...")
        validated = await _validate_and_get_opponent(db, player, "WSH")

        if "error" in validated:
            print(f"   ✗ ERROR: {validated['error']}")
            return

        opponent = validated["opponent"]
        current_week = validated["week"]

        print(f"   ✓ Opponent validated: {opponent}")
        print(f"   ✓ Week: {current_week}")
        print()

        # 3. Gather stats
        print("3. Gathering player statistics...")
        stat_type = "passing_yards"
        line_score = 265.5

        current_stats = await _get_current_season_stats(db, player.id, stat_type)

        print(f"   Season Stats (2025):")
        print(f"   - Games Played: {current_stats.get('games_played', 0)}")
        print(f"   - Average: {current_stats.get('avg_per_game', 0)} yards/game")
        print(f"   - Last 3 Games: {current_stats.get('last_3_games', [])}")
        print(f"   - Range: {current_stats.get('min', 0)} - {current_stats.get('max', 0)} yards")
        print()

        # 4. Get matchup context
        print("4. Analyzing matchup...")
        matchup_context = await _get_matchup_context(db, player, opponent)
        injury_context = await _get_injury_context(db, player.id)

        print(f"   Opponent: {opponent}")
        print(f"   Location: {matchup_context.get('location', 'Unknown')}")
        print()

        # 5. RAG Search
        print("5. Finding similar situations (RAG)...")
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

            print(f"   ✓ Found {len(similar_situations)} similar situations")
        except Exception as e:
            print(f"   ⚠ RAG unavailable: {str(e)}")
            similar_situations = []
        print()

        # 6. Generate prediction
        print("6. Generating AI prediction...")
        print()

        prop_context = {
            "player": player.name,
            "stat_type": stat_type,
            "line": line_score,
            "opponent": opponent,
            "week": current_week
        }

        claude_service = get_claude_service()
        prediction = await claude_service.predict_prop(
            prop=prop_context,
            current_stats=current_stats,
            matchup_context=matchup_context,
            injury_context=injury_context,
            similar_situations=similar_situations
        )

        # 7. Display results
        print("="*80)
        print("PREDICTION RESULTS")
        print("="*80)
        print()
        print(f"Player:     {player.name}")
        print(f"Opponent:   {opponent} (Week {current_week})")
        print(f"Prop:       {stat_type.replace('_', ' ').title()}")
        print(f"Line:       {line_score} yards")
        print()
        print(f"PREDICTION: {prediction['prediction']}")
        print(f"Confidence: {prediction['confidence']}%")
        print(f"Projected:  {prediction['projected_value']} yards")
        print()
        print("Reasoning:")
        print("-" * 80)
        print(prediction['reasoning'])
        print()

        if prediction.get('key_factors'):
            print("Key Factors:")
            for factor in prediction['key_factors']:
                print(f"  • {factor}")
            print()

        if prediction.get('risk_factors'):
            print("Risk Factors:")
            for risk in prediction['risk_factors']:
                print(f"  ⚠ {risk}")
            print()

        print("="*80)
        print(f"Model: {prediction['model']}")
        print(f"Similar Situations: {len(similar_situations)}")
        print("="*80)
        print()
        print("✓ Prediction complete with VALIDATED opponent!")
        print()


if __name__ == "__main__":
    asyncio.run(run_prediction())
