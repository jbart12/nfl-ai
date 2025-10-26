"""
Remaining Sources Research Script

Final comprehensive test of all remaining fantasy, betting, and analytics sources:

Remaining TIER 2/3 Sources:
- Sharp Football Stats
- FantasyData
- Pro Football Focus (PFF)
- Vegas Insider
- NumberFire
- PlayerProfiler
- 4for4
- Stathead (Sports Reference)
- DraftKings/BetMGM (sportsbooks)

Tests availability, access methods, and data quality.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import aiohttp


class RemainingSourcesResearcher:
    """Test all remaining NFL data sources."""

    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "sources_tested": [],
            "successful": [],
            "failed": [],
            "scrape_only": [],
            "requires_paid": [],
        }

        self.samples_dir = Path("/Users/jace/dev/nfl-ai/samples/remaining")
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    async def test_source(
        self,
        session: aiohttp.ClientSession,
        name: str,
        url: str,
        tier: int,
        test_type: str = "api"
    ) -> Dict[str, Any]:
        """Generic source tester."""
        result = {
            "source": name,
            "tier": tier,
            "url": url,
            "test_type": test_type,
            "status": "pending"
        }

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json' if test_type == "api" else 'text/html'
            }

            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                result["status_code"] = resp.status

                if resp.status == 200:
                    if test_type == "api":
                        try:
                            data = await resp.json()
                            save_path = self.samples_dir / f"{name.lower().replace(' ', '_')}.json"
                            with open(save_path, 'w') as f:
                                json.dump(data, f, indent=2)
                            result["status"] = "success"
                            result["access_method"] = "API"
                        except:
                            result["status"] = "scrape_only"
                            result["access_method"] = "HTML"
                    else:
                        result["status"] = "scrape_only"
                        result["access_method"] = "HTML scraping"

                elif resp.status in [401, 403]:
                    result["status"] = "requires_auth"
                    result["note"] = "Authentication required"

                elif resp.status == 402:
                    result["status"] = "requires_paid"
                    result["note"] = "Paid subscription required"

                else:
                    result["status"] = "failed"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def run_all_tests(self):
        """Test all remaining sources."""
        print("\n" + "="*80)
        print("REMAINING SOURCES COMPREHENSIVE RESEARCH")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Testing all remaining fantasy, betting, and analytics sources")
        print("="*80)

        sources_to_test = [
            # TIER 2
            {
                "name": "Sharp Football Stats",
                "url": "https://www.sharpfootballstats.com/",
                "tier": 2,
                "type": "html"
            },
            {
                "name": "FantasyData",
                "url": "https://api.sportsdata.io/v3/nfl/stats/json/Players",
                "tier": 2,
                "type": "api"
            },
            {
                "name": "Pro Football Focus",
                "url": "https://www.pff.com/nfl/grades",
                "tier": 2,
                "type": "html"
            },
            # TIER 3
            {
                "name": "Vegas Insider",
                "url": "https://www.vegasinsider.com/nfl/odds/",
                "tier": 3,
                "type": "html"
            },
            {
                "name": "NumberFire",
                "url": "https://www.numberfire.com/nfl/players/stats",
                "tier": 3,
                "type": "html"
            },
            {
                "name": "PlayerProfiler",
                "url": "https://www.playerprofiler.com/nfl/",
                "tier": 3,
                "type": "html"
            },
            {
                "name": "4for4",
                "url": "https://www.4for4.com/fantasy-football/rankings",
                "tier": 3,
                "type": "html"
            },
            {
                "name": "Stathead",
                "url": "https://stathead.com/football/",
                "tier": 3,
                "type": "html"
            },
            {
                "name": "DraftKings Sportsbook",
                "url": "https://sportsbook.draftkings.com/leagues/football/nfl",
                "tier": 3,
                "type": "html"
            },
            {
                "name": "Football Perspective",
                "url": "https://www.footballperspective.com/",
                "tier": 3,
                "type": "html"
            },
        ]

        async with aiohttp.ClientSession() as session:
            for source_config in sources_to_test:
                print(f"\n{'='*80}")
                print(f"Testing: {source_config['name']} (TIER {source_config['tier']})")
                print(f"{'='*80}")

                result = await self.test_source(
                    session,
                    source_config["name"],
                    source_config["url"],
                    source_config["tier"],
                    source_config["type"]
                )

                self.results["sources_tested"].append(result)

                # Print result
                status_emoji = {
                    "success": "✅",
                    "scrape_only": "⚠️ ",
                    "requires_auth": "🔐",
                    "requires_paid": "💰",
                    "failed": "❌"
                }.get(result["status"], "❓")

                print(f"{status_emoji} {result['source']}: {result['status'].upper()}")
                if "access_method" in result:
                    print(f"   Access: {result['access_method']}")
                if "note" in result:
                    print(f"   Note: {result['note']}")

                # Small delay
                await asyncio.sleep(0.5)

        self._generate_summary()
        self._save_results()

    def _generate_summary(self):
        """Generate comprehensive summary."""
        print("\n" + "="*80)
        print("COMPREHENSIVE RESEARCH SUMMARY")
        print("="*80)

        # Categorize
        for source in self.results["sources_tested"]:
            status = source["status"]
            name = source["source"]

            if status == "success":
                self.results["successful"].append(name)
            elif status == "scrape_only":
                self.results["scrape_only"].append(name)
            elif status == "requires_paid":
                self.results["requires_paid"].append(name)
            else:
                self.results["failed"].append(name)

        # Print categorized results
        print(f"\n📊 Results Breakdown:")
        print(f"  ✅ API Accessible: {len(self.results['successful'])}")
        print(f"  ⚠️  Scraping Required: {len(self.results['scrape_only'])}")
        print(f"  💰 Paid Subscription: {len(self.results['requires_paid'])}")
        print(f"  ❌ Not Accessible: {len(self.results['failed'])}")

        if self.results["successful"]:
            print(f"\n✅ API Accessible Sources:")
            for name in self.results["successful"]:
                source = next(s for s in self.results["sources_tested"] if s["source"] == name)
                print(f"  - {name} (TIER {source['tier']})")

        if self.results["scrape_only"]:
            print(f"\n⚠️  Scraping Required (consider for Phase 2):")
            for name in self.results["scrape_only"]:
                source = next(s for s in self.results["sources_tested"] if s["source"] == name)
                print(f"  - {name} (TIER {source['tier']})")

        if self.results["requires_paid"]:
            print(f"\n💰 Requires Paid Subscription:")
            for name in self.results["requires_paid"]:
                print(f"  - {name}")

        print("\n" + "="*80)
        print("FINAL RECOMMENDATION")
        print("="*80)

        api_count = len(self.results["successful"])

        if api_count > 0:
            print(f"🟢 GO - {api_count} additional source(s) with API access")
            print("\nIntegrate these sources as supplemental data")
        else:
            print("🟡 CONDITIONAL - No free APIs, but scraping options available")
            print("\nMost premium sources require paid subscriptions")
            print("Consider scraping if additional data needed in Phase 2")

    def _save_results(self):
        """Save results."""
        results_path = self.samples_dir / "research_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {results_path}\n")


async def main():
    """Main entry point."""
    researcher = RemainingSourcesResearcher()
    await researcher.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
