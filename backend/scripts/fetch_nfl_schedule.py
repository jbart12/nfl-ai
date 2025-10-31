"""
Fetch NFL Schedule from Sleeper API

CRITICAL: Ensures we always have accurate matchup data for predictions.
This prevents the issue of predicting against the wrong opponent.
"""
import asyncio
import sys
from pathlib import Path
import argparse

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.nfl import Game, Team
from app.services.sleeper_stats import get_sleeper_stats_service
from app.utils.slate import determine_slate
import structlog
import httpx
from datetime import datetime

logger = structlog.get_logger()


async def fetch_schedule(season: str = "2025", weeks: list = None):
    """
    Fetch NFL schedule and store in database.

    Uses ESPN Scoreboard API since Sleeper doesn't provide schedule data.

    Args:
        season: Season year (default: 2025)
        weeks: List of weeks to fetch, or None for all
    """
    print("NFL Schedule Fetcher - ESPN Scoreboard API")
    print("="*60)
    print(f"Season: {season}")
    print("="*60)
    print()

    async with AsyncSessionLocal() as session:
        try:
            sleeper_service = get_sleeper_stats_service()

            # Get current NFL state
            nfl_state = await sleeper_service.get_nfl_state()
            current_week = nfl_state.get("week")

            print(f"Current Week: {current_week}")
            print()

            # Determine weeks to fetch
            if not weeks:
                # Fetch all weeks up to current + next 2
                weeks = list(range(1, min(current_week + 3, 19)))

            games_added = 0
            games_updated = 0

            for week in weeks:
                print(f"Fetching Week {week}...")

                # Fetch schedule from ESPN Scoreboard API
                url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
                params = {
                    "seasontype": "2",  # Regular season
                    "week": str(week),
                    "dates": season
                }

                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(url, params=params)

                    if response.status_code != 200:
                        print(f"  ✗ No schedule data for Week {week}")
                        continue

                    data = response.json()
                    games_data = data.get("events", [])

                    if not games_data:
                        print(f"  ✗ No games found for Week {week}")
                        continue

                    print(f"  Found {len(games_data)} games")

                    for event in games_data:
                        # Parse ESPN event data
                        event_id = event.get("id")
                        competitions = event.get("competitions", [])

                        if not competitions:
                            continue

                        competition = competitions[0]
                        competitors = competition.get("competitors", [])

                        if len(competitors) < 2:
                            continue

                        # ESPN format: competitors[0] is home, competitors[1] is away
                        home_competitor = next((c for c in competitors if c.get("homeAway") == "home"), None)
                        away_competitor = next((c for c in competitors if c.get("homeAway") == "away"), None)

                        if not home_competitor or not away_competitor:
                            continue

                        # Get team abbreviations
                        home_team = home_competitor.get("team", {}).get("abbreviation")
                        away_team = away_competitor.get("team", {}).get("abbreviation")

                        if not home_team or not away_team:
                            continue

                        # Get scores (if game is complete)
                        home_score = home_competitor.get("score")
                        away_score = away_competitor.get("score")

                        # Check if completed
                        status = competition.get("status", {})
                        is_completed = status.get("type", {}).get("completed", False)

                        # Parse game time
                        game_time = None
                        game_date_str = event.get("date")
                        if game_date_str:
                            try:
                                game_time = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                                # Convert to naive datetime (UTC) for database storage
                                game_time = game_time.replace(tzinfo=None)
                            except:
                                pass

                        # Determine slate from game time (need to make aware for slate calculation)
                        import pytz
                        slate = None
                        if game_time:
                            game_time_aware = pytz.utc.localize(game_time)
                            slate = determine_slate(game_time_aware)

                        # Create game ID
                        game_id = f"{season}_{week}_{away_team}_{home_team}"

                        # Check if game exists
                        existing_game = await session.get(Game, game_id)

                        if existing_game:
                            # Update scores if game is completed
                            if is_completed and home_score is not None:
                                existing_game.away_score = int(away_score) if away_score else None
                                existing_game.home_score = int(home_score) if home_score else None
                                existing_game.is_completed = True
                                games_updated += 1
                            # Update game time and slate if not set
                            if game_time and not existing_game.game_time:
                                existing_game.game_time = game_time
                                existing_game.slate = slate
                        else:
                            # Create new game
                            new_game = Game(
                                id=game_id,
                                season=int(season),
                                week=week,
                                game_time=game_time,
                                slate=slate,
                                home_team_id=home_team,
                                away_team_id=away_team,
                                home_score=int(home_score) if home_score and is_completed else None,
                                away_score=int(away_score) if away_score and is_completed else None,
                                is_completed=is_completed
                            )
                            session.add(new_game)
                            games_added += 1

                await session.commit()
                print(f"  ✓ Week {week} complete")

            print()
            print("="*60)
            print(f"✓ Schedule fetch complete")
            print(f"  Games added: {games_added}")
            print(f"  Games updated: {games_updated}")
            print("="*60)

            logger.info(
                "schedule_fetched",
                season=season,
                games_added=games_added,
                games_updated=games_updated
            )

        except Exception as e:
            logger.error("fetch_schedule_error", error=str(e))
            print(f"\n✗ Error: {e}")
            raise


async def get_current_week_matchups():
    """Display current week matchups for quick reference"""
    print("\n" + "="*60)
    print("CURRENT WEEK MATCHUPS")
    print("="*60)

    async with AsyncSessionLocal() as session:
        sleeper_service = get_sleeper_stats_service()
        nfl_state = await sleeper_service.get_nfl_state()
        current_week = nfl_state.get("week")
        current_season = nfl_state.get("season")

        # Fetch current week schedule
        url = f"https://api.sleeper.app/v1/schedules/nfl/regular/{current_season}/{current_week}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                games = response.json()

                print(f"\nWeek {current_week} Games:")
                print("-" * 60)

                for game in games:
                    away = game.get("away", "???")
                    home = game.get("home", "???")
                    print(f"  {away:4s} @ {home:4s}")

                print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch NFL schedule from Sleeper API")
    parser.add_argument("--season", type=str, default="2025")
    parser.add_argument("--weeks", type=int, nargs="+", help="Specific weeks to fetch")
    parser.add_argument("--show-current", action="store_true", help="Show current week matchups")

    args = parser.parse_args()

    if args.show_current:
        asyncio.run(get_current_week_matchups())
    else:
        asyncio.run(fetch_schedule(
            season=args.season,
            weeks=args.weeks
        ))
