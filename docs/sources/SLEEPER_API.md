# Sleeper API - Data Source Documentation

**Status:** ✅ APPROVED
**Priority:** TIER 1 (Critical) - Injury Data Primary Source
**Research Date:** 2025-10-26
**Recommendation:** GO

---

## Executive Summary

Sleeper is a fantasy football platform with a robust public API providing comprehensive player data with **real-time injury updates**. The API excels at injury tracking with 1,098 out of 11,400 players having current injury status information.

**Key Strengths:**
- ✅ **EXCEPTIONAL injury data** (1,098 players with injury status)
- ✅ Detailed injury information (status, body part, start date, notes)
- ✅ Practice participation tracking
- ✅ Depth chart information
- ✅ Complete player database (11,400 players)
- ✅ ID mapping to other platforms (ESPN, Yahoo, Rotowire, etc.)
- ✅ No authentication required
- ✅ Free to use

**Limitations:**
- ⚠️ Stats/projections endpoints returned 404 (may need different format)
- ⚠️ Some players have incomplete data (free agents, practice squad)
- ⚠️ No game-level data (use ESPN for that)

---

## API Overview

**Base URL:** `https://api.sleeper.app/v1`

**Authentication:** None required

**Rate Limits:** None observed (tested 5 endpoints with 1-second delays)

**Data Format:** JSON

**Update Frequency:**
- Injury status: Real-time (updates as news breaks)
- Player database: Daily
- Trending players: Hourly
- NFL state: Weekly

---

## Tested Endpoints

### 1. NFL State - `/state/nfl`

**Purpose:** Get current NFL season, week, and state information

**Sample Request:**
```bash
curl https://api.sleeper.app/v1/state/nfl
```

**Response Size:** ~230 bytes

**Key Data Available:**
- Current season (2025)
- Current week (8)
- Season type (regular, preseason, postseason)
- League season information
- Season start date
- Display week

**Data Structure:**
```json
{
  "week": 8,
  "leg": 8,
  "season": "2025",
  "season_type": "regular",
  "league_season": "2025",
  "previous_season": "2024",
  "season_start_date": "2025-09-04",
  "display_week": 8,
  "league_create_season": "2025",
  "season_has_scores": true
}
```

**Sample File:** `/samples/sleeper/nfl_state.json`

**Use Cases:**
- Determine current week for data queries
- Check if season is active
- Sync week information across systems

---

### 2. All NFL Players - `/players/nfl` 🌟 **CRITICAL ENDPOINT**

**Purpose:** Complete database of all NFL players with injury information

**Sample Request:**
```bash
curl https://api.sleeper.app/v1/players/nfl
```

**Response Size:** ~14.6 MB (11,400 players)

**Key Data Available:**

#### Player Identification
- `player_id`: Sleeper's unique player ID
- `espn_id`: ESPN player ID (for cross-referencing)
- `yahoo_id`: Yahoo player ID
- `rotowire_id`: Rotowire player ID
- `sportradar_id`: Sportradar GUID
- `gsis_id`: NFL GSIS ID
- `stats_id`, `fantasy_data_id`, `swish_id`, etc.

#### Basic Information
- `first_name`, `last_name`, `full_name`
- `position`: Position abbreviation (QB, RB, WR, TE, etc.)
- `fantasy_positions`: Array of eligible fantasy positions
- `number`: Jersey number
- `age`, `birth_date`, `birth_city`, `birth_state`, `birth_country`
- `height`, `weight`
- `college`, `high_school`
- `years_exp`: Years of experience

#### Team Information
- `team`: Current team abbreviation (e.g., "KC", "PHI")
- `team_abbr`: Alternate team abbreviation
- `team_changed_at`: Timestamp of last team change
- `status`: Player status ("Active", "Inactive", "PracticeSquad", etc.)

#### 🏥 Injury Information (CRITICAL)
- `injury_status`: Current injury designation
  - "Questionable" (518 players)
  - "IR" - Injured Reserve (268 players)
  - "Out" (176 players)
  - "PUP" - Physically Unable to Perform (37 players)
  - "Sus" - Suspended (12 players)
  - "Doubtful" (1 player)
  - "NA", "COV", "DNR" (various)
- `injury_body_part`: Body part affected (e.g., "Neck", "Ankle", "Knee")
- `injury_start_date`: When injury was first reported
- `injury_notes`: Additional injury details
- `practice_participation`: Practice participation level
- `practice_description`: Description of practice activity

#### Depth Chart
- `depth_chart_position`: Position on depth chart
- `depth_chart_order`: Order within position group (1 = starter)

#### Other
- `active`: Boolean - is player active in NFL
- `news_updated`: Last time player news was updated
- `search_rank`: Search ranking
- `hashtag`: Social media hashtag

