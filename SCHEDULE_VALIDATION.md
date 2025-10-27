# Schedule Validation & Data Integrity

## Problem Identified: October 27, 2025

**Issue**: Made a prediction for Mahomes vs SF, but the Chiefs actually play WAS (Washington Commanders) in Week 8.

## Root Cause

1. **No schedule data in database** - Only had player stats, not game schedules
2. **No opponent validation** - API accepts any opponent string without checking
3. **Manual data entry error** - Used "SF" as example without verifying actual matchup

## Impact

- **Predictions are meaningless** if opponent is wrong
- **Matchup analysis is critical** - different defenses have different vulnerabilities
- **User trust is destroyed** if we provide inaccurate information

## Prevention Strategy

### 1. Mandatory Schedule Data

**Action**: Always fetch and maintain current NFL schedules

```bash
# Run weekly (or daily during season)
python -m scripts.fetch_nfl_schedule --season 2025
```

### 2. Opponent Validation

**Required**: Add validation to prediction endpoint

```python
# Before making prediction:
1. Look up player's team schedule for current week
2. Verify opponent matches request OR auto-populate it
3. Reject request if opponent doesn't match schedule
4. Add warning if using future/past week without schedule data
```

### 3. Data Freshness Alerts

**Current**: We validate player stats are fresh (<7 days)

**Add**: Validate schedule data is current
- Alert if no games scheduled for current week
- Alert if schedule data is >7 days old
- Alert if requesting prediction for game that already finished

### 4. Automatic Opponent Lookup

**Enhancement**: Don't require opponent in request - look it up automatically

```python
# Given: player_name, stat_type, line_score
# Auto-determine:
1. Player's team from database
2. Current week from Sleeper API
3. Opponent from schedule table
4. Validate game hasn't started yet
```

## Implementation Checklist

- [x] Create fetch_nfl_schedule.py script
- [x] Add opponent validation to prediction endpoint
- [x] Add schedule freshness check to data validation (already in backfill script)
- [x] Make opponent optional (auto-lookup from schedule)
- [x] Add "game already started" validation
- [x] Create populate_teams.py script (required for foreign keys)
- [x] Populate 32 NFL teams in database
- [x] Fetch and store Week 1-10 schedules
- [x] Verify Week 8 shows WSH @ KC (correct matchup)
- [x] Document fix in SCHEDULE_FIX_COMPLETE.md
- [ ] Create cron job / scheduled task to update schedules daily (deployment task)
- [ ] Add endpoint to show current week matchups (nice-to-have)
- [ ] Document schedule fetch process in README (nice-to-have)

## Data Sources

**Primary**: Sleeper API
- Endpoint: `https://api.sleeper.app/v1/schedules/nfl/regular/{season}/{week}`
- Free, no auth required
- Includes scores for completed games

**Backup**: ESPN API (if available)

## Critical Rule

**NEVER MAKE PREDICTIONS WITHOUT VERIFIED OPPONENT DATA**

If opponent is not in request:
1. Look up from schedule
2. If not found, REJECT with error: "Cannot determine opponent for Week {X}. Please fetch schedule data."

If opponent IS in request:
1. Validate against schedule
2. If mismatch, REJECT with error: "Opponent mismatch. {Player}'s team plays {ActualOpponent} in Week {X}, not {RequestedOpponent}"

## Testing

Before any prediction:
```bash
# Verify schedule data exists
python -m scripts.fetch_nfl_schedule --show-current

# Check specific matchup
psql -c "SELECT * FROM games WHERE season=2025 AND week=8 AND (home_team_id='KC' OR away_team_id='KC');"
```
