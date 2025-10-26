"""
Analytics & Reference Sites Research Script

Tests comprehensive list of analytics and reference sites:

TIER 2 (Important Analytics):
- Pro Football Reference (PFR) - Historical stats
- Football Outsiders - DVOA, advanced metrics
- Sharp Football Stats - Betting analytics
- FantasyPros - Projections & rankings
- RotoWire - News & analysis
- FantasyData - Projections API

TIER 3 (Supplemental):
- Action Network - Betting trends
- TeamRankings - Statistical analysis
- NumberFire - Projections
- PlayerProfiler - Advanced metrics
- 4for4 - Fantasy analysis
- Football Perspective - Analytics blog
- FiveThirtyEight - Elo ratings

Tests which have:
1. Public APIs (JSON)
2. RSS feeds
3. Scrapable data pages
4. Require paid subscriptions
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import aiohttp
import xml.etree.ElementTree as ET


class AnalyticsSitesResearcher:
    """Research analytics and reference sites comprehensively."""

    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "sources_tested": [],
            "successful": [],
            "failed": [],
            "scrape_only": [],
            "requires_auth": [],
            "findings": {},
        }

        self.samples_dir = Path("/Users/jace/dev/nfl-ai/samples/analytics")
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    async def test_pro_football_reference(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test Pro Football Reference."""
        result = {
            "source": "Pro Football Reference",
            "tier": 2,
            "status": "pending"
        }

        print("\n" + "="*80)
        print("TESTING: Pro Football Reference (PFR)")
        print("="*80)

        try:
            # PFR doesn't have a public API, but has structured HTML
            # Test accessing a stats page
            url = "https://www.pro-football-reference.com/years/2024/passing.htm"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    result["status"] = "scrape_only"
                    result["access_method"] = "HTML scraping"
                    result["note"] = "No public API - must scrape HTML tables"
                    print("  ✅ PFR accessible via scraping")
                    print("     - Has comprehensive historical stats")
                    print("     - HTML table format (requires parsing)")
                    print("     - Consider for historical context only")
                else:
                    result["status"] = "failed"
                    print(f"  ❌ PFR: HTTP {resp.status}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"  ❌ PFR: {e}")

        return result

    async def test_football_outsiders(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test Football Outsiders (DVOA stats)."""
        result = {
            "source": "Football Outsiders",
            "tier": 2,
            "status": "pending"
        }

        print("\n" + "="*80)
        print("TESTING: Football Outsiders (DVOA)")
        print("="*80)

        try:
            # Football Outsiders has DVOA stats
            url = "https://www.footballoutsiders.com/stats/nfl/team-offense/2024"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    result["status"] = "scrape_only"
                    result["access_method"] = "HTML scraping or paid API"
                    result["note"] = "DVOA metrics valuable but may require subscription"
                    print("  ✅ Football Outsiders accessible")
                    print("     - DVOA (Defense-adjusted Value Over Average)")
                    print("     - May require paid subscription for full access")
                else:
                    result["status"] = "failed"
                    print(f"  ❌ Football Outsiders: HTTP {resp.status}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"  ❌ Football Outsiders: {e}")

        return result

    async def test_fantasypros(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test FantasyPros API."""
        result = {
            "source": "FantasyPros",
            "tier": 2,
            "status": "pending"
        }

        print("\n" + "="*80)
        print("TESTING: FantasyPros")
        print("="*80)

        try:
            # FantasyPros has a public API for projections
            url = "https://api.fantasypros.com/v2/json/nfl/2024/consensus-rankings"

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    save_path = self.samples_dir / "fantasypros_rankings.json"
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    result["status"] = "success"
                    print("  ✅ FantasyPros API accessible")
                    print("     - Consensus rankings available")
                elif resp.status == 401 or resp.status == 403:
                    result["status"] = "requires_auth"
                    result["note"] = "Requires API key"
                    print("  ⚠️  FantasyPros: Requires API key")
                else:
                    result["status"] = "failed"
                    print(f"  ❌ FantasyPros: HTTP {resp.status}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"  ❌ FantasyPros: {e}")

        return result

    async def test_rotowire(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test RotoWire."""
        result = {
            "source": "RotoWire",
            "tier": 2,
            "status": "pending"
        }

        print("\n" + "="*80)
        print("TESTING: RotoWire")
        print("="*80)

        try:
            # RotoWire has RSS feeds for news
            url = "https://www.rotowire.com/rss/news.php?sport=NFL"

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    xml_content = await resp.text()
                    root = ET.fromstring(xml_content)
                    items = root.findall(".//item")

                    save_path = self.samples_dir / "rotowire_news.xml"
                    with open(save_path, 'w') as f:
                        f.write(xml_content)

                    result["status"] = "success"
                    result["access_method"] = "RSS feed"
                    print(f"  ✅ RotoWire RSS: {len(items)} news items")
                else:
                    result["status"] = "failed"
                    print(f"  ❌ RotoWire: HTTP {resp.status}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"  ❌ RotoWire: {e}")

        return result

    async def test_action_network(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test Action Network (betting analytics)."""
        result = {
            "source": "Action Network",
            "tier": 3,
            "status": "pending"
        }

        print("\n" + "="*80)
        print("TESTING: Action Network (Betting Trends)")
        print("="*80)

        try:
            # Action Network may have public endpoints
            url = "https://api.actionnetwork.com/web/v1/leagues/9/games"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    save_path = self.samples_dir / "action_network_games.json"
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    result["status"] = "success"
                    print("  ✅ Action Network API accessible")
                elif resp.status == 401:
                    result["status"] = "requires_auth"
                    print("  ⚠️  Action Network: Requires authentication")
                else:
                    result["status"] = "failed"
                    print(f"  ❌ Action Network: HTTP {resp.status}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"  ❌ Action Network: {e}")

        return result

    async def test_fivethirtyeight(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test FiveThirtyEight NFL Elo ratings."""
        result = {
            "source": "FiveThirtyEight",
            "tier": 3,
            "status": "pending"
        }

        print("\n" + "="*80)
        print("TESTING: FiveThirtyEight (Elo Ratings)")
        print("="*80)

        try:
            # FiveThirtyEight publishes data on GitHub
            url = "https://projects.fivethirtyeight.com/nfl-api/nfl_elo_latest.csv"

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    csv_content = await resp.text()
                    save_path = self.samples_dir / "fivethirtyeight_elo.csv"
                    with open(save_path, 'w') as f:
                        f.write(csv_content)
                    result["status"] = "success"
                    result["access_method"] = "CSV file"
                    print("  ✅ FiveThirtyEight Elo ratings available")
                    print("     - Team strength ratings")
                    print("     - Game predictions")
                else:
                    result["status"] = "failed"
                    print(f"  ❌ FiveThirtyEight: HTTP {resp.status}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"  ❌ FiveThirtyEight: {e}")

        return result

    async def test_teamrankings(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test TeamRankings."""
        result = {
            "source": "TeamRankings",
            "tier": 3,
            "status": "pending"
        }

        print("\n" + "="*80)
        print("TESTING: TeamRankings")
        print("="*80)

        try:
            url = "https://www.teamrankings.com/nfl/stats/"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    result["status"] = "scrape_only"
                    result["access_method"] = "HTML scraping"
                    print("  ✅ TeamRankings accessible via scraping")
                    print("     - Statistical rankings")
                    print("     - Betting trends")
                else:
                    result["status"] = "failed"
                    print(f"  ❌ TeamRankings: HTTP {resp.status}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"  ❌ TeamRankings: {e}")

        return result

    async def run_all_tests(self):
        """Run all analytics site tests."""
        print("\n" + "="*80)
        print("ANALYTICS & REFERENCE SITES RESEARCH")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing {7} analytics sources")
        print("="*80)

        async with aiohttp.ClientSession() as session:
            # Test TIER 2 sources
            pfr_result = await self.test_pro_football_reference(session)
            self.results["sources_tested"].append(pfr_result)

            fo_result = await self.test_football_outsiders(session)
            self.results["sources_tested"].append(fo_result)

            fp_result = await self.test_fantasypros(session)
            self.results["sources_tested"].append(fp_result)

            rw_result = await self.test_rotowire(session)
            self.results["sources_tested"].append(rw_result)

            # Test TIER 3 sources
            an_result = await self.test_action_network(session)
            self.results["sources_tested"].append(an_result)

            fte_result = await self.test_fivethirtyeight(session)
            self.results["sources_tested"].append(fte_result)

            tr_result = await self.test_teamrankings(session)
            self.results["sources_tested"].append(tr_result)

        self._generate_summary()
        self._save_results()

    def _generate_summary(self):
        """Generate summary."""
        print("\n" + "="*80)
        print("RESEARCH SUMMARY")
        print("="*80)

        # Categorize results
        for source in self.results["sources_tested"]:
            status = source["status"]
            source_name = source["source"]

            if status == "success":
                self.results["successful"].append(source_name)
                print(f"✅ {source_name}: API/Feed available")
            elif status == "scrape_only":
                self.results["scrape_only"].append(source_name)
                print(f"⚠️  {source_name}: Scraping only")
            elif status == "requires_auth":
                self.results["requires_auth"].append(source_name)
                print(f"🔐 {source_name}: Requires authentication")
            else:
                self.results["failed"].append(source_name)
                print(f"❌ {source_name}: Not accessible")

        # Recommendation
        print("\n" + "="*80)
        print("RECOMMENDATION")
        print("="*80)

        api_sources = len(self.results["successful"])
        scrape_sources = len(self.results["scrape_only"])
        auth_sources = len(self.results["requires_auth"])

        print(f"\n📊 Results:")
        print(f"  - API/Feed accessible: {api_sources}")
        print(f"  - Scraping required: {scrape_sources}")
        print(f"  - Requires auth: {auth_sources}")

        if api_sources > 0:
            print(f"\n🟢 GO - {api_sources} analytics source(s) with API/feed access")
            print("\nPriority Integration:")
            for source_name in self.results["successful"]:
                source_data = next(s for s in self.results["sources_tested"] if s["source"] == source_name)
                print(f"  ✅ {source_name} (TIER {source_data.get('tier', '?')})")
        else:
            print("\n🟡 CONDITIONAL - Most sources require scraping or authentication")

        print("\nScraping Options (if needed):")
        for source_name in self.results["scrape_only"]:
            print(f"  ⚠️  {source_name} - Consider for Phase 2")

    def _save_results(self):
        """Save results."""
        results_path = self.samples_dir / "research_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {results_path}\n")


async def main():
    """Main entry point."""
    researcher = AnalyticsSitesResearcher()
    await researcher.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
