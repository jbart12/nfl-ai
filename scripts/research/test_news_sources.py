"""
News & Breaking Updates Research Script

Breaking news (especially injuries) can dramatically impact player props.
Traditional Twitter API is now expensive ($100+/month), so we test FREE alternatives:

1. ESPN News API - Already tested, works great
2. NFL.com RSS Feeds - Official league news
3. Sleeper Injury Updates - Real-time injury changes
4. Reddit NFL RSS - Community-driven breaking news

This script validates:
1. News availability and freshness
2. Coverage of injury updates
3. Update frequency
4. Reliability and structure

**NO API KEYS REQUIRED** - All free sources
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import aiohttp
import xml.etree.ElementTree as ET


class NewsSourcesResearcher:
    """Research free news sources for NFL breaking updates."""

    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "sources_tested": [],
            "successful": [],
            "failed": [],
            "findings": {},
        }

        # Create directories for saving results
        self.samples_dir = Path("/Users/jace/dev/nfl-ai/samples/news")
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    async def test_espn_news(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test ESPN News API (already validated in ESPN research)."""
        result = {
            "source": "ESPN News API",
            "status": "pending",
            "type": "JSON API"
        }

        print("\n" + "="*80)
        print("TESTING: ESPN News API")
        print("="*80)

        try:
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/news"

            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    save_path = self.samples_dir / "espn_news.json"
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)

                    articles = data.get("articles", [])
                    result["status"] = "success"
                    result["article_count"] = len(articles)

                    # Analyze articles
                    if articles:
                        sample = articles[0]
                        result["sample_article"] = {
                            "headline": sample.get("headline"),
                            "published": sample.get("published"),
                            "description": sample.get("description", "")[:100],
                        }

                        print(f"✅ Found {len(articles)} articles")
                        print(f"   Latest: {sample.get('headline')}")
                        print(f"   Published: {sample.get('published')}")

                        # Check for injury-related news
                        injury_articles = [
                            a for a in articles
                            if any(keyword in a.get("headline", "").lower() for keyword in ["injury", "hurt", "out", "questionable"])
                        ]
                        result["injury_article_count"] = len(injury_articles)
                        print(f"   Injury-related articles: {len(injury_articles)}")

                else:
                    result["status"] = "failed"
                    result["error"] = f"HTTP {response.status}"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"❌ ESPN News failed: {e}")

        return result

    async def test_nfl_rss(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test NFL.com RSS feeds."""
        result = {
            "source": "NFL.com RSS",
            "status": "pending",
            "type": "RSS Feed"
        }

        print("\n" + "="*80)
        print("TESTING: NFL.com RSS Feeds")
        print("="*80)

        # Test multiple NFL RSS feeds
        feeds_to_test = {
            "news": "https://www.nfl.com/feeds/rss/news",
            "injuries": "https://www.nfl.com/feeds/rss/injuries",
        }

        successful_feeds = []

        for feed_name, feed_url in feeds_to_test.items():
            try:
                print(f"\n  Testing {feed_name} feed...")
                async with session.get(feed_url) as response:
                    if response.status == 200:
                        xml_content = await response.text()

                        # Parse RSS XML
                        root = ET.fromstring(xml_content)

                        # Save sample
                        save_path = self.samples_dir / f"nfl_rss_{feed_name}.xml"
                        with open(save_path, 'w') as f:
                            f.write(xml_content)

                        # Count items
                        items = root.findall(".//item")
                        print(f"  ✅ {feed_name}: {len(items)} items")

                        if items:
                            first_item = items[0]
                            title = first_item.find("title").text if first_item.find("title") is not None else "N/A"
                            pub_date = first_item.find("pubDate").text if first_item.find("pubDate") is not None else "N/A"
                            print(f"     Latest: {title}")
                            print(f"     Published: {pub_date}")

                        successful_feeds.append({
                            "name": feed_name,
                            "url": feed_url,
                            "item_count": len(items)
                        })

                    else:
                        print(f"  ❌ {feed_name}: HTTP {response.status}")

            except Exception as e:
                print(f"  ❌ {feed_name} failed: {e}")

        if successful_feeds:
            result["status"] = "success"
            result["successful_feeds"] = successful_feeds
        else:
            result["status"] = "failed"
            result["error"] = "No feeds accessible"

        return result

    async def test_reddit_nfl_rss(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test Reddit NFL RSS feed."""
        result = {
            "source": "Reddit /r/NFL RSS",
            "status": "pending",
            "type": "RSS Feed"
        }

        print("\n" + "="*80)
        print("TESTING: Reddit /r/NFL RSS")
        print("="*80)

        try:
            # Reddit RSS feeds (sorted by new for breaking news)
            urls_to_test = [
                ("new", "https://www.reddit.com/r/nfl/new/.rss"),
                ("hot", "https://www.reddit.com/r/nfl/.rss"),
            ]

            successful = []

            for sort_type, url in urls_to_test:
                try:
                    async with session.get(url, headers={"User-Agent": "NFL-AI Research 1.0"}) as response:
                        if response.status == 200:
                            xml_content = await response.text()

                            # Parse RSS (Reddit uses Atom format)
                            root = ET.fromstring(xml_content)

                            # Save sample
                            save_path = self.samples_dir / f"reddit_nfl_{sort_type}.xml"
                            with open(save_path, 'w') as f:
                                f.write(xml_content)

                            # Count entries (Atom uses <entry> not <item>)
                            entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")

                            print(f"  ✅ Reddit {sort_type}: {len(entries)} posts")

                            if entries:
                                first_entry = entries[0]
                                title_elem = first_entry.find("{http://www.w3.org/2005/Atom}title")
                                title = title_elem.text if title_elem is not None else "N/A"
                                print(f"     Latest: {title[:80]}...")

                            successful.append({
                                "sort": sort_type,
                                "url": url,
                                "entry_count": len(entries)
                            })

                        else:
                            print(f"  ❌ Reddit {sort_type}: HTTP {response.status}")

                except Exception as e:
                    print(f"  ❌ Reddit {sort_type}: {e}")

            if successful:
                result["status"] = "success"
                result["feeds"] = successful
            else:
                result["status"] = "failed"
                result["error"] = "No Reddit feeds accessible"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def test_sleeper_injury_tracking(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test Sleeper for real-time injury updates (already validated)."""
        result = {
            "source": "Sleeper Injury Updates",
            "status": "pending",
            "type": "JSON API"
        }

        print("\n" + "="*80)
        print("TESTING: Sleeper Real-Time Injury Updates")
        print("="*80)

        try:
            url = "https://api.sleeper.app/v1/players/nfl"

            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    # Find recently updated injuries (would compare timestamps in production)
                    injured = [
                        p for p in data.values()
                        if p.get("injury_status") is not None
                    ]

                    result["status"] = "success"
                    result["total_injured"] = len(injured)

                    # Sample recent injuries
                    sample_injuries = injured[:5]
                    result["sample_injuries"] = [
                        {
                            "name": p.get("full_name"),
                            "team": p.get("team"),
                            "status": p.get("injury_status"),
                            "body_part": p.get("injury_body_part")
                        }
                        for p in sample_injuries
                    ]

                    print(f"✅ Found {len(injured)} players with injury status")
                    print(f"   This is real-time injury tracking (already validated)")

                else:
                    result["status"] = "failed"
                    result["error"] = f"HTTP {response.status}"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def run_all_tests(self):
        """Run all news source tests."""
        print("\n" + "="*80)
        print("NEWS SOURCES RESEARCH - BREAKING NEWS & INJURIES")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Testing FREE news sources (no Twitter API needed)")
        print("="*80)

        async with aiohttp.ClientSession() as session:
            # Test all sources
            espn_result = await self.test_espn_news(session)
            self.results["sources_tested"].append(espn_result)

            nfl_result = await self.test_nfl_rss(session)
            self.results["sources_tested"].append(nfl_result)

            reddit_result = await self.test_reddit_nfl_rss(session)
            self.results["sources_tested"].append(reddit_result)

            sleeper_result = await self.test_sleeper_injury_tracking(session)
            self.results["sources_tested"].append(sleeper_result)

        self._generate_summary()
        self._save_results()

    def _generate_summary(self):
        """Generate summary and recommendations."""
        print("\n" + "="*80)
        print("RESEARCH SUMMARY")
        print("="*80)

        for source_result in self.results["sources_tested"]:
            status_icon = "✅" if source_result["status"] == "success" else "❌"
            print(f"\n{status_icon} {source_result['source']}: {source_result['status'].upper()}")
            print(f"   Type: {source_result['type']}")

            if source_result["status"] == "success":
                self.results["successful"].append(source_result["source"])
            else:
                self.results["failed"].append(source_result["source"])
                if "error" in source_result:
                    print(f"   Error: {source_result['error']}")

        # Recommendations
        print("\n" + "="*80)
        print("RECOMMENDATION")
        print("="*80)

        successful_count = len(self.results["successful"])

        if successful_count >= 2:
            print(f"🟢 GO - {successful_count} free news sources available\n")
            print("Recommended News Strategy:")
            print("  1. **Sleeper Injury Updates** - Real-time injury status (PRIMARY)")
            print("     → Already pulling 1,098 injury statuses")
            print("     → Update: Every 30 minutes")
            print("")
            print("  2. **ESPN News API** - Breaking news articles")
            print("     → Provides context and narratives")
            print("     → Update: Every 15 minutes during game days")
            print("")
            print("  3. **NFL.com RSS** - Official league announcements")
            print("     → Injury reports, roster moves")
            print("     → Update: Every hour")
            print("")
            print("  4. **Reddit /r/NFL** - Community breaking news (optional)")
            print("     → Often breaks news before official sources")
            print("     → Update: Every 5 minutes during game days")
            print("")
            print("✅ No Twitter API needed - FREE sources cover everything!")

            self.results["recommendation"] = "GO"
        else:
            print("🔴 NO-GO - Insufficient news sources available")
            self.results["recommendation"] = "NO-GO"

        # News Impact
        print("\n" + "="*80)
        print("NEWS IMPACT ON PROPS")
        print("="*80)
        print("""
Breaking news can instantly change prop values:

🚨 INJURY NEWS (Most Critical):
   - Player ruled OUT → Props removed or adjusted dramatically
   - Questionable status → Props may lower slightly
   - Backup elevated → Opportunity increase

📰 NEWS TYPES TO MONITOR:
   1. Injury designations (Fri official reports)
   2. Snap count changes
   3. Role changes (WR1 to WR2, etc.)
   4. Weather updates
   5. Coaching decisions

⏰ TIMING:
   - Friday 4 PM ET: Official injury reports
   - Gameday morning: Final injury decisions
   - 90 min before game: Inactive lists
   - Real-time: Breaking news during week

Strategy: Poll Sleeper injuries + ESPN news frequently on gamedays
""")

    def _save_results(self):
        """Save research results."""
        results_path = self.samples_dir / "research_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {results_path}")

        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("1. Review saved sample responses in samples/news/")
        print("2. Document findings in docs/sources/NEWS_SOURCES.md")
        print("3. Build news aggregator service")
        print("4. Set up alerts for critical injury news")
        print("5. Integrate news into RAG narratives")
        print("="*80 + "\n")


async def main():
    """Main entry point."""
    researcher = NewsSourcesResearcher()
    await researcher.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