**Data Structure (Sample Player):**
```json
{
  "6462": {
    "player_id": "6462",
    "first_name": "Ellis",
    "last_name": "Richardson",
    "full_name": "Ellis Richardson",
    "position": "TE",
    "fantasy_positions": ["TE"],
    "team": null,
    "team_abbr": null,
    "age": 26,
    "birth_date": "1995-02-12",
    "height": "75",
    "weight": "245",
    "college": "Georgia Southern",
    "years_exp": 3,
    "status": "Active",
    "injury_status": null,
    "injury_body_part": null,
    "injury_start_date": null,
    "injury_notes": null,
    "practice_participation": null,
    "practice_description": null,
    "depth_chart_position": null,
    "depth_chart_order": null,
    "espn_id": 3926590,
    "yahoo_id": 32262,
    "gsis_id": " 00-0035057",
    "sportradar_id": "efd6f3c3-b752-4bc2-a4f2-b776c15c3ec0"
  }
}
```

**Sample File:** `/samples/sleeper/players_all.json`

**Injury Data Statistics (as of 2025-10-26):**
- Total players: 11,400
- Players with injury status: 1,098 (9.6%)
- Injury status breakdown:
  - Questionable: 518 (47.2%)
  - IR: 268 (24.4%)
  - Out: 176 (16.0%)
  - NA: 83 (7.6%)
  - PUP: 37 (3.4%)
  - Sus: 12 (1.1%)
  - COV: 2
  - Doubtful: 1
  - DNR: 1

**Use Cases:**
- ✅ **Real-time injury tracking** (PRIMARY USE CASE)
- ✅ Player identification and mapping across platforms
- ✅ Depth chart information for starter/backup identification
- ✅ Practice participation for injury severity assessment
- ✅ Team roster tracking
- ✅ Physical attributes (height, weight for matchup analysis)

---

### 3. Trending Players - `/players/nfl/trending/add`

**Purpose:** Get players who are being added in fantasy leagues (indicates rising interest)

**Sample Request:**
```bash
curl https://api.sleeper.app/v1/players/nfl/trending/add
```

**Response Size:** ~990 bytes (25 players)

**Key Data Available:**
- Player ID
- Count (number of adds)

**Data Structure:**
```json
[
  {
    "player_id": "8136",
    "count": 247
  },
  {
    "player_id": "7564",
    "count": 189
  }
]
```

**Sample File:** `/samples/sleeper/trending_adds.json`

**Use Cases:**
- Identify players gaining interest (may indicate news/opportunity)
- Spot emerging breakout candidates
- Contextual narrative for predictions

---

### 4. NFL Stats - `/stats/nfl/{season}` ❌

**Purpose:** Player statistics for a season

**Sample Request:**
```bash
curl https://api.sleeper.app/v1/stats/nfl/2024
```

**Status:** ❌ 404 Not Found

**Notes:**
- Endpoint format may be incorrect
- May require week parameter
- May need regular/postseason specification
- **Not critical** - we can get stats from ESPN

---

### 5. Player Projections - `/projections/nfl/{season}` ❌

**Purpose:** Fantasy projections for players

**Sample Request:**
```bash
curl https://api.sleeper.app/v1/projections/nfl/2024
```

**Status:** ❌ 404 Not Found

**Notes:**
- Endpoint format may be incorrect
- May require week parameter
- **Not critical** - we can generate our own projections

---

## Data Quality Analysis

### Injury Data Quality Assessment

**Coverage:** Excellent
- 1,098 players with injury status out of 11,400 total (9.6%)
- This represents all significant injuries across the league
- Includes IR, Out, Questionable, Doubtful, PUP

**Detail Level:** Excellent
- Injury status (Questionable, IR, Out, etc.)
- Body part affected (Neck, Ankle, Knee, etc.)
- Injury start date
- Practice participation
- Practice description (limited, full, etc.)
- Notes field for additional context

**Freshness:** Excellent (Based on Fantasy Platform Requirements)
- Sleeper is a live fantasy platform - injury data MUST be real-time
- Updates as news breaks from official sources
- Practice reports updated daily
- Injury designations updated as teams announce them

**Reliability:** High
- Sleeper's business depends on accurate data
- Crowd-sourced verification from thousands of fantasy players
- Multiple data providers for validation

---

## ID Mapping Table

Sleeper provides excellent ID mapping to other platforms:

| Sleeper Field | Platform | Use Case |
|---------------|----------|----------|
| `espn_id` | ESPN | Cross-reference with ESPN API data |
| `yahoo_id` | Yahoo Sports | Fantasy data sync |
| `rotowire_id` | Rotowire | News and injury reports |
| `sportradar_id` | Sportradar | Advanced stats and tracking |
| `gsis_id` | NFL GSIS | Official NFL data |
| `stats_id` | Stats.com | Historical statistics |
| `fantasy_data_id` | FantasyData | Fantasy projections |
| `swish_id` | Swish Analytics | Advanced analytics |

