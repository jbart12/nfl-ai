"""
PrizePicks API Service

Fetches real player prop lines from PrizePicks for use in predictions.
PrizePicks provides free, public access to thousands of NFL player props.
"""
import asyncio
import aiohttp
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = structlog.get_logger()


class PrizePicksService:
    """Service for fetching player props from PrizePicks API"""

    BASE_URL = "https://api.prizepicks.com"
    NFL_LEAGUE_ID = 9  # CRITICAL: Must be 9 for NFL

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://app.prizepicks.com/',
            'Origin': 'https://app.prizepicks.com',
            'Connection': 'keep-alive',
        }

    async def fetch_nfl_projections(self) -> List[Dict[str, Any]]:
        """
        Fetch all active NFL player prop projections.

        Returns:
            List of projection dictionaries with player and prop info
        """
        params = {
            'league_id': self.NFL_LEAGUE_ID,
            'per_page': 250,
            'single_stat': 'true'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/projections",
                    params=params,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        projections = self._parse_projections(data)
                        logger.info(
                            "prizepicks_fetch_success",
                            count=len(projections)
                        )
                        return projections
                    else:
                        logger.error(
                            "prizepicks_fetch_failed",
                            status=response.status
                        )
                        return []
        except Exception as e:
            logger.error("prizepicks_fetch_error", error=str(e))
            return []

    def _parse_projections(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse PrizePicks JSON-API response into simplified projection format.

        Args:
            data: Raw JSON-API response

        Returns:
            List of parsed projections
        """
        projections = []

        # Build player map from included entities
        player_map = {}
        for entity in data.get('included', []):
            if entity.get('type') == 'new_player':
                player_id = entity['id']
                player_map[player_id] = entity.get('attributes', {})

        # Parse each projection
        for proj_data in data.get('data', []):
            attributes = proj_data.get('attributes', {})
            relationships = proj_data.get('relationships', {})

            # Get player info
            player_rel = relationships.get('new_player', {}).get('data', {})
            player_id = player_rel.get('id')
            player_info = player_map.get(player_id, {})

            # Map PrizePicks stat types to our internal format
            stat_type = self._normalize_stat_type(attributes.get('stat_type', ''))

            if stat_type:  # Only include if we can map the stat type
                projection = {
                    'prizepicks_id': proj_data['id'],
                    'player_name': player_info.get('name', ''),
                    'team': player_info.get('team', ''),
                    'position': player_info.get('position', ''),
                    'stat_type': stat_type,
                    'line_score': float(attributes.get('line_score', 0)),
                    'start_time': attributes.get('start_time'),
                    'description': attributes.get('description', ''),
                    'is_promo': attributes.get('is_promo', False),
                }
                projections.append(projection)

        return projections

    def _normalize_stat_type(self, prizepicks_stat: str) -> Optional[str]:
        """
        Map PrizePicks stat type names to our internal stat type format.

        Args:
            prizepicks_stat: PrizePicks stat type (e.g., "Receiving Yards")

        Returns:
            Our internal stat type (e.g., "receiving_yards") or None if unmappable
        """
        mapping = {
            # Passing
            'Pass Yds': 'passing_yards',
            'Pass Yards': 'passing_yards',
            'Passing Yards': 'passing_yards',
            'Pass TDs': 'passing_touchdowns',
            'Pass Touchdowns': 'passing_touchdowns',
            'Passing Touchdowns': 'passing_touchdowns',
            'Pass Completions': 'pass_completions',
            'Pass Attempts': 'pass_attempts',
            'INT': 'interceptions',
            'Interceptions': 'interceptions',

            # Rushing
            'Rush Yds': 'rushing_yards',
            'Rush Yards': 'rushing_yards',
            'Rushing Yards': 'rushing_yards',
            'Rush Attempts': 'rush_attempts',
            'Rush TDs': 'rushing_touchdowns',
            'Rush Touchdowns': 'rushing_touchdowns',
            'Rushing Touchdowns': 'rushing_touchdowns',

            # Receiving
            'Rec Yds': 'receiving_yards',
            'Receiving Yds': 'receiving_yards',
            'Receiving Yards': 'receiving_yards',
            'Receptions': 'receptions',
            'Rec': 'receptions',
            'Rec TDs': 'receiving_touchdowns',
            'Receiving TDs': 'receiving_touchdowns',
            'Receiving Touchdowns': 'receiving_touchdowns',
            'Rec Targets': 'receiving_targets',

            # Combined
            'Pass+Rush Yds': 'pass_rush_yards',
            'Rush+Rec Yds': 'rush_rec_yards',
            'Rush+Rec TDs': 'rush_rec_touchdowns',

            # Fantasy
            'Fantasy Score': 'fantasy_points',
            'Fantasy Points': 'fantasy_points',
        }

        return mapping.get(prizepicks_stat)

    async def get_props_for_player(
        self,
        player_name: str,
        team: str
    ) -> List[Dict[str, Any]]:
        """
        Get all available props for a specific player.

        Args:
            player_name: Player's name
            team: Team abbreviation

        Returns:
            List of props for this player
        """
        all_props = await self.fetch_nfl_projections()

        player_props = [
            p for p in all_props
            if p['player_name'] == player_name and p['team'] == team
        ]

        return player_props

    async def get_props_by_stat_type(
        self,
        stat_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get all props for a specific stat type.

        Args:
            stat_type: Our internal stat type (e.g., "receiving_yards")

        Returns:
            List of props for this stat type
        """
        all_props = await self.fetch_nfl_projections()
        return [p for p in all_props if p['stat_type'] == stat_type]


# Global instance
_prizepicks_service = None


def get_prizepicks_service() -> PrizePicksService:
    """Get the global PrizePicks service instance"""
    global _prizepicks_service
    if _prizepicks_service is None:
        _prizepicks_service = PrizePicksService()
    return _prizepicks_service
