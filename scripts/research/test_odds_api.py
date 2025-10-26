"""
The Odds API Research Script

The-Odds-API provides betting odds from multiple sportsbooks including:
- Game lines (spread, moneyline, totals)
- Player props (passing yards, TDs, receptions, etc.)

This is CRITICAL for our system because ESPN and Sleeper do NOT provide prop odds.

This script tests:
1. If player props are available (vs just game lines)
2. What prop types are available
3. Which sportsbooks are covered
4. Data freshness and update frequency
5. Rate limits and cost structure

**IMPORTANT:** This API requires an API key. Get one free at: https://the-odds-api.com/
Free tier: 500 requests/month, good for testing.

Run this script to save sample responses and generate documentation.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiohttp


class OddsAPIResearcher:
    """Research The Odds API endpoints and document findings."""

    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")

        if not self.api_key:
            print("⚠️  WARNING: No ODDS_API_KEY found in environment!")
            print("Get a free API key at: https://the-odds-api.com/")
            print("Add to .env file: ODDS_API_KEY=your_key_here")
            print("\nProceeding with test key (will likely fail)...")
            self.api_key = "test"

        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "endpoints_tested": [],
            "successful": [],
            "failed": [],
            "findings": {},
            "api_usage": {},
        }

        # Create directories for saving results
        self.samples_dir = Path("/Users/jace/dev/nfl-ai/samples/odds_api")
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    async def test_endpoint(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        description: str,
        save_as: str,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Test a single Odds API endpoint.

        Args:
            session: aiohttp session
            endpoint: API endpoint path
            description: Human-readable description
            save_as: Filename to save response
            params: Query parameters

        Returns:
            Test results dictionary
        """
        # Add API key to params
        if params is None:
            params = {}
        params["apiKey"] = self.api_key

        url = f"{self.BASE_URL}{endpoint}"
        result = {
            "endpoint": endpoint,
            "description": description,
            "url": url,
            "params": {k: v for k, v in params.items() if k != "apiKey"},  # Don't log API key
            "status": "pending",
        }

        try:
            print(f"\n{'='*80}")
            print(f"Testing: {description}")
            print(f"URL: {url}")
            print(f"Params: {result['params']}")
            print(f"{'='*80}")

            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                result["status_code"] = response.status

                # Check for rate limit headers
                if "x-requests-remaining" in response.headers:
                    result["requests_remaining"] = response.headers["x-requests-remaining"]
                    print(f"📊 API Requests Remaining: {result['requests_remaining']}")

                if "x-requests-used" in response.headers:
                    result["requests_used"] = response.headers["x-requests-used"]
                    print(f"📊 API Requests Used: {result['requests_used']}")

                if response.status == 200:
                    data = await response.json()
                    result["status"] = "success"
                    result["response_size"] = len(json.dumps(data))

                    # Save the response
                    save_path = self.samples_dir / f"{save_as}.json"
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)

                    result["saved_to"] = str(save_path)

                    # Analyze the response
                    result["analysis"] = self._analyze_response(data, description)

                    print(f"✅ SUCCESS - Status: {response.status}")
                    print(f"📦 Response size: {result['response_size']:,} bytes")
                    print(f"💾 Saved to: {save_path}")

                    # Print key findings
                    if result["analysis"]:
                        print(f"\n📊 Key Findings:")
                        for key, value in result["analysis"].items():
                            print(f"  - {key}: {value}")

                elif response.status == 401:
                    result["status"] = "failed"
                    result["error"] = "Invalid API key"
                    print(f"❌ FAILED - Invalid API key")
                    print(f"Get a free API key at: https://the-odds-api.com/")

                elif response.status == 422:
                    result["status"] = "failed"
                    error_data = await response.json()
                    result["error"] = error_data
                    print(f"❌ FAILED - Invalid parameters: {error_data}")

                else:
                    result["status"] = "failed"
                    result["error"] = f"HTTP {response.status}"
                    print(f"❌ FAILED - Status: {response.status}")
                    try:
                        error_data = await response.json()
                        print(f"Error details: {error_data}")
                    except:
                        pass

        except asyncio.TimeoutError:
            result["status"] = "failed"
            result["error"] = "Request timeout"
            print(f"❌ FAILED - Timeout")
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"❌ FAILED - Error: {e}")

        return result

    def _analyze_response(self, data: Dict[str, Any], description: str) -> Dict[str, Any]:
        """
        Analyze API response and extract key information.

        Args:
            data: JSON response data
            description: Endpoint description

        Returns:
            Analysis results
        """
        analysis = {}

        # Sports list analysis
        if "sports" in description.lower() and isinstance(data, list):
            analysis["num_sports"] = len(data)
            nfl_sports = [s for s in data if "football" in s.get("title", "").lower()]
            if nfl_sports:
                analysis["nfl_sports_available"] = [s["key"] for s in nfl_sports]

        # Odds data analysis
        elif "odds" in description.lower() or "events" in description.lower():
            if isinstance(data, list):
                analysis["num_events"] = len(data)
                if data:
                    event = data[0]
                    analysis["event_keys"] = list(event.keys())

                    # Check if this has player props
                    if "bookmakers" in event:
                        bookmakers = event["bookmakers"]
                        analysis["num_bookmakers"] = len(bookmakers)
                        if bookmakers:
                            markets = bookmakers[0].get("markets", [])
                            analysis["num_markets"] = len(markets)
                            if markets:
                                analysis["market_types"] = [m["key"] for m in markets]

                                # Check for player prop markets
                                player_prop_markets = [
                                    m for m in markets
                                    if any(keyword in m["key"] for keyword in ["player", "passing", "rushing", "receiving"])
                                ]
                                analysis["has_player_props"] = len(player_prop_markets) > 0
                                if player_prop_markets:
                                    analysis["player_prop_types"] = [m["key"] for m in player_prop_markets]

        # Event detail analysis
        elif isinstance(data, dict) and "bookmakers" in data:
            analysis["event_id"] = data.get("id")
            analysis["home_team"] = data.get("home_team")
            analysis["away_team"] = data.get("away_team")

            bookmakers = data.get("bookmakers", [])
            analysis["num_bookmakers"] = len(bookmakers)

            if bookmakers:
                all_markets = []
                for bookmaker in bookmakers:
                    for market in bookmaker.get("markets", []):
                        if market["key"] not in all_markets:
                            all_markets.append(market["key"])

                analysis["all_market_types"] = all_markets
                analysis["has_player_props"] = any("player" in m or "passing" in m or "rushing" in m for m in all_markets)

        return analysis

    async def run_all_tests(self):
        """Run all Odds API endpoint tests."""

        print("\n" + "="*80)
        print("THE ODDS API RESEARCH - COMPREHENSIVE TESTING")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"API Key configured: {'Yes' if self.api_key and self.api_key != 'test' else 'No (using test key)'}")
        print("="*80)

        # Define all endpoints to test
        endpoints_to_test = [
            {
                "endpoint": "/sports",
                "description": "List of all available sports",
                "save_as": "sports_list",
                "params": {}
            },
            {
                "endpoint": "/sports/americanfootball_nfl/odds",
                "description": "NFL Game Odds (h2h, spreads, totals)",
                "save_as": "nfl_game_odds",
                "params": {
                    "regions": "us",
                    "markets": "h2h,spreads,totals",
                }
            },
            {
                "endpoint": "/sports/americanfootball_nfl/events",
                "description": "NFL Events/Games List",
                "save_as": "nfl_events",
                "params": {}
            },
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint_config in endpoints_to_test:
                result = await self.test_endpoint(
                    session,
                    endpoint_config["endpoint"],
                    endpoint_config["description"],
                    endpoint_config["save_as"],
                    endpoint_config.get("params")
                )

                self.results["endpoints_tested"].append(result)

                if result["status"] == "success":
                    self.results["successful"].append(endpoint_config["endpoint"])

                    # Track API usage
                    if "requests_remaining" in result:
                        self.results["api_usage"]["requests_remaining"] = result["requests_remaining"]
                    if "requests_used" in result:
                        self.results["api_usage"]["requests_used"] = result["requests_used"]

                else:
                    self.results["failed"].append(endpoint_config["endpoint"])

                # Small delay between requests
                await asyncio.sleep(1)

            # If we have events, test getting odds for a specific event
            events_test = next(
                (t for t in self.results["endpoints_tested"] if "events" in t["endpoint"]),
                None
            )

            if events_test and events_test["status"] == "success":
                # Load events to get an event ID
                events_file = self.samples_dir / "nfl_events.json"
                if events_file.exists():
                    with open(events_file, 'r') as f:
                        events = json.load(f)

                    if events and len(events) > 0:
                        event_id = events[0]["id"]
                        print(f"\n📍 Testing event-specific endpoint with event ID: {event_id}")

                        # Test player props endpoint (this is the critical test!)
                        player_props_result = await self.test_endpoint(
                            session,
                            f"/sports/americanfootball_nfl/events/{event_id}/odds",
                            f"Event Odds with Player Props (Event: {event_id})",
                            f"event_{event_id}_odds",
                            {
                                "regions": "us",
                                "markets": "player_pass_tds,player_pass_yds,player_rush_yds,player_receptions",
                            }
                        )

                        self.results["endpoints_tested"].append(player_props_result)

                        if player_props_result["status"] == "success":
                            self.results["successful"].append(f"/events/{event_id}/odds (player props)")
                        else:
                            self.results["failed"].append(f"/events/{event_id}/odds (player props)")

        # Generate summary
        self._generate_summary()

        # Save results
        self._save_results()

    def _generate_summary(self):
        """Generate summary of research findings."""

        total_tested = len(self.results["endpoints_tested"])
        total_success = len(self.results["successful"])
        total_failed = len(self.results["failed"])

        print("\n" + "="*80)
        print("RESEARCH SUMMARY")
        print("="*80)
        print(f"Total endpoints tested: {total_tested}")
        print(f"Successful: {total_success} ({total_success/total_tested*100:.1f}%)")
        print(f"Failed: {total_failed} ({total_failed/total_tested*100:.1f}%)")

        if self.results["api_usage"]:
            print(f"\n📊 API Usage:")
            print(f"  Requests used: {self.results['api_usage'].get('requests_used', 'Unknown')}")
            print(f"  Requests remaining: {self.results['api_usage'].get('requests_remaining', 'Unknown')}")

        print("="*80)

        if self.results["successful"]:
            print("\n✅ Successful Endpoints:")
            for endpoint in self.results["successful"]:
                print(f"  - {endpoint}")

        if self.results["failed"]:
            print("\n❌ Failed Endpoints:")
            for endpoint in self.results["failed"]:
                print(f"  - {endpoint}")

        # Key findings
        print("\n" + "="*80)
        print("KEY FINDINGS - PLAYER PROPS AVAILABILITY")
        print("="*80)

        # Check if player props are available
        player_props_found = False
        for test in self.results["endpoints_tested"]:
            if test["status"] == "success":
                analysis = test.get("analysis", {})
                if analysis.get("has_player_props"):
                    player_props_found = True
                    print(f"✅ PLAYER PROPS AVAILABLE!")
                    print(f"   Endpoint: {test['endpoint']}")
                    if analysis.get("player_prop_types"):
                        print(f"   Prop types: {', '.join(analysis['player_prop_types'])}")
                    break

        if not player_props_found:
            print("❌ PLAYER PROPS NOT FOUND")
            print("   The Odds API may not support player props, or they require different parameters")
            print("   Alternative: We may need to use PrizePicks API or scrape DraftKings")

        # Go/No-Go Recommendation
        print("\n" + "="*80)
        print("GO/NO-GO RECOMMENDATION")
        print("="*80)

        if player_props_found:
            print("🟢 GO - The Odds API provides player props")
            print("\nReasons:")
            print("  ✅ Player props available")
            print("  ✅ Multiple sportsbooks")
            print("  ✅ Real-time odds")
            self.results["recommendation"] = "GO"
        elif total_success > 0:
            print("🟡 CONDITIONAL - The Odds API works but player props not confirmed")
            print("\nReasons:")
            print("  ✅ API is functional")
            print("  ❌ Player props availability unclear")
            print("  ⚠️  May need to test different market parameters")
            print("  ⚠️  May need PrizePicks or DraftKings as alternative")
            self.results["recommendation"] = "CONDITIONAL"
        else:
            print("🔴 NO-GO - The Odds API is not accessible")
            print("\nReasons:")
            print("  ❌ API key may be invalid")
            print("  ❌ Endpoints not working")
            self.results["recommendation"] = "NO-GO"

    def _save_results(self):
        """Save research results to JSON file."""

        results_path = self.samples_dir / "research_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {results_path}")

        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("1. Review saved sample responses in samples/odds_api/")
        print("2. If player props NOT available:")
        print("   - Research PrizePicks API (already integrated in old system)")
        print("   - Consider DraftKings scraping")
        print("3. Document findings in docs/sources/ODDS_API.md")
        print("4. Calculate monthly costs based on usage")
        print("="*80 + "\n")


async def main():
    """Main entry point."""
    researcher = OddsAPIResearcher()
    await researcher.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