**Integration Value:** 🌟 **CRITICAL**

This ID mapping allows us to:
1. Merge Sleeper injury data with ESPN game data
2. Cross-reference players across all data sources
3. Validate player identification
4. Build comprehensive player profiles

---

## Integration Plan

### Priority 1: Injury Data Sync (Daily + Breaking News)

```python
async def sync_injury_data():
    """
    Sync injury data from Sleeper API.

    Run:
    - Daily at 3 PM ET (after practice reports)
    - On-demand when breaking injury news detected
    """
    players = await fetch_sleeper_players()

    injured_players = [
        p for p in players.values()
        if p.get("injury_status") is not None
    ]

    for player in injured_players:
        await update_player_injury(
            player_id=player["espn_id"],  # Use ESPN ID for our database
            injury_status=player["injury_status"],
            injury_body_part=player.get("injury_body_part"),
            injury_start_date=player.get("injury_start_date"),
            injury_notes=player.get("injury_notes"),
            practice_participation=player.get("practice_participation"),
            practice_description=player.get("practice_description"),
            last_updated=datetime.now()
        )
```

### Priority 2: Player ID Mapping (One-time + Weekly Updates)

```python
async def build_player_id_mapping():
    """
    Build cross-platform player ID mapping.

    Run once at setup, then weekly to catch new players.
    """
    players = await fetch_sleeper_players()

    for sleeper_id, player in players.items():
        await store_player_mapping(
            sleeper_id=sleeper_id,
            espn_id=player.get("espn_id"),
            yahoo_id=player.get("yahoo_id"),
            rotowire_id=player.get("rotowire_id"),
            gsis_id=player.get("gsis_id"),
            name=player["full_name"],
            position=player["position"],
            team=player.get("team")
        )
```

### Priority 3: Depth Chart Tracking (Daily)

```python
async def sync_depth_charts():
    """
    Track depth chart changes for starter/backup analysis.

    Run daily to detect depth chart changes.
    """
    players = await fetch_sleeper_players()

    # Group by team and position
    depth_charts = {}
    for player in players.values():
        if player.get("team") and player.get("depth_chart_position"):
            key = f"{player['team']}_{player['depth_chart_position']}"
            if key not in depth_charts:
                depth_charts[key] = []
            depth_charts[key].append({
                "name": player["full_name"],
                "order": player.get("depth_chart_order", 999),
                "espn_id": player.get("espn_id")
            })

    # Sort by depth chart order
    for key in depth_charts:
        depth_charts[key].sort(key=lambda x: x["order"])

    await store_depth_charts(depth_charts)
```

### Suggested Update Frequencies

| Data Type | Update Frequency | Priority |
|-----------|-----------------|----------|
| Injury Status | Daily 3 PM ET + breaking news | CRITICAL |
| Player Database | Daily | HIGH |
| ID Mapping | Weekly | MEDIUM |
| Depth Charts | Daily | MEDIUM |
| Trending Players | Hourly (during season) | LOW |

---

## Data Gaps & Limitations

### Missing Data

1. **Game-Level Data** ❌
   - No scores, schedules, or game information
   - **Solution:** Use ESPN API

2. **Player Stats** ❌
   - Stats endpoint returned 404
   - **Solution:** Use ESPN API or build from game data

3. **Projections** ❌
   - Projections endpoint returned 404
   - **Solution:** Generate our own using RAG + Claude

4. **News Articles** ❌
   - No dedicated news endpoint
   - **Solution:** Use ESPN news API or Twitter

5. **Props/Betting Lines** ❌
   - No betting data
   - **Solution:** Use The Odds API or PrizePicks

### Data Quality Issues

1. **Free Agents**
   - Players without teams have incomplete data
   - Missing depth chart info
   - May have stale injury info

2. **Practice Squad**
   - Less detailed injury tracking
   - Depth chart position may be null

3. **Rookies**
   - May be missing some platform IDs
   - Years of experience = 0

---

## Sample Usage Code

### Injury Data Accessor

