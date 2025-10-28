# 🚀 Next Session - Start Here

## Quick Status Check

### 1. Verify Services Are Running
```bash
docker-compose ps
# All should show "Up" or "healthy"
```

### 2. Check Current System State
```bash
# View opportunities feed
open http://localhost:13000/opportunities

# Check prediction count
docker-compose exec -T postgres psql -U nfl_user -d nfl_analytics -c "SELECT COUNT(*) FROM predictions WHERE is_active = true;"

# Test API
curl -s "http://localhost:18000/api/v1/predictions/opportunities?limit=5" | jq '.count'
```

---

## 📊 Current State (as of Oct 28, 2025, 9:00 AM)

**System Status:** ✅ Production Ready

**Predictions in Database:**
- Total: 98 active predictions
- Players: 13 unique players
- Average Confidence: 69.90%
- Weeks: 8, 9

**Services:**
- ✅ API running on port 18000
- ✅ Frontend running on port 13000
- ✅ PostgreSQL on port 15432
- ✅ All Docker services healthy

**Key URLs:**
- Frontend: http://localhost:13000
- Opportunities Feed: http://localhost:13000/opportunities
- API: http://localhost:18000

---

## 🎯 What to Do First

### Option 1: View Existing Opportunities
```bash
# Just open the browser
open http://localhost:13000/opportunities
```

### Option 2: Generate More Predictions
```bash
# Generate for more players in week 9
curl -X POST "http://localhost:18000/api/v1/predictions/generate-batch?week=9&season=2025&max_players=50"

# This will take 5-10 minutes (0.5s per prediction * ~300 predictions)
```

### Option 3: Start Automated Scheduler
```bash
cd backend

# Run continuously (every 6 hours)
python -m scripts.run_prediction_scheduler

# Or run once to test
python -m scripts.run_prediction_scheduler --once
```

---

## 📖 Full Documentation

- **SESSION_SUMMARY_2025-10-28.md** - Complete session documentation
- **OPPORTUNITIES_SYSTEM_COMPLETE.md** - System architecture and usage
- **README.md** - Project overview
- **DOCKER_SETUP.md** - Docker configuration

---

## 🔧 Common Commands

### View Predictions
```bash
# Top opportunities by edge
docker-compose exec -T postgres psql -U nfl_user -d nfl_analytics -c "
  SELECT player_name, stat_type, line_score, edge, confidence
  FROM predictions
  WHERE is_active = true
  ORDER BY edge DESC
  LIMIT 10;
"

# Count by position
docker-compose exec -T postgres psql -U nfl_user -d nfl_analytics -c "
  SELECT player_position, COUNT(*)
  FROM predictions
  WHERE is_active = true
  GROUP BY player_position;
"
```

### Generate Predictions
```bash
# Small batch (fast test)
curl -X POST "http://localhost:18000/api/v1/predictions/generate-batch?week=9&season=2025&max_players=5"

# Full week
curl -X POST "http://localhost:18000/api/v1/predictions/generate-batch?week=9&season=2025"
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart just frontend
docker-compose restart frontend

# Restart just API
docker-compose restart api
```

---

## ⚠️ Quick Troubleshooting

**If opportunities feed is empty:**
1. Check prediction count in database (command above)
2. Verify API is responding: `curl http://localhost:18000/health`
3. Generate test predictions with batch endpoint

**If frontend won't load:**
1. Check logs: `docker-compose logs frontend`
2. Restart: `docker-compose restart frontend`
3. Rebuild if needed: `docker-compose build frontend && docker-compose up -d frontend`

**If API errors:**
1. Check logs: `docker-compose logs api`
2. Verify database connection
3. Check migration status: `docker-compose exec api alembic current`

---

## 🎉 Ready to Go!

Everything is set up and working. Pick one of the options above and continue building!

**Last Updated:** October 28, 2025, 9:00 AM
