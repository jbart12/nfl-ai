# NFL RAG+AI Prop Prediction System - Master Plan

**Created**: October 26, 2025
**Project**: Fresh start RAG-powered prop prediction system using Claude AI
**Status**: Phase 0 - Data Source Research

---

## Executive Summary

Building a **Retrieval-Augmented Generation (RAG) system** that combines:
1. **Vector database (Qdrant)** with comprehensive NFL context (player narratives, situational data, historical patterns)
2. **Claude API** for intelligent reasoning over retrieved context
3. **Hybrid approach**: Structured stats + unstructured context (RAG) + AI reasoning (Claude)

**Expected Impact**: 30-50% improvement in prediction accuracy by adding contextual intelligence that pure statistics miss.

**Key Principles**:
- ✅ **Data accuracy is #1 priority** - Real-time, validated, fresh data
- ✅ **Research before building** - Validate all data sources first
- ✅ **Separate codebase** - Clean slate, no legacy constraints
- ✅ **Cost-effective** - Use free tools where possible (Qdrant), optimize Claude usage

---

## Architecture Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Vector DB** | Qdrant | Free, Python-native, production-ready |
| **Structured DB** | PostgreSQL | Reliable, proven for structured data |
| **AI Reasoning** | Claude 3.5 Sonnet | Best reasoning, cost-effective |
| **Embeddings** | OpenAI text-embedding-3-large | High quality, affordable |
| **Backend** | FastAPI + Python 3.11 | Async, modern, fast |
| **Data Updates** | 15-30 min polling | Real-time enough, cost-effective |
| **AI Strategy** | Hybrid (60% rules, 40% Claude) | Cost optimization |

---

## Current Phase: Phase 0 - Data Source Research

**Duration**: 1-2 weeks
**Goal**: Research and validate EVERY data source before building
**Status**: Planning complete, ready to execute

### Research Approach

For each data source, we will:
1. Make real API calls
2. Document exact response schemas
3. Save sample JSON responses
4. Test rate limits
5. Verify data quality
6. Assess uniqueness/value
7. Make go/no-go decision
8. Plan integration strategy

---

## Data Sources to Research (28 Total)

### TIER 1: Critical - Must Have ⭐⭐⭐⭐⭐

| # | Source | Purpose | Access | Cost | Priority |
|---|--------|---------|--------|------|----------|
| 1 | **ESPN API** | Player stats, injuries, games | API | FREE | 🔴 Day 1-2 |
| 2 | **Sleeper API** | Real-time injuries, projections | API | FREE | 🔴 Day 3 |
| 3 | **The Odds API** | Betting lines, prop odds | API | $25/mo | 🔴 Day 4 |
| 4 | **Twitter API v2** | Breaking injury news | API | $100/mo | 🟡 Day 5 |
| 5 | **Weather.com API** | Game conditions | API | FREE tier | 🟡 Day 6 |
| 6 | **NFL.com Official** | Official injury reports | Scrape | FREE | 🟡 Day 7 |

**Critical Questions**:
- ✅ ESPN: Do we get play-by-play? Practice participation?
- ✅ Sleeper: How fast are injury updates?
- 🚨 **Odds API: Does it have player props or just game lines?**
- ✅ Twitter: Is $100/mo worth it vs RSS feeds?

### TIER 2: Important - High Value ⭐⭐⭐⭐

| # | Source | Purpose | Access | Cost | Priority |
|---|--------|---------|--------|------|----------|
| 7 | **Next Gen Stats** | Player tracking, routes | Scrape | FREE | 🟡 Day 8 |
| 8 | **Pro Football Focus** | Player grades, coverage | API/Scrape | $40/mo | 🟡 Day 8-9 |
| 9 | **FantasyData API** | Projections, news | API | $19/mo | 🟢 Day 10 |
| 10 | **Sharp Football** | EPA, success rate | API/Scrape | FREE | 🟢 Day 10 |
| 11 | **Football Outsiders** | DVOA, efficiency | Scrape | TBD | 🟢 Day 11 |

**Critical Questions**:
- Next Gen: Is there an API or must we scrape?
- PFF: Worth $40/month? What's available?
- Sharp Football: Free API access confirmed?

### TIER 3: Supplemental - Nice to Have ⭐⭐⭐

| # | Source | Purpose | Priority |
|---|--------|---------|----------|
| 12 | Action Network | Public betting % | 🟢 Day 11 |
| 13 | Vegas Insider | Line movements | 🟢 Day 11 |
| 14 | Rotoworld | News aggregation | 🟢 Day 12 |
| 15 | FantasyPros | Expert analysis | 🟢 Day 12 |
| 16 | Reddit NFL API | Sentiment, news | 🟢 Day 12 |
| 17 | NOAA Weather | Backup weather | 🟢 Day 13 |
| 18 | Team Websites | Depth charts | 🟢 Day 13 |
| 19 | PrizePicks Scraper | Current prop lines | 🔴 Day 4 |
| 20 | DraftKings Scraper | Alternative prop lines | 🟡 Day 13 |
| 21-28 | Other sources | Various | 🟢 Week 2 |

