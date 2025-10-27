"""
Sleeper API Stats Service

Fetches current, live NFL player stats from Sleeper API.
This is the PRIMARY data source for up-to-date player statistics.

Sleeper API advantages:
- Completely free, no authentication required
- Real-time stats for current 2025 season
- Weekly game-by-game data
- Reliable and well-documented
"""
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

logger = structlog.get_logger()


class SleeperStatsService:
    """Service for fetching player statistics from Sleeper API"""

    def __init__(self):
        self.base_url = "https://api.sleeper.app/v1"
        self.timeout = 30.0
        self._players_cache = None  # Cache player mappings

    async def get_nfl_state(self) -> Dict[str, Any]:
        """
        Get current NFL season state (current week, season, type).

        Returns:
            {
                "week": 8,
                "season": "2025",
                "season_type": "regular",  # "pre", "regular", "post"
                "display_week": 8
            }
        """
        try:
            url = f"{self.base_url}/state/nfl"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                state = response.json()

                logger.info(
                    "nfl_state_fetched",
                    week=state.get("week"),
                    season=state.get("season"),
                    season_type=state.get("season_type")
                )

                return state

        except Exception as e:
            logger.error("get_nfl_state_error", error=str(e))
            raise

    async def get_all_players(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all NFL players from Sleeper.
        Results are cached since this is a large response (~10MB).

        Returns:
            Dictionary mapping player_id to player info
        """
        if self._players_cache:
            return self._players_cache

        try:
            url = f"{self.base_url}/players/nfl"

            async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for large response
                response = await client.get(url)
                response.raise_for_status()
                players = response.json()

                self._players_cache = players

                logger.info("sleeper_players_fetched", count=len(players))

                return players

        except Exception as e:
            logger.error("get_all_players_error", error=str(e))
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True
    )
    async def get_player_stats_for_week(
        self,
        season: str,
        week: int,
        season_type: str = "regular"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get all player stats for a specific week.

        Args:
            season: Season year (e.g., "2025")
            week: Week number (1-18 for regular season)
            season_type: "pre", "regular", or "post"

        Returns:
            Dictionary mapping player_id to their stats for that week
        """
        try:
            url = f"{self.base_url}/stats/nfl/{season_type}/{season}/{week}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                stats = response.json()

                logger.info(
                    "player_week_stats_fetched",
                    season=season,
                    week=week,
                    season_type=season_type,
                    players_count=len(stats) if stats else 0
                )

                return stats or {}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(
                    "player_week_stats_not_found",
                    season=season,
                    week=week,
                    season_type=season_type
                )
                return {}
            raise

        except Exception as e:
            logger.error(
                "get_player_stats_error",
                error=str(e),
                season=season,
                week=week
            )
            raise

    async def get_player_season_stats(
        self,
        sleeper_player_id: str,
        season: str,
        season_type: str = "regular"
    ) -> List[Dict[str, Any]]:
        """
        Get all weekly stats for a player for an entire season.

        Args:
            sleeper_player_id: Sleeper player ID
            season: Season year (e.g., "2025")
            season_type: "pre", "regular", or "post"

        Returns:
            List of weekly stats dictionaries
        """
        season_stats = []

        # Regular season is typically 18 weeks
        max_week = 18 if season_type == "regular" else (3 if season_type == "pre" else 5)

        for week in range(1, max_week + 1):
            week_stats = await self.get_player_stats_for_week(season, week, season_type)

            if sleeper_player_id in week_stats:
                player_week_stats = week_stats[sleeper_player_id]
                player_week_stats["week"] = week
                player_week_stats["season"] = season
                player_week_stats["season_type"] = season_type
                season_stats.append(player_week_stats)

        logger.info(
            "player_season_stats_fetched",
            player_id=sleeper_player_id,
            season=season,
            games_found=len(season_stats)
        )

        return season_stats

    def normalize_stats(self, raw_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Sleeper stats format to our database schema.

        Sleeper uses different field names, this maps them to our schema.
        """
        normalized = {}

        # Passing stats
        if "pass_cmp" in raw_stats:
            normalized["passing_completions"] = raw_stats.get("pass_cmp", 0)
        if "pass_att" in raw_stats:
            normalized["passing_attempts"] = raw_stats.get("pass_att", 0)
        if "pass_yd" in raw_stats:
            normalized["passing_yards"] = raw_stats.get("pass_yd", 0)
        if "pass_td" in raw_stats:
            normalized["passing_touchdowns"] = raw_stats.get("pass_td", 0)
        if "pass_int" in raw_stats:
            normalized["interceptions"] = raw_stats.get("pass_int", 0)

        # Rushing stats
        if "rush_att" in raw_stats:
            normalized["rushing_attempts"] = raw_stats.get("rush_att", 0)
        if "rush_yd" in raw_stats:
            normalized["rushing_yards"] = raw_stats.get("rush_yd", 0)
        if "rush_td" in raw_stats:
            normalized["rushing_touchdowns"] = raw_stats.get("rush_td", 0)

        # Receiving stats
        if "rec" in raw_stats:
            normalized["receiving_receptions"] = raw_stats.get("rec", 0)
        if "rec_tgt" in raw_stats:
            normalized["receiving_targets"] = raw_stats.get("rec_tgt", 0)
        if "rec_yd" in raw_stats:
            normalized["receiving_yards"] = raw_stats.get("rec_yd", 0)
        if "rec_td" in raw_stats:
            normalized["receiving_touchdowns"] = raw_stats.get("rec_td", 0)

        # Fantasy points (various scoring systems)
        if "pts_half_ppr" in raw_stats:
            normalized["fantasy_points"] = raw_stats.get("pts_half_ppr", 0)
        elif "pts_ppr" in raw_stats:
            normalized["fantasy_points"] = raw_stats.get("pts_ppr", 0)
        elif "pts_std" in raw_stats:
            normalized["fantasy_points"] = raw_stats.get("pts_std", 0)

        return normalized


# Singleton instance
_sleeper_stats_service = None


def get_sleeper_stats_service() -> SleeperStatsService:
    """Get or create Sleeper stats service singleton"""
    global _sleeper_stats_service
    if _sleeper_stats_service is None:
        _sleeper_stats_service = SleeperStatsService()
    return _sleeper_stats_service
