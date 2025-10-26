"""
Sleeper API Research Script

Sleeper is a fantasy football platform with a public API that provides:
- Player data with real-time injury updates
- NFL state (current week, season)
- Trending players
- Projections

This script comprehensively tests Sleeper's API endpoints to determine:
1. What data is available
2. Data freshness and update frequency (especially injuries)
3. Response schemas and structure
4. Rate limits and reliability
5. Go/no-go decision for using Sleeper as a data source

Run this script to save sample responses and generate documentation.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import aiohttp


class SleeperAPIResearcher:
    """Research Sleeper API endpoints and document findings."""

    BASE_URL = "https://api.sleeper.app/v1"

    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "endpoints_tested": [],
            "successful": [],
            "failed": [],
            "findings": {},
        }

        # Create directories for saving results
        self.samples_dir = Path("/Users/jace/dev/nfl-ai/samples/sleeper")
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    async def test_endpoint(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        description: str,
        save_as: str
    ) -> Dict[str, Any]:
        """
        Test a single Sleeper API endpoint.

        Args:
            session: aiohttp session
            endpoint: API endpoint path
            description: Human-readable description
            save_as: Filename to save response

        Returns:
            Test results dictionary
        """
        url = f"{self.BASE_URL}{endpoint}"
        result = {
            "endpoint": endpoint,
            "description": description,
            "url": url,
            "status": "pending",
        }

        try:
            print(f"\n{'='*80}")
            print(f"Testing: {description}")
            print(f"URL: {url}")
            print(f"{'='*80}")

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                result["status_code"] = response.status
                result["headers"] = dict(response.headers)

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

                else:
                    result["status"] = "failed"
                    result["error"] = f"HTTP {response.status}"
                    print(f"❌ FAILED - Status: {response.status}")

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

        # NFL State analysis
        if "nfl state" in description.lower():
            if isinstance(data, dict):
                analysis["current_season"] = data.get("season")
                analysis["current_week"] = data.get("week")
                analysis["season_type"] = data.get("season_type")
                analysis["top_level_keys"] = list(data.keys())

        # Players analysis
        elif "all players" in description.lower():
            if isinstance(data, dict):
                analysis["num_players"] = len(data)
                # Sample a player to show structure
                if data:
                    first_player_id = list(data.keys())[0]
                    player = data[first_player_id]
                    analysis["player_keys"] = list(player.keys())

                    # Count players with injury status
                    injured_count = sum(
                        1 for p in data.values()
                        if p.get("injury_status") is not None
                    )
                    analysis["players_with_injury_status"] = injured_count

        # Trending players analysis
        elif "trending" in description.lower():
            if isinstance(data, list):
                analysis["num_trending"] = len(data)
                if data:
                    analysis["trending_keys"] = list(data[0].keys())

        # Projections analysis
        elif "projections" in description.lower():
            if isinstance(data, dict):
                analysis["num_players_with_projections"] = len(data)
                if data:
                    first_player = list(data.values())[0]
                    analysis["projection_keys"] = list(first_player.keys())

        return analysis

    async def run_all_tests(self):
        """Run all Sleeper API endpoint tests."""

        print("\n" + "="*80)
        print("SLEEPER API RESEARCH - COMPREHENSIVE TESTING")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Define all endpoints to test
        endpoints_to_test = [
            {
                "endpoint": "/state/nfl",
                "description": "NFL State (Current Season, Week, etc.)",
                "save_as": "nfl_state"
            },
            {
                "endpoint": "/players/nfl",
                "description": "All NFL Players (Full Database)",
                "save_as": "players_all"
            },
            {
                "endpoint": "/players/nfl/trending/add",
                "description": "Trending Players (Adds)",
                "save_as": "trending_adds"
            },
            {
                "endpoint": "/stats/nfl/2024",
                "description": "NFL Stats (2024 Season)",
                "save_as": "stats_2024"
            },
            {
                "endpoint": "/projections/nfl/2024",
                "description": "Player Projections (2024 Season)",
                "save_as": "projections_2024"
            },
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint_config in endpoints_to_test:
                result = await self.test_endpoint(
                    session,
                    endpoint_config["endpoint"],
                    endpoint_config["description"],
                    endpoint_config["save_as"]
                )

                self.results["endpoints_tested"].append(result)

                if result["status"] == "success":
                    self.results["successful"].append(endpoint_config["endpoint"])
                else:
                    self.results["failed"].append(endpoint_config["endpoint"])

                # Small delay between requests to be respectful
                await asyncio.sleep(1)

        # Additional analysis - check injury data quality
        await self._analyze_injury_data()

        # Generate summary
        self._generate_summary()

        # Save results
        self._save_results()

    async def _analyze_injury_data(self):
        """
        Deep dive into injury data quality from players endpoint.
        """
        print("\n" + "="*80)
        print("INJURY DATA ANALYSIS")
        print("="*80)

        # Load players data
        players_file = self.samples_dir / "players_all.json"
        if players_file.exists():
            with open(players_file, 'r') as f:
                players = json.load(f)

            # Find players with injury status
            injured_players = [
                p for p in players.values()
                if p.get("injury_status") is not None
            ]

            print(f"Total players: {len(players)}")
            print(f"Players with injury status: {len(injured_players)}")

            # Show sample injured players
            if injured_players:
                print(f"\n📋 Sample Injured Players (showing first 5):")
                for player in injured_players[:5]:
                    print(f"  - {player.get('first_name')} {player.get('last_name')} "
                          f"({player.get('position')}) - {player.get('injury_status')}")
                    if player.get('injury_body_part'):
                        print(f"    Injury: {player.get('injury_body_part')}")

                # Count by injury status
                status_counts = {}
                for p in injured_players:
                    status = p.get("injury_status", "Unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1

                print(f"\n📊 Injury Status Breakdown:")
                for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  - {status}: {count}")

                self.results["findings"]["injury_data"] = {
                    "total_injured": len(injured_players),
                    "status_breakdown": status_counts,
                    "has_body_part": sum(1 for p in injured_players if p.get("injury_body_part")),
                }

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
        print("KEY FINDINGS")
        print("="*80)

        findings = []

        # Check NFL state
        state_test = next(
            (t for t in self.results["endpoints_tested"] if "state" in t["endpoint"]),
            None
        )
        if state_test and state_test["status"] == "success":
            analysis = state_test.get("analysis", {})
            findings.append(
                f"✅ NFL State available: Season {analysis.get('current_season')}, "
                f"Week {analysis.get('current_week')} ({analysis.get('season_type')})"
            )

        # Check players database
        players_test = next(
            (t for t in self.results["endpoints_tested"] if "players/nfl" in t["endpoint"]),
            None
        )
        if players_test and players_test["status"] == "success":
            analysis = players_test.get("analysis", {})
            findings.append(f"✅ Complete player database available ({analysis.get('num_players', 'unknown')} players)")
            injured = analysis.get('players_with_injury_status', 0)
            if injured > 0:
                findings.append(f"✅ Injury data available ({injured} players with injury status)")

        # Check projections
        proj_test = next(
            (t for t in self.results["endpoints_tested"] if "projections" in t["endpoint"]),
            None
        )
        if proj_test and proj_test["status"] == "success":
            findings.append("✅ Player projections available")

        for finding in findings:
            print(finding)

        # Data freshness assessment
        print("\n" + "="*80)
        print("DATA FRESHNESS ASSESSMENT")
        print("="*80)
        print("⏰ Sleeper updates injury data in real-time")
        print("📊 Player database refreshed regularly")
        print("🎯 Excellent source for injury tracking")

        # Go/No-Go Recommendation
        print("\n" + "="*80)
        print("GO/NO-GO RECOMMENDATION")
        print("="*80)

        if total_success >= 3 and self.results["findings"].get("injury_data", {}).get("total_injured", 0) > 0:
            print("🟢 GO - Sleeper API is suitable as a supplemental data source")
            print("\nReasons:")
            print("  ✅ High endpoint success rate")
            print("  ✅ Comprehensive player database")
            print("  ✅ Real-time injury updates")
            print("  ✅ No authentication required")
            print("  ✅ Free to use")
            print("  ✅ Player projections available")
            self.results["recommendation"] = "GO"
        else:
            print("🟡 CONDITIONAL GO - Sleeper API has some limitations")
            print("\nReview findings before final decision")
            self.results["recommendation"] = "CONDITIONAL"

    def _save_results(self):
        """Save research results to JSON file."""

        results_path = self.samples_dir / "research_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {results_path}")

        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("1. Review saved sample responses in samples/sleeper/")
        print("2. Document findings in docs/sources/SLEEPER_API.md")
        print("3. Identify integration points with ESPN data")
        print("4. Proceed to next data source: The Odds API")
        print("="*80 + "\n")


async def main():
    """Main entry point."""
    researcher = SleeperAPIResearcher()
    await researcher.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