---

## Research Execution Plan

### Week 1: TIER 1 Critical Sources

**Day 1-2: ESPN API** 🔴 START HERE
```bash
# Test these endpoints:
curl "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
curl "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
curl "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/KC/roster"
curl "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/KC/injuries"

# Questions to answer:
- What player data is available?
- How are injuries formatted?
- Do we get practice participation?
- How detailed is play-by-play?
- Historical data availability?
```

**Deliverables**:
- `docs/sources/ESPN_API.md` - Complete documentation
- `samples/espn/*.json` - Real API responses
- Go/no-go decision
- Integration plan

**Day 3: Sleeper API**
```bash
curl "https://api.sleeper.app/v1/players/nfl"
curl "https://api.sleeper.app/v1/state/nfl"

# Questions:
- How fresh is injury data?
- Real-time update testing
- News format and sources
```

**Day 4: The Odds API + PrizePicks** 🚨 CRITICAL
```bash
# Sign up for The Odds API
# Test prop odds availability

# CRITICAL QUESTION:
# Does The Odds API have player props (rec yards, TDs)?
# Or just game lines (spread, total)?

# If no props → Must scrape PrizePicks/DraftKings directly
```

**Day 5: Twitter/News Sources**
- Evaluate Twitter API costs vs RSS feeds
- Test news aggregators
- Decide on news strategy

**Day 6: Weather APIs**
- Test Weather.com API
- Map stadium locations
- Verify forecast accuracy

**Day 7: NFL Official Data**
- Find official injury report sources
- Test scraping feasibility
- Document reporting schedule

### Week 2: TIER 2 & 3 Sources

**Day 8-9: Advanced Analytics**
- Next Gen Stats exploration
- PFF subscription decision
- Sharp Football access testing

**Day 10-11: Supplemental Data**
- FantasyData testing
- News aggregators
- Betting market data

**Day 12-13: Integration Planning**
- Map data flows
- Design database schemas
- Plan narrative generation
- Design embedding strategy

**Day 14: Finalize Research**
- Compile master documentation
- Make final source selections
- Create implementation roadmap

---

## Documentation Standards

### For Each Data Source

Create `docs/sources/[SOURCE_NAME].md` with:

```markdown
# [Source Name]

## Overview
- **Purpose**: What we use this for
- **Access Method**: API / Scraping / Manual
- **Cost**: Free / $X per month
- **Update Frequency**: Real-time / Hourly / Daily
- **Reliability**: High / Medium / Low
- **Status**: ✅ Approved / ❌ Rejected / 🟡 Under Review

## Authentication
- API Key Required: Yes/No
- Rate Limits: X requests per minute
- Sign-up Process: [steps]

## Endpoints Documented

### Endpoint 1: [Name]
- **URL**: `https://...`
- **Method**: GET/POST
- **Parameters**:
  - `param1` (required): Description
  - `param2` (optional): Description
- **Rate Limit**: X/min
- **Response Time**: Avg Xms

**Sample Request**:
```bash
curl -X GET "https://..." \
  -H "Authorization: Bearer TOKEN"
```

**Sample Response**:
```json
{
  "player_id": 123,
  "name": "Tyreek Hill",
  ...
}
```

## Complete Field Reference

| Field Path | Type | Description | Always Present? | Example |
|------------|------|-------------|-----------------|---------|
| `player.id` | int | Unique player ID | ✅ | 123 |
| `player.injury_status` | enum | OUT/DOUBTFUL/etc | ❌ | "QUESTIONABLE" |
| ... | ... | ... | ... | ... |

## Data Quality Assessment
- **Completeness**: 95% of expected fields present
- **Accuracy**: Cross-checked with official sources
- **Timeliness**: Updates within X minutes
- **Issues Found**: [Any problems discovered]

## Usage in RAG System

**Vector Database Narratives**:
- Game performance narratives
- Injury impact stories
- Matchup history summaries

**Structured Database Storage**:
- Player stats (Postgres)
- Injury status (Postgres)
- Real-time alerts (Redis)

**Example Narrative Generated**:
```
"Tyreek Hill vs BAL (Week 8, 2024): Hill dominated with 8 receptions
for 156 yards and 2 TDs. KC was trailing, leading to pass-heavy script
(45 attempts). Hill exploited BAL's Cover-3 scheme running deep posts.
Weather: Clear, 68°F. Hill was questionable (ankle) but full practice Friday."
```

