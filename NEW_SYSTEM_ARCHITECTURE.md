# NEW RAG + Claude AI System Architecture
**Status:** Clean slate - Old statistical system completely removed
**Date:** 2025-10-26

---

## How the NEW System Works with Data Sources

### Core Difference: Statistical vs AI

**OLD System (REMOVED):**
```
Data Source → Calculate averages → Apply adjustment factors → Output prediction
```
- ESPN stats → Season average: 65.2 yards
- Weather → -5% adjustment for wind
- Injury → -10% adjustment for questionable
- Defense → -8% adjustment for tough matchup
- **Final: 65.2 × 0.95 × 0.90 × 0.92 = 51.3 yards predicted**

**NEW System (Building Now):**
```
Data Sources → Generate narrative → RAG search → Claude reasoning → Prediction with context
```
- All data sources → Rich contextual narrative
- RAG → Find similar historical situations
- Claude → Analyzes everything holistically
- **Final: "OVER 69.5 yards (75% confidence) because..."**

---

## Data Source Integration (NEW Architecture)

### 1. PostgreSQL: Structured Data Store

**What Goes Here:**
- Player game-by-game stats (historical performance)
- PrizePicks props (what we're predicting)
- Games (matchups, scores, weather)
- Injuries (Sleeper data)
- Team/player info

**How It's Used:**
```python
# When a new prop appears:
prop = "Jaylen Waddle - Receiving Yards: 69.5"

# Pull structured data from Postgres
game_data = get_game_context(prop)
# → Opponent: BUF (ranked #3 vs WR)
# → Weather: 15mph wind, 42°F
# → Game at home

player_history = get_player_game_stats(player_id="waddle")
# → Last 5 games: 75, 45, 92, 61, 58 yards
# → vs BUF (2024): 48 yards
# → In wind >10mph: 52, 48, 61 yards (avg 53.7)

injury_data = get_player_injuries(player_id="waddle")
# → Status: ACTIVE (no injury designation)
```

**Key Point:** PostgreSQL gives us FACTS and NUMBERS

---

### 2. Qdrant: Vector Database (NEW - RAG)

**What Goes Here:**
- Game narratives (embedded as vectors)
- Historical similar situations
- Performance patterns

**How It Works:**

**Step 1: Generate Narrative** (after every game)
```python
# After Waddle plays vs BUF in Week 8
narrative = f"""
Player: Jaylen Waddle
Game: Week 8, 2025 vs BUF
Result: 6 receptions, 58 yards, 0 TDs
Context: Home game, 15mph wind, 42°F weather
Opponent: BUF ranked #3 vs WR
Status: ACTIVE, no injuries
QB: Tua Tagovailoa (ACTIVE)
Game Script: Lost 24-17, trailed most of game (more passing)
Snap Share: 72% (54/75 snaps)
Targets: 9 (66% catch rate)
Analysis: Weather limited deep balls. Short-area targets effective.
"""

# Embed this narrative into a 3072-dimension vector
vector = openai_embed(narrative)

# Store in Qdrant
qdrant.upsert(
    collection="game_performances",
    vector=vector,
    payload={
        "player_id": "waddle",
        "stat_type": "receiving_yards",
        "actual_value": 58,
        "game_date": "2025-10-24",
        "narrative": narrative
    }
)
```

**Step 2: Semantic Search** (when predicting)
```python
# New prop: Waddle Receiving Yards 65.5 vs NYJ next week
query_narrative = f"""
Looking for: Jaylen Waddle receiving yard performances
Similar to: vs tough defense, cold weather, coming off 58-yard game
Season: 2025
"""

# Search for similar situations
query_vector = openai_embed(query_narrative)

similar_games = qdrant.search(
    collection="game_performances",
    query_vector=query_vector,
    limit=10,
    filters={
        "player_id": "waddle",
        "stat_type": "receiving_yards"
    }
)

# Returns most similar past performances:
# 1. Week 4, 2024 vs NYJ: 61 yards (89% similarity)
# 2. Week 12, 2024 vs tough DEF: 52 yards (87% similarity)
# 3. Week 6, 2025 in cold: 58 yards (85% similarity)
```

**Key Point:** Qdrant finds SIMILAR SITUATIONS semantically, not just by numbers

---

### 3. Claude API: The Prediction Engine

**What It Does:**
- Analyzes all context holistically
- Provides reasoning (not just a number)
- Outputs confidence scores
- Explains WHY

**How It Works:**
```python
# Build comprehensive context for Claude
context = {
    "prop": {
        "player": "Jaylen Waddle",
        "stat_type": "Receiving Yards",
        "line": 65.5,
        "opponent": "NYJ"
    },

    "current_season_stats": {
        "games_played": 8,
        "avg_per_game": 63.8,
        "last_3_games": [75, 61, 58],
        "std_dev": 15.2
    },

    "matchup_context": {
        "opponent_rank_vs_wr": 12,  # (middle of pack)
        "weather": "Clear, 68°F, 5mph wind",
        "location": "Away",
        "vegas_total": 47.5,  # (high-scoring game expected)
    },

    "injury_context": {
        "player_status": "ACTIVE",
        "qb_status": "ACTIVE (Tua)",
        "key_teammates": "All starting WRs healthy"
    },

    "similar_situations": [
        {
            "game": "Week 4, 2024 vs NYJ",
            "result": 61 yards,
            "context": "Away, Tua active, 68°F clear",
            "narrative": "Caught 7 of 10 targets..."
        },
        {
            "game": "Week 7, 2025 vs ranked #14 defense",
            "result": 75 yards,
            "context": "Home, ideal weather",
            "narrative": "Breakout game with..."
        }
    ]
}

# Send to Claude
prompt = f"""
You are an expert NFL prop analyzer. Predict whether Jaylen Waddle will go OVER or UNDER 65.5 receiving yards vs NYJ.

CURRENT PROP:
{context['prop']}

SEASON STATS:
{context['current_season_stats']}

MATCHUP CONTEXT:
{context['matchup_context']}

INJURIES:
{context['injury_context']}

SIMILAR HISTORICAL GAMES:
{context['similar_situations']}

Provide:
1. Prediction: OVER or UNDER
2. Confidence: 0-100%
3. Projected Value: Your estimate
4. Reasoning: Detailed analysis of WHY

Format as JSON.
"""

response = anthropic.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt}]
)

# Claude's response:
{
    "prediction": "OVER",
    "confidence": 72,
    "projected_value": 71.3,
    "reasoning": "Strong OVER for several reasons:

    1. MATCHUP ADVANTAGE: NYJ ranks #12 vs WR (middle of pack).
       In Week 4 2024, Waddle posted 61 yards vs this same defense
       with similar weather conditions.

    2. POSITIVE TREND: Last 3 games show consistency (75, 61, 58).
       Even the 'down' game of 58 was in harsh weather. With clear
       conditions this week, expect reversion to 70+ range.

    3. GAME SCRIPT: Vegas total of 47.5 suggests high-scoring affair.
       Miami will need to throw to keep pace. Waddle is Tua's
       safety valve and should see 8-10 targets.

    4. HEALTH: Full health for Waddle and Tua is critical. Both
       are ACTIVE with no injury designations. This removes
       the biggest risk factor.

    5. VENUE: While road game, NYJ's home field advantage is
       minimal. Weather conditions are ideal for passing.

    RISK FACTORS:
    - Game script could shift if Miami gets big lead early
    - Target share could diminish if Tyreek Hill dominates
    - Waddle's floor is ~45 yards in tough games

    PROJECTION: 71.3 yards (range: 58-85)
    RECOMMENDATION: OVER 65.5 at 72% confidence"
}
```

**Key Point:** Claude provides REASONING and CONTEXT, not just predictions

---

## Complete Prediction Flow (NEW System)

```
┌─────────────────────────────────────────────────────┐
│  1. NEW PROP DETECTED                               │
│  PrizePicks: Jaylen Waddle Receiving Yards 65.5     │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  2. GATHER STRUCTURED DATA (PostgreSQL)             │
│  • Player game stats (last 10 games)                │
│  • Matchup info (opponent defensive rank)           │
│  • Weather forecast (from NOAA)                     │
│  • Injury status (from Sleeper)                     │
│  • Vegas lines (total, spread)                      │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  3. GENERATE SEARCH QUERY                           │
│  Build narrative describing what we're looking for  │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  4. RAG SEARCH (Qdrant)                             │
│  • Embed query → vector                             │
│  • Search for similar past performances             │
│  • Return top 5-10 most relevant games              │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  5. BUILD CLAUDE CONTEXT                            │
│  Combine:                                           │
│  • Current stats                                    │
│  • Matchup data                                     │
│  • Similar historical games (from RAG)              │
│  • Weather, injuries, vegas lines                   │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  6. CLAUDE PREDICTION                               │
│  • Analyzes all context holistically                │
│  • Provides prediction + confidence + reasoning     │
│  • Returns detailed explanation                     │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  7. STORE PREDICTION (PostgreSQL)                   │
│  Save to predictions table:                         │
│  • prediction: "OVER"                               │
│  • confidence: 72                                   │
│  • reasoning: "Strong OVER because..."              │
│  • similar_situations_data: {...}                   │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  8. RETURN TO USER                                  │
│  Display prediction with full reasoning             │
└─────────────────────────────────────────────────────┘

After game completes:

┌─────────────────────────────────────────────────────┐
│  9. POST-GAME UPDATE                                │
│  • Get actual result: 71 yards                      │
│  • Update prediction: was_correct = TRUE            │
│  • Generate narrative of actual game                │
│  • Embed narrative → store in Qdrant                │
│  • Now available for future RAG searches!           │
└─────────────────────────────────────────────────────┘
```

---

## Data Source Roles (Summary)

| Data Source | Old Role | NEW Role |
|-------------|----------|----------|
| **ESPN** | Provide season averages | Provide game-by-game history for narratives |
| **Sleeper** | N/A (not syncing) | Provide real-time injury context |
| **PrizePicks** | Props to analyze | Props to analyze (SAME) |
| **NOAA** | Weather adjustment -5% | Weather context for Claude |
| **Next Gen Stats** | N/A | Advanced metrics for Claude context |
| **PostgreSQL** | Store stats & predictions | Store ALL data + predictions |
| **Qdrant** | N/A (didn't exist) | **NEW:** Store game narratives as vectors |
| **Claude API** | N/A (used scipy) | **NEW:** Main prediction engine |
| **OpenAI** | N/A | **NEW:** Generate embeddings for RAG |

---

## Why This is Better

### Old System (Statistical):
```python
prediction = season_avg * weather_adj * injury_adj * defense_adj
# 65.2 × 0.95 × 0.90 × 0.92 = 51.3 yards
# Confidence: Based on standard deviation
```

**Problems:**
- ❌ Treats all factors as independent multipliers
- ❌ Can't reason about complex interactions
- ❌ No understanding of game context
- ❌ Can't learn from similar situations
- ❌ No explanation of WHY

### NEW System (AI + RAG):
```python
# 1. Find games where Waddle faced similar conditions
similar_games = rag_search("Waddle vs tough defense in cold")

# 2. Claude analyzes everything together
reasoning = claude.analyze({
    "current_stats": stats,
    "matchup": matchup,
    "similar_games": similar_games,
    "injuries": injuries,
    "weather": weather
})

# Returns: "OVER 65.5 because in 3 similar games he averaged
#           72 yards, and the game script favors passing..."
```

**Benefits:**
- ✅ Understands complex interactions
- ✅ Learns from similar historical situations
- ✅ Provides clear reasoning
- ✅ Adapts to unique contexts
- ✅ Gets smarter over time (more narratives in Qdrant)

---

## Key Insight: The Feedback Loop

Every game creates NEW data for the system:

```
Week 8: Predict Waddle 65.5 yards
     ↓
Game happens: Waddle gets 71 yards
     ↓
Generate narrative: "Waddle 71 yards vs NYJ in ideal weather..."
     ↓
Store in Qdrant with embedding
     ↓
Week 15: New similar prop appears
     ↓
RAG search finds Week 8 game
     ↓
Claude uses it as reference: "Similar to Week 8 when he had 71..."
     ↓
Better prediction!
```

**The system gets smarter with every game.**

---

## What We're Building Next

1. **Claude Service** (`services/claude_prediction.py`)
   - API wrapper for Claude
   - Prompt templates
   - Response parsing

2. **OpenAI Embeddings** (`services/embeddings.py`)
   - Generate vectors from narratives
   - Use text-embedding-3-large (3072 dimensions)

3. **Qdrant Service** (`services/vector_store.py`)
   - Store game narratives
   - Semantic search
   - Collection management

4. **RAG Generator** (`services/rag_narrative.py`)
   - Build narratives from game data
   - Generate embeddings
   - Search for similar situations

5. **Prediction Endpoint** (`api/endpoints/predictions.py`)
   - Accept prop
   - Orchestrate full flow
   - Return Claude prediction

6. **ESPN Game Stats** (`services/espn_game_stats.py`)
   - **CRITICAL:** Get historical player performance
   - Populate player_game_stats table
   - Enable trend analysis

---

## Cost Estimate (NEW System)

**Per Prediction:**
- Claude API: ~$0.015 (2000 tokens in, 1500 tokens out)
- OpenAI Embedding: ~$0.0001 (query embedding)
- Qdrant: Free (self-hosted)

**Monthly (1000 props analyzed):**
- Claude: ~$15
- OpenAI: ~$0.10
- **Total: ~$15-20/month**

**Plus Overhead:**
- Embedding game narratives: ~$5/month
- Additional Claude calls for refinement: ~$10/month
- **TOTAL: $30-50/month**

Much lower than the $60-250 estimate because we're not embedding everything, just game narratives.

---

## Next Steps

1. ✅ Remove old system (DONE)
2. ✅ Add Qdrant + AI packages (DONE)
3. Build core AI services
4. Build ESPN game stats accessor
5. Create prediction endpoint
6. Test end-to-end flow
7. Backfill historical data

We're building the RIGHT system now! 🚀
