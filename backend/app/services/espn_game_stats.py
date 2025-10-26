"""
ESPN Player Game Stats Service

Fetches game-by-game player statistics from ESPN API.
This is CRITICAL for populating player_game_stats table with historical performance data.
"""
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = structlog.get_logger()


class ESPNGameStatsService:
    """Service for fetching player game-by-game statistics from ESPN"""

    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        self.timeout = 30.0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True
    )
    async def get_player_game_log(
        self,
        espn_player_id: str,
        season: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch a player's game-by-game statistics for a season.

        Args:
            espn_player_id: ESPN's player ID
            season: Season year (e.g., 2025, 2024)

        Returns:
            List of game statistics dictionaries
        """
        try:
            url = f"{self.base_url}/athletes/{espn_player_id}/gamelog"
            params = {"season": season}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                game_logs = []

                # ESPN returns game logs in "events" or "seasonTypes" structure
                season_types = data.get("seasonTypes", [])

                for season_type in season_types:
                    if season_type.get("type") != 2:  # 2 = regular season
                        continue

                    categories = season_type.get("categories", [])

                    for category in categories:
                        events = category.get("events", [])

                        for event in events:
                            game_log = self._parse_game_log_event(event, espn_player_id)
                            if game_log:
                                game_logs.append(game_log)

                logger.info(
                    "player_game_log_fetched",
                    player_id=espn_player_id,
                    season=season,
                    games_found=len(game_logs)
                )

                return game_logs

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(
                    "player_game_log_not_found",
                    player_id=espn_player_id,
                    season=season
                )
                return []
            else:
                logger.error(
                    "espn_game_log_http_error",
                    player_id=espn_player_id,
                    status_code=e.response.status_code
                )
                raise

        except Exception as e:
            logger.error(
                "espn_game_log_error",
                error=str(e),
                player_id=espn_player_id,
                season=season
            )
            raise

    async def get_game_box_score(
        self,
        game_id: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch box score for a specific game with all player stats.

        Args:
            game_id: ESPN game ID

        Returns:
            Dictionary mapping team IDs to lists of player stats
        """
        try:
            url = f"{self.base_url}/summary"
            params = {"event": game_id}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                box_score = data.get("boxscore", {})
                players_by_team = {}

                for team in box_score.get("players", []):
                    team_id = team.get("team", {}).get("id", "")
                    team_abbr = team.get("team", {}).get("abbreviation", "")

                    player_stats = []

                    for stat_category in team.get("statistics", []):
                        category_name = stat_category.get("name", "").lower()

                        for athlete in stat_category.get("athletes", []):
                            athlete_info = athlete.get("athlete", {})
                            stats = athlete.get("stats", [])

                            player_stat = {
                                "espn_player_id": athlete_info.get("id", ""),
                                "player_name": athlete_info.get("displayName", ""),
                                "position": athlete_info.get("position", {}).get("abbreviation", ""),
                                "team_abbr": team_abbr,
                                "stats": self._parse_box_score_stats(stats, category_name)
                            }

                            player_stats.append(player_stat)

                    players_by_team[team_id] = player_stats

                logger.info(
                    "game_box_score_fetched",
                    game_id=game_id,
                    teams=len(players_by_team)
                )

                return players_by_team

        except Exception as e:
            logger.error(
                "espn_box_score_error",
                error=str(e),
                game_id=game_id
            )
            raise

    def _parse_game_log_event(
        self,
        event: Dict[str, Any],
        espn_player_id: str
    ) -> Optional[Dict[str, Any]]:
        """Parse a single game log event into our format"""
        try:
            # Extract game metadata
            game_info = event.get("gameInfo", {})
            opponent = game_info.get("opponent", {})
            stats = event.get("stats", [])

            # Parse date
            game_date_str = game_info.get("date", "")
            game_date = None
            if game_date_str:
                try:
                    game_date = datetime.fromisoformat(game_date_str.replace("Z", "+00:00"))
                except:
                    pass

            game_log = {
                "espn_player_id": espn_player_id,
                "espn_game_id": game_info.get("id", ""),
                "game_date": game_date,
                "week": game_info.get("week", {}).get("number", 0),
                "season": game_info.get("season", {}).get("year", 0),
                "opponent_abbr": opponent.get("abbreviation", ""),
                "is_home": not game_info.get("atVs", "vs").startswith("@"),
                "stats": self._parse_game_log_stats(stats)
            }

            return game_log

        except Exception as e:
            logger.warning(
                "parse_game_log_event_error",
                error=str(e),
                player_id=espn_player_id
            )
            return None

    def _parse_game_log_stats(self, stats: List[str]) -> Dict[str, float]:
        """
        Parse ESPN game log stats array into a dictionary.

        ESPN returns stats as a string array that maps to stat labels.
        Common positions:
        - QB: [C/ATT, YDS, AVG, TD, INT, QBR, RTG]
        - RB: [CAR, YDS, AVG, TD, LONG, REC, YDS, TD]
        - WR/TE: [REC, TAR, YDS, AVG, TD, LONG]
        """
        parsed_stats = {}

        # This is a simplified parser - ESPN's format can vary by position
        # In production, you'd want more robust parsing based on the stat labels
        # which are provided separately in the API response

        if len(stats) == 0:
            return parsed_stats

        # For now, return raw stats with generic keys
        # TODO: Enhance this with proper label mapping from ESPN API
        for i, stat in enumerate(stats):
            try:
                # Try to convert to float, skip if not a number
                parsed_stats[f"stat_{i}"] = float(stat) if stat else 0.0
            except (ValueError, TypeError):
                parsed_stats[f"stat_{i}"] = 0.0

        return parsed_stats

    def _parse_box_score_stats(
        self,
        stats: List[str],
        category_name: str
    ) -> Dict[str, float]:
        """Parse box score stats based on category"""
        parsed = {}

        # Box score stats come with labels, so we can parse more accurately
        # Common categories: "passing", "rushing", "receiving", "defensive"

        if category_name == "passing" and len(stats) >= 7:
            # [C/ATT, YDS, AVG, TD, INT, SACK, QBR, RTG]
            parsed = {
                "passing_completions": self._parse_fraction(stats[0], index=0),
                "passing_attempts": self._parse_fraction(stats[0], index=1),
                "passing_yards": self._safe_float(stats[1]),
                "passing_avg": self._safe_float(stats[2]),
                "passing_touchdowns": self._safe_float(stats[3]),
                "interceptions": self._safe_float(stats[4]),
            }

        elif category_name == "rushing" and len(stats) >= 4:
            # [CAR, YDS, AVG, TD, LONG]
            parsed = {
                "rushing_attempts": self._safe_float(stats[0]),
                "rushing_yards": self._safe_float(stats[1]),
                "rushing_avg": self._safe_float(stats[2]),
                "rushing_touchdowns": self._safe_float(stats[3]),
                "rushing_long": self._safe_float(stats[4]) if len(stats) > 4 else 0.0,
            }

        elif category_name == "receiving" and len(stats) >= 4:
            # [REC, TAR, YDS, AVG, TD, LONG]
            parsed = {
                "receiving_receptions": self._safe_float(stats[0]),
                "receiving_targets": self._safe_float(stats[1]),
                "receiving_yards": self._safe_float(stats[2]),
                "receiving_avg": self._safe_float(stats[3]),
                "receiving_touchdowns": self._safe_float(stats[4]) if len(stats) > 4 else 0.0,
                "receiving_long": self._safe_float(stats[5]) if len(stats) > 5 else 0.0,
            }

        return parsed

    def _safe_float(self, value: Any) -> float:
        """Safely convert value to float"""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Remove non-numeric characters except decimal point
                cleaned = ''.join(c for c in value if c.isdigit() or c == '.')
                return float(cleaned) if cleaned else 0.0
            return 0.0
        except (ValueError, TypeError):
            return 0.0

    def _parse_fraction(self, fraction_str: str, index: int = 0) -> float:
        """Parse fraction string like '23/35' and return the part at index"""
        try:
            if '/' in str(fraction_str):
                parts = str(fraction_str).split('/')
                if len(parts) == 2:
                    return float(parts[index])
            return 0.0
        except (ValueError, TypeError, IndexError):
            return 0.0

    async def bulk_fetch_player_stats(
        self,
        player_ids: List[str],
        season: int,
        batch_size: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch game logs for multiple players in batches.

        Args:
            player_ids: List of ESPN player IDs
            season: Season year
            batch_size: Number of concurrent requests

        Returns:
            Dictionary mapping player IDs to their game logs
        """
        results = {}

        # Process in batches to avoid overwhelming the API
        for i in range(0, len(player_ids), batch_size):
            batch = player_ids[i:i + batch_size]

            logger.info(
                "fetching_player_batch",
                batch_num=i // batch_size + 1,
                total_batches=(len(player_ids) + batch_size - 1) // batch_size,
                batch_size=len(batch)
            )

            # Fetch all players in this batch concurrently
            import asyncio
            tasks = [
                self.get_player_game_log(player_id, season)
                for player_id in batch
            ]

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Map results
            for player_id, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(
                        "player_stats_fetch_failed",
                        player_id=player_id,
                        error=str(result)
                    )
                    results[player_id] = []
                else:
                    results[player_id] = result

        logger.info(
            "bulk_fetch_complete",
            players_processed=len(results),
            season=season
        )

        return results


# Singleton instance
_espn_game_stats_service = None


def get_espn_game_stats_service() -> ESPNGameStatsService:
    """Get or create ESPN game stats service singleton"""
    global _espn_game_stats_service
    if _espn_game_stats_service is None:
        _espn_game_stats_service = ESPNGameStatsService()
    return _espn_game_stats_service
