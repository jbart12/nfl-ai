"""
Claude API Service for NFL Prop Predictions

Uses Anthropic's Claude 3.5 Sonnet to analyze props with full context and reasoning.
"""
import json
import os
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
import structlog

logger = structlog.get_logger()


class ClaudePredictionService:
    """Service for generating NFL prop predictions using Claude AI"""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Latest Claude Sonnet 4.5
        self.max_tokens = 2000

    async def predict_prop(
        self,
        prop: Dict[str, Any],
        current_stats: Dict[str, Any],
        matchup_context: Dict[str, Any],
        injury_context: Dict[str, Any],
        similar_situations: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a prediction for an NFL prop using Claude AI.

        Args:
            prop: Prop details (player, stat_type, line, opponent)
            current_stats: Current season statistics
            matchup_context: Game matchup info (weather, defense rank, vegas lines)
            injury_context: Injury status for player and key teammates
            similar_situations: Historical similar games from RAG search
            additional_context: Any additional context data

        Returns:
            Dict containing:
                - prediction: "OVER" or "UNDER"
                - confidence: 0-100
                - projected_value: Estimated stat value
                - reasoning: Detailed analysis
        """
        try:
            prompt = self._build_prediction_prompt(
                prop=prop,
                current_stats=current_stats,
                matchup_context=matchup_context,
                injury_context=injury_context,
                similar_situations=similar_situations,
                additional_context=additional_context
            )

            logger.info(
                "claude_prediction_request",
                player=prop.get("player"),
                stat_type=prop.get("stat_type"),
                line=prop.get("line")
            )

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract the text content from Claude's response
            response_text = response.content[0].text

            # Parse JSON from response
            prediction_data = self._parse_response(response_text)

            # Add metadata
            prediction_data["model"] = self.model
            prediction_data["prompt_tokens"] = response.usage.input_tokens
            prediction_data["completion_tokens"] = response.usage.output_tokens

            logger.info(
                "claude_prediction_success",
                player=prop.get("player"),
                prediction=prediction_data.get("prediction"),
                confidence=prediction_data.get("confidence"),
                tokens_used=response.usage.input_tokens + response.usage.output_tokens
            )

            return prediction_data

        except Exception as e:
            logger.error(
                "claude_prediction_error",
                error=str(e),
                player=prop.get("player")
            )
            raise

    def _build_prediction_prompt(
        self,
        prop: Dict[str, Any],
        current_stats: Dict[str, Any],
        matchup_context: Dict[str, Any],
        injury_context: Dict[str, Any],
        similar_situations: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build comprehensive prompt for Claude"""

        similar_games_text = self._format_similar_situations(similar_situations)
        additional_text = self._format_additional_context(additional_context) if additional_context else ""

        prompt = f"""You are an expert NFL prop analyzer with deep knowledge of player performance patterns, matchup dynamics, and game contexts.

Analyze the following prop and provide a detailed prediction with reasoning.

CURRENT PROP:
Player: {prop.get('player')}
Stat Type: {prop.get('stat_type')}
Line: {prop.get('line')}
Opponent: {prop.get('opponent')}
Game Week: {prop.get('week', 'N/A')}

CURRENT SEASON STATISTICS:
{self._format_dict(current_stats)}

MATCHUP CONTEXT:
{self._format_dict(matchup_context)}

INJURY STATUS:
{self._format_dict(injury_context)}

SIMILAR HISTORICAL GAMES (from semantic search):
{similar_games_text}

{additional_text}

TASK:
Analyze all the provided context and predict whether this player will go OVER or UNDER the line.

Provide your response in the following JSON format:
{{
    "prediction": "OVER" or "UNDER",
    "confidence": <integer 0-100>,
    "projected_value": <your estimated value for this stat>,
    "reasoning": "<detailed multi-paragraph analysis explaining your prediction>",
    "key_factors": [
        "<factor 1>",
        "<factor 2>",
        "<factor 3>"
    ],
    "risk_factors": [
        "<risk 1>",
        "<risk 2>"
    ],
    "comparable_game": "<most similar historical game from the list above>"
}}

IMPORTANT GUIDELINES:
1. Consider ALL context holistically, not just individual factors
2. Pay special attention to similar historical situations
3. Account for game script (vegas total, spread)
4. Consider weather impact if relevant to the stat type
5. Factor in injury status of player AND key teammates
6. Look for trends in recent performances
7. Consider opponent's defensive strength vs this position
8. Be honest about uncertainty - lower confidence if data is limited
9. Provide detailed reasoning that shows your analytical process
10. Reference specific similar games when they support your prediction

Return ONLY valid JSON, no additional text before or after."""

        return prompt

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary as readable text"""
        if not data:
            return "No data available"

        lines = []
        for key, value in data.items():
            # Convert snake_case to Title Case
            formatted_key = key.replace("_", " ").title()
            lines.append(f"  • {formatted_key}: {value}")

        return "\n".join(lines)

    def _format_similar_situations(self, similar_situations: List[Dict[str, Any]]) -> str:
        """Format similar situations for prompt"""
        if not similar_situations:
            return "No similar historical games found"

        formatted = []
        for i, situation in enumerate(similar_situations, 1):
            game_info = situation.get("game", "Unknown game")
            result = situation.get("result", "Unknown result")
            context = situation.get("context", "No context")
            narrative = situation.get("narrative", "")
            similarity = situation.get("similarity_score", 0)

            formatted.append(f"""
{i}. {game_info} (Similarity: {similarity:.1%})
   Result: {result}
   Context: {context}
   {narrative[:200] + '...' if len(narrative) > 200 else narrative}
""")

        return "\n".join(formatted)

    def _format_additional_context(self, context: Dict[str, Any]) -> str:
        """Format additional context"""
        return f"\nADDITIONAL CONTEXT:\n{self._format_dict(context)}"

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response"""
        try:
            # Try to extract JSON from response
            # Claude sometimes adds text before/after JSON
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")

            json_str = response_text[start_idx:end_idx]
            prediction_data = json.loads(json_str)

            # Validate required fields
            required_fields = ["prediction", "confidence", "projected_value", "reasoning"]
            for field in required_fields:
                if field not in prediction_data:
                    raise ValueError(f"Missing required field: {field}")

            # Validate prediction value
            if prediction_data["prediction"] not in ["OVER", "UNDER"]:
                raise ValueError(f"Invalid prediction: {prediction_data['prediction']}")

            # Validate confidence range
            if not 0 <= prediction_data["confidence"] <= 100:
                raise ValueError(f"Confidence out of range: {prediction_data['confidence']}")

            return prediction_data

        except json.JSONDecodeError as e:
            logger.error("claude_response_parse_error", error=str(e), response=response_text[:200])
            raise ValueError(f"Failed to parse Claude response as JSON: {e}")
        except Exception as e:
            logger.error("claude_response_validation_error", error=str(e))
            raise


# Singleton instance
_claude_service = None

def get_claude_service() -> ClaudePredictionService:
    """Get or create Claude service singleton"""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudePredictionService()
    return _claude_service