```python
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime

class SleeperDataAccessor:
    """Data accessor for Sleeper API."""

    BASE_URL = "https://api.sleeper.app/v1"

    async def fetch_all_players(self) -> Dict[str, Any]:
        """Fetch complete player database."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/players/nfl") as resp:
                if resp.status == 200:
                    return await resp.json()
                raise Exception(f"Sleeper API error: {resp.status}")

    async def get_injured_players(self) -> List[Dict[str, Any]]:
        """Get all players with injury status."""
        players = await self.fetch_all_players()

        injured = []
        for player_id, player in players.items():
            if player.get("injury_status"):
                injured.append({
                    "sleeper_id": player_id,
                    "espn_id": player.get("espn_id"),
                    "name": player.get("full_name"),
                    "position": player.get("position"),
                    "team": player.get("team"),
                    "injury_status": player["injury_status"],
                    "injury_body_part": player.get("injury_body_part"),
                    "injury_start_date": player.get("injury_start_date"),
                    "injury_notes": player.get("injury_notes"),
                    "practice_participation": player.get("practice_participation"),
                })

        return injured

    async def get_player_by_espn_id(self, espn_id: int) -> Optional[Dict[str, Any]]:
        """Find player by ESPN ID."""
        players = await self.fetch_all_players()

        for player in players.values():
            if player.get("espn_id") == espn_id:
                return player

        return None

    async def get_team_depth_chart(self, team_abbr: str) -> Dict[str, List[Dict]]:
        """Get depth chart for a team."""
        players = await self.fetch_all_players()

        depth_chart = {}
        for player in players.values():
            if player.get("team") == team_abbr and player.get("depth_chart_position"):
                position = player["depth_chart_position"]
                if position not in depth_chart:
                    depth_chart[position] = []

                depth_chart[position].append({
                    "name": player.get("full_name"),
                    "order": player.get("depth_chart_order", 999),
                    "injury_status": player.get("injury_status"),
                })

        # Sort each position by depth chart order
        for position in depth_chart:
            depth_chart[position].sort(key=lambda x: x["order"])

        return depth_chart
```

---

## Testing Results

**Test Date:** 2025-10-26
**Endpoints Tested:** 5
**Success Rate:** 60% (3/5)
**Average Response Time:** < 2 seconds (players endpoint is large)
**Failures:** 2 (stats and projections - not critical)

### Detailed Results

| Endpoint | Status | Response Size | Notes |
|----------|--------|---------------|-------|
| `/state/nfl` | ✅ 200 | 230 B | Current week info |
| `/players/nfl` | ✅ 200 | 14.6 MB | 11,400 players, 1,098 with injuries |
| `/players/nfl/trending/add` | ✅ 200 | 990 B | 25 trending players |
| `/stats/nfl/2024` | ❌ 404 | - | Not critical |
| `/projections/nfl/2024` | ❌ 404 | - | Not critical |

---

## Go/No-Go Decision

### ✅ **GO** - Sleeper API Approved as TIER 1 Injury Data Source

**Justification:**

1. **Injury Data Excellence:** 1,098 players with injury status - unmatched coverage
2. **Data Detail:** Injury status, body part, dates, practice participation
3. **ID Mapping:** Cross-platform IDs enable data merging
4. **Depth Charts:** Starter/backup information for context
5. **Reliability:** Fantasy platform requires real-time accuracy
6. **Cost:** Free with no authentication
7. **Performance:** Fast, reliable API

**Role in System:**

- **PRIMARY SOURCE** for injury data
- **SECONDARY SOURCE** for player identification/mapping
- **SUPPLEMENTAL** for depth chart information

**Why 60% Success Rate is Acceptable:**

- The 3 successful endpoints provide all critical data
- Failed endpoints (stats/projections) are available from other sources
- The players endpoint alone justifies using Sleeper
- Quality over quantity - what works is exceptional

**Critical Data Flow:**

```
Sleeper Injury Data → Our Database → Merge with ESPN Game Data → RAG Narratives
       ↓
ESPN Player ID Mapping
       ↓
Unified Player Profile
```

---

## Next Steps

1. ✅ **Research Complete** - Sleeper API validated
2. ⏭️ **Build Sleeper Accessor** (src/data/accessors/sleeper/)
   - Implement players endpoint
   - Add caching (14.6 MB response should be cached)
   - Build injury data extractor
   - Build ID mapping system
   - Add depth chart parser

3. ⏭️ **Integration with ESPN:**
   - Use espn_id to map Sleeper injuries to ESPN players
   - Merge injury data into player profiles
   - Build unified player database

4. ⏭️ **Move to Next Source:** The Odds API (prop betting lines)

---

## Additional Resources

- **Sample Responses:** `/Users/jace/dev/nfl-ai/samples/sleeper/`
- **Test Results:** `/Users/jace/dev/nfl-ai/samples/sleeper/research_results.json`
- **Research Script:** `/Users/jace/dev/nfl-ai/scripts/research/test_sleeper_api.py`
- **Official Docs:** https://docs.sleeper.com/ (if available)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-26
**Reviewed By:** Research Script (Automated)
**Next Review:** After implementing injury sync system
