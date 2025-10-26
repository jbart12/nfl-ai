"""
NFL Official Stats & Next Gen Stats Research Script

Tests official NFL data sources:
1. NFL.com API (if available)
2. Next Gen Stats (NGS) - Advanced metrics
3. NFL Fantasy API
4. NFL Game Stats API

Next Gen Stats provides:
- Player tracking data
- Route running metrics
- Separation metrics
- Pressure rate
- Target separation
- Time to throw

**Mostly FREE** - Some advanced features may require NFL Game Pass
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import aiohttp


class NFLOfficialStatsResearcher:
    """Research NFL official stats sources."""

    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "sources_tested": [],
            "successful": [],
            "failed": [],
            "findings": {},
        }

        self.samples_dir = Path("/Users/jace/dev/nfl-ai/samples/nfl_official")
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    async def test_nfl_stats_api(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test NFL.com stats API."""
        result = {
            "source": "NFL.com Stats API",
            "status": "pending",
            "endpoints_tested": []
        }

        print("\n" + "="*80)
        print("TESTING: NFL.com Stats API")
        print("="*80)

        # Known NFL.com API endpoints
        endpoints = [
            ("stats", "https://api.nfl.com/v1/stats"),
            ("teams", "https://api.nfl.com/v1/teams"),
            ("players", "https://api.nfl.com/v1/players"),
        ]

        for name, url in endpoints:
            try:
                print(f"\n  Testing {name} endpoint...")
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    result["endpoints_tested"].append({
                        "name": name,
                        "url": url,
                        "status": resp.status
                    })

                    if resp.status == 200:
                        data = await resp.json()
                        save_path = self.samples_dir / f"nfl_api_{name}.json"
                        with open(save_path, 'w') as f:
                            json.dump(data, f, indent=2)
                        print(f"  ✅ {name}: Success")
                    else:
                        print(f"  ❌ {name}: HTTP {resp.status}")

            except Exception as e:
                print(f"  ❌ {name}: {e}")
                result["endpoints_tested"].append({
                    "name": name,
                    "url": url,
                    "error": str(e)
                })

        successful = [e for e in result["endpoints_tested"] if e.get("status") == 200]
        result["status"] = "success" if successful else "failed"

        return result

    async def test_next_gen_stats(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test Next Gen Stats API."""
        result = {
            "source": "Next Gen Stats",
            "status": "pending",
            "endpoints_tested": []
        }

        print("\n" + "="*80)
        print("TESTING: Next Gen Stats (NGS)")
        print("="*80)

        # Next Gen Stats is embedded in NFL.com
        # Try accessing public NGS data
        ngs_endpoints = [
            ("passing", "https://nextgenstats.nfl.com/api/statboard/passing"),
            ("rushing", "https://nextgenstats.nfl.com/api/statboard/rushing"),
            ("receiving", "https://nextgenstats.nfl.com/api/statboard/receiving"),
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://nextgenstats.nfl.com/'
        }

        for name, url in ngs_endpoints:
            try:
                print(f"\n  Testing {name} stats...")
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    result["endpoints_tested"].append({
                        "name": name,
                        "url": url,
                        "status": resp.status
                    })

                    if resp.status == 200:
                        data = await resp.json()
                        save_path = self.samples_dir / f"ngs_{name}.json"
                        with open(save_path, 'w') as f:
                            json.dump(data, f, indent=2)

                        # Analyze NGS data
                        if isinstance(data, list) and data:
                            print(f"  ✅ {name}: {len(data)} players")
                            sample = data[0]
                            print(f"     Sample keys: {list(sample.keys())[:5]}")
                        else:
                            print(f"  ✅ {name}: Success (structure unknown)")

                    else:
                        print(f"  ❌ {name}: HTTP {resp.status}")

            except Exception as e:
                print(f"  ❌ {name}: {e}")

        successful = [e for e in result["endpoints_tested"] if e.get("status") == 200]
        result["status"] = "success" if successful else "failed"

        return result

    async def test_nfl_fantasy_api(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test NFL Fantasy API."""
        result = {
            "source": "NFL Fantasy API",
            "status": "pending"
        }

        print("\n" + "="*80)
        print("TESTING: NFL Fantasy API")
        print("="*80)

        try:
            # NFL Fantasy often uses fantasy.nfl.com
            url = "https://fantasy.nfl.com/api/v1/players/stats"

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    save_path = self.samples_dir / "nfl_fantasy_stats.json"
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    print("  ✅ NFL Fantasy API accessible")
                    result["status"] = "success"
                else:
                    print(f"  ❌ NFL Fantasy API: HTTP {resp.status}")
                    result["status"] = "failed"

        except Exception as e:
            print(f"  ❌ NFL Fantasy API: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def run_all_tests(self):
        """Run all NFL official stats tests."""
        print("\n" + "="*80)
        print("NFL OFFICIAL STATS RESEARCH")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        async with aiohttp.ClientSession() as session:
            # Test all sources
            nfl_api_result = await self.test_nfl_stats_api(session)
            self.results["sources_tested"].append(nfl_api_result)

            ngs_result = await self.test_next_gen_stats(session)
            self.results["sources_tested"].append(ngs_result)

            fantasy_result = await self.test_nfl_fantasy_api(session)
            self.results["sources_tested"].append(fantasy_result)

        self._generate_summary()
        self._save_results()

    def _generate_summary(self):
        """Generate summary."""
        print("\n" + "="*80)
        print("RESEARCH SUMMARY")
        print("="*80)

        for source in self.results["sources_tested"]:
            status_icon = "✅" if source["status"] == "success" else "❌"
            print(f"\n{status_icon} {source['source']}: {source['status'].upper()}")

            if source["status"] == "success":
                self.results["successful"].append(source["source"])
                if "endpoints_tested" in source:
                    successful_endpoints = [e for e in source["endpoints_tested"] if e.get("status") == 200]
                    print(f"   Successful endpoints: {len(successful_endpoints)}")
            else:
                self.results["failed"].append(source["source"])

        print("\n" + "="*80)
        print("RECOMMENDATION")
        print("="*80)

        if self.results["successful"]:
            print(f"🟢 GO - {len(self.results['successful'])} official NFL source(s) available\n")
            print("Next Gen Stats Value:")
            print("  - Player tracking data (speed, separation)")
            print("  - Route running metrics")
            print("  - Pressure rate for QBs")
            print("  - Target separation for WRs")
            print("  - Advanced rushing metrics")
            self.results["recommendation"] = "GO"
        else:
            print("🟡 CONDITIONAL - Official NFL APIs may require authentication")
            print("Alternative: Scrape NFL.com stats pages or use ESPN advanced stats")
            self.results["recommendation"] = "CONDITIONAL"

    def _save_results(self):
        """Save results."""
        results_path = self.samples_dir / "research_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {results_path}\n")


async def main():
    """Main entry point."""
    researcher = NFLOfficialStatsResearcher()
    await researcher.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