## Code Examples

**Fetch Player Stats**:
```python
import requests

def get_player_stats(player_id):
    url = f"https://api.example.com/players/{player_id}"
    response = requests.get(url)
    return response.json()
```

**Parse Injury Data**:
```python
def parse_injury_status(data):
    return {
        'player_id': data['id'],
        'status': data['injury_status'],
        'type': data.get('injury_type'),
        'updated': data['updated_at']
    }
```

## Integration Plan

**Polling Frequency**:
- Game days: Every 15 minutes
- Off days: Every 30 minutes

**Data Validation**:
- Check required fields present
- Validate enum values
- Cross-reference with other sources
- Alert on conflicts

**Error Handling**:
- Retry logic: 3 attempts with exponential backoff
- Fallback: Use cached data if API down
- Alerts: Notify on repeated failures

## Testing Results

**Rate Limit Testing**:
- Attempted: 100 requests in 1 minute
- Result: Rate limited at 60 requests
- Confirmed limit: 60/minute

**Data Freshness Testing**:
- Monitored Patrick Mahomes injury update
- ESPN updated: 2:45 PM
- This API updated: 2:48 PM
- Lag: ~3 minutes ✅ Acceptable

**Edge Cases**:
- Missing injury_type field for 12% of injuries
- Playoff games have different format
- Historical data only available since 2020

## Decision

✅ **APPROVED** - Will use for primary player stats and injuries

**Rationale**:
- Free and reliable
- Good data coverage
- Acceptable update frequency
- Essential for MVP

**Alternatives Considered**:
- [Source X]: Rejected due to cost
- [Source Y]: Too slow to update
```

---

## Phase 1 Implementation (After Research)

### Week 3: Core Infrastructure

**Goals**:
1. Set up new codebase
2. Build data pipeline for ESPN + Sleeper
3. Get Qdrant running with sample data
4. Test Claude API integration

**Deliverables**:
- Working data collectors for ESPN + Sleeper
- Qdrant vector database with sample narratives
- Basic Claude API client
- Simple API endpoint for prop analysis

### Week 4: RAG Engine

**Goals**:
1. Build narrative generator
2. Implement retrieval logic
3. Create Claude prompt templates
4. Test end-to-end prediction

**Deliverables**:
- Narrative generation from structured data
- Vector similarity search
- Claude reasoning over context
- Working prop predictions

### Week 5: Real-Time Data

**Goals**:
1. Add remaining critical data sources
2. Implement 15-min polling
3. Build staleness monitoring
4. Add data validators

**Deliverables**:
- Comprehensive data pipeline
- Real-time updates
- Data quality monitoring
- Alert system for stale data

---

## Success Metrics

### Research Phase Complete When:
- [ ] All TIER 1 sources tested with real API calls
- [ ] Sample JSON responses saved for all sources
- [ ] All schemas fully documented
- [ ] Go/no-go decisions made
- [ ] Implementation priority finalized
- [ ] Exact costs known
- [ ] Data gaps identified
- [ ] Integration code snippets written

### MVP Complete When:
- [ ] ESPN + Sleeper data ingesting in real-time
- [ ] Qdrant storing 10K+ narrative embeddings
- [ ] Claude API making predictions
- [ ] Accuracy > current system by 20%+
- [ ] API responding in < 4 seconds
- [ ] Data < 30 minutes stale

---

## Budget Estimates

### Monthly Costs:

**Infrastructure**:
- Qdrant: FREE (self-hosted)
- PostgreSQL: FREE (self-hosted)
- Redis: FREE (self-hosted)

**APIs**:
- ESPN: FREE ✅
- Sleeper: FREE ✅
- The Odds API: $25 (10K requests)
- Twitter API: $100 (10K tweets) - TBD
- Weather.com: FREE tier (500 calls/day)
- PFF: $40 (if subscribe) - TBD
- FantasyData: $19 (if subscribe) - TBD

**AI**:
- Claude API: ~$16/month (500 props × 40% × $0.02)
- OpenAI Embeddings: ~$3/month

**Total**: $40-200/month depending on optional services

---

## Next Immediate Steps

1. ✅ Create project directory structure
2. ✅ Save master plan (this document)
3. 🔴 **START: Research ESPN API** (Day 1-2)
   - Test all endpoints
   - Document schemas
   - Save sample responses
   - Build test collector
4. Continue with research roadmap

---

## Notes & Decisions Log

**2025-10-26**: Project initialized
- Decided on Qdrant (free, Python-native)
- Decided on separate codebase
- Prioritized data accuracy over speed to market
- Committed to research-first approach

---

*Last Updated: October 26, 2025*
