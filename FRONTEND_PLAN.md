# Frontend Implementation Plan - NFL AI Prediction System

## Overview

A Next.js web application for browsing and analyzing NFL player prop predictions with AI-powered insights, multi-season historical context, and intelligent bet discovery.

## Tech Stack

### Core Framework
```
- Next.js 14+ (App Router)
- React 18+
- TypeScript
- Tailwind CSS
- shadcn/ui component library
```

### Data & State
```
- TanStack Query (React Query) - API calls & caching
- Zustand - Lightweight global state (user preferences, filters)
- Local Storage - Persist favorites, tracked bets
```

### Visualization
```
- Recharts - Charts and graphs
- Framer Motion - Animations
- Lucide React - Icons
```

### Deployment
```
- Vercel (recommended) or Digital Ocean App Platform
- Environment variables for API endpoints
```

## Information Architecture

### Three Core Browsing Modes

#### Mode 1: Discovery View - "Top Picks"
**URL**: `/`

**Purpose**: Answer "What should I bet today?"

**Layout**:
```
[Header/Nav]
  ↓
[Time-based sections]
  - Tonight (if Thu/Mon)
  - Tomorrow
  - Sunday Early
  - Sunday Late
  - Monday Night
  ↓
[High-confidence picks first]
  - 75%+ marked with 🔥
  - Show top 3-5 per time slot
  - Expandable for all picks
```

**Filters**:
- Minimum confidence (60%, 70%, 75%+)
- Position (QB/RB/WR/TE/All)
- Prop type (Yards/TDs/Receptions)
- Sort (Confidence, Edge, Time)

#### Mode 2: Game-by-Game View
**URL**: `/games` or `/games/week/8`

**Purpose**: Browse matchups, compare game contexts

**Layout**:
```
[Week selector]
  ↓
[Games grouped by time slot]
  - Thursday Night
  - Sunday 1:00 PM
  - Sunday 4:00 PM
  - Sunday Night
  - Monday Night
  ↓
[Each game card shows:]
  - Teams, spread, total
  - Weather/location
  - Top 3-4 high-confidence props
  - "View all X props" link
```

#### Mode 3: Individual Game Deep Dive
**URL**: `/games/bal-cin-2025-w8`

**Purpose**: See all props for a matchup, build parlays

**Tabs**:
1. **Top Picks**: 5-7 highest confidence
2. **All Props**: Sortable table
3. **SGP Builder**: Parlay correlation analysis
4. **Game Context**: Weather, injuries, trends

**Props grouped by**:
- Confidence tier (High/Med/Low)
- Player (all props for one player)
- Prop type (Pass/Rush/Rec)

### Supporting Pages

#### Player Profile
**URL**: `/players/patrick-mahomes`

**Shows**:
- 2025 season stats
- Career trends chart
- All current week props
- Recent prediction history
- Season-long performance

#### Search
**URL**: `/search?q=mahomes`

**Features**:
- Fuzzy search
- Autocomplete
- Filter by position
- Recent searches
- Popular players

#### Tracked Bets
**URL**: `/tracked`

**Shows**:
- Live bets (in-progress games)
- Upcoming bets
- Past results (W/L)
- Weekly/season performance
- ROI tracking

## Component Architecture

### Page Components
```
/app
  ├── page.tsx                    (Discovery: Top Picks)
  ├── games
  │   ├── page.tsx               (Game-by-game list)
  │   └── [gameId]
  │       └── page.tsx           (Individual game deep dive)
  ├── players
  │   └── [playerId]
  │       └── page.tsx           (Player profile)
  ├── search
  │   └── page.tsx               (Search interface)
  └── tracked
      └── page.tsx               (User's tracked bets)
```

### Shared Components
```
/components
  ├── ui/                        (shadcn/ui primitives)
  │   ├── button.tsx
  │   ├── card.tsx
  │   ├── progress.tsx
  │   ├── badge.tsx
  │   ├── select.tsx
  │   └── ...
  │
  ├── prediction/
  │   ├── PredictionCard.tsx     (Main result card)
  │   ├── ConfidenceMeter.tsx    (Visual confidence bar)
  │   ├── KeyFactors.tsx         (Bullet points)
  │   ├── RiskFactors.tsx        (Warning section)
  │   └── TLDRSection.tsx        (One-liner summary)
  │
  ├── stats/
  │   ├── RecentFormChart.tsx    (Last 5 games bar chart)
  │   ├── SeasonStatsTable.tsx   (Stats grid)
  │   ├── TrendIndicator.tsx     (📈📉 arrows)
  │   └── StatComparison.tsx     (Side-by-side)
  │
  ├── rag/
  │   ├── SimilarSituations.tsx  (RAG results cards)
  │   ├── SimilarityBadge.tsx    (87% match indicator)
  │   └── HistoricalOutcome.tsx  (✓ OVER / ✗ UNDER)
  │
  ├── game/
  │   ├── GameCard.tsx           (Matchup summary)
  │   ├── GameContext.tsx        (Weather, spread, total)
  │   ├── PropsList.tsx          (Sortable prop table)
  │   └── SGPBuilder.tsx         (Parlay builder)
  │
  ├── player/
  │   ├── PlayerSearch.tsx       (Autocomplete search)
  │   ├── PlayerCard.tsx         (Avatar, name, team)
  │   └── PlayerStats.tsx        (Season summary)
  │
  ├── layout/
  │   ├── Header.tsx             (Top nav)
  │   ├── MobileNav.tsx          (Bottom tabs on mobile)
  │   ├── FilterBar.tsx          (Persistent filters)
  │   └── Sidebar.tsx            (Desktop navigation)
  │
  └── shared/
      ├── LoadingSkeleton.tsx    (Loading states)
      ├── ErrorBoundary.tsx      (Error handling)
      ├── EmptyState.tsx         (No results)
      └── ThinkingAnimation.tsx  (AI analyzing...)
```

## API Integration

### Endpoints to Call

```typescript
// /lib/api.ts

// Get prediction for specific player prop
POST /api/predictions/predict
{
  player_name: string
  stat_type: string
  line_score: number
  opponent?: string  // Optional, will be auto-looked up
}

// Get all predictions for a week (NEW - needs backend endpoint)
GET /api/predictions/week/8?confidence_min=60

// Get all predictions for a game (NEW - needs backend endpoint)
GET /api/predictions/game/bal-cin-2025-w8

// Get player profile
GET /api/players/mahomes_p_4046

// Get current week schedule
GET /api/schedule/current

// Get game details
GET /api/games/bal-cin-2025-w8

// Health check
GET /health
```

### New Backend Endpoints Needed

We'll need to add these to the FastAPI backend:

```python
# backend/app/api/endpoints/predictions.py

@router.get("/predictions/week/{week}")
async def get_week_predictions(
    week: int,
    season: int = 2025,
    confidence_min: float = 60,
    position: Optional[str] = None,
    stat_type: Optional[str] = None
):
    """
    Get all high-confidence predictions for a week.
    Pre-generate predictions for top players.
    """
    pass

@router.get("/predictions/game/{game_id}")
async def get_game_predictions(game_id: str):
    """
    Get all predictions for players in a specific game.
    """
    pass

@router.get("/predictions/top")
async def get_top_predictions(
    limit: int = 20,
    time_range: str = "today"  # today, tomorrow, week
):
    """
    Get highest-confidence predictions across all games.
    """
    pass
```

### Data Models

```typescript
// types/prediction.ts

export interface Prediction {
  player_name: string
  player_id: string
  position: string
  team: string
  opponent: string
  week: number
  stat_type: string
  line_score: number
  prediction: 'OVER' | 'UNDER'
  confidence: number
  projected_value: number
  edge: number  // projected - line

  reasoning: string
  key_factors: string[]
  risk_factors: string[]

  current_stats: {
    games_played: number
    avg_per_game: number
    last_3_games: number[]
    min: number
    max: number
    std_dev: number
  }

  similar_situations: SimilarSituation[]

  metadata: {
    model: string
    generated_at: string
  }
}

export interface SimilarSituation {
  id: string
  similarity_score: number
  player_name: string
  game: string  // "Week 14, 2024 vs LAC"
  result: string  // "291 yards"
  narrative: string
  outcome: 'OVER' | 'UNDER'
  line?: number
}

export interface Game {
  id: string
  home_team: string
  away_team: string
  week: number
  season: number
  game_time: string
  spread: number
  total: number
  is_completed: boolean
  home_score?: number
  away_score?: number
}

export interface Player {
  id: string
  name: string
  position: string
  team: string
  photo_url?: string
  jersey_number?: number
}
```

## UI Design System

### Color Palette

```css
/* tailwind.config.ts */

colors: {
  // Brand
  primary: '#1E3A8A',      // NFL Blue
  secondary: '#059669',     // Success Green
  accent: '#DC2626',        // Warning Red

  // Confidence levels
  confidence: {
    high: '#10B981',        // 70%+ Green
    medium: '#F59E0B',      // 50-69% Yellow
    low: '#EF4444',         // <50% Red
  },

  // Predictions
  over: '#10B981',          // Green
  under: '#DC2626',         // Red
  push: '#64748B',          // Gray

  // Game states
  live: '#EF4444',          // Red dot
  upcoming: '#3B82F6',      // Blue
  final: '#64748B',         // Gray
}
```

### Typography

```css
/* Global styles */

h1: text-4xl font-bold tracking-tight
h2: text-3xl font-semibold
h3: text-2xl font-semibold
h4: text-xl font-semibold
body: text-base
small: text-sm
tiny: text-xs
```

### Spacing Scale

```
xs:  0.5rem (8px)
sm:  0.75rem (12px)
md:  1rem (16px)
lg:  1.5rem (24px)
xl:  2rem (32px)
2xl: 3rem (48px)
```

### Component Patterns

#### Confidence Meter
```tsx
<div className="space-y-2">
  <div className="flex justify-between">
    <span className="text-sm text-muted-foreground">Confidence</span>
    <span className="font-bold">{confidence}%</span>
  </div>
  <Progress
    value={confidence}
    className={cn(
      confidence >= 70 && "bg-confidence-high",
      confidence >= 50 && confidence < 70 && "bg-confidence-medium",
      confidence < 50 && "bg-confidence-low"
    )}
  />
  <span className="text-xs text-muted-foreground">
    {confidence >= 70 ? "HIGH" : confidence >= 50 ? "MODERATE" : "LOW"}
  </span>
</div>
```

#### Prediction Badge
```tsx
<Badge
  variant={prediction === 'OVER' ? 'success' : 'destructive'}
  className="text-lg px-4 py-2"
>
  {prediction} {lineScore}
</Badge>
```

#### Recent Form Bars
```tsx
<div className="space-y-1">
  {last5Games.map((yards, i) => (
    <div key={i} className="flex items-center gap-2">
      <span className="text-xs w-12">Week {week - i}</span>
      <div className="flex-1 h-6 bg-muted rounded">
        <div
          className={cn(
            "h-full rounded transition-all",
            yards > lineScore ? "bg-over" : "bg-under"
          )}
          style={{ width: `${(yards / maxYards) * 100}%` }}
        />
      </div>
      <span className="text-xs w-16 text-right">{yards}</span>
      {yards > lineScore ? <Check className="w-4 h-4 text-over" /> : <X className="w-4 h-4 text-under" />}
    </div>
  ))}
  <div className="border-t pt-1">
    <div className="text-xs text-muted-foreground">
      Line: {lineScore}
    </div>
  </div>
</div>
```

## Responsive Design

### Breakpoints

```
sm:  640px  - Mobile landscape, small tablets
md:  768px  - Tablets
lg:  1024px - Laptops, desktop
xl:  1280px - Large desktop
2xl: 1536px - Extra large screens
```

### Mobile-First Approach

**Mobile (<768px)**:
- Bottom navigation bar (4 tabs)
- Single column layout
- Stacked cards
- Collapsible sections
- Swipeable carousels for similar situations

**Tablet (768px-1024px)**:
- Side navigation drawer
- 2-column grid for predictions
- More spacing
- Show more data per card

**Desktop (1024px+)**:
- Persistent sidebar
- 3-column grid
- All details visible
- Hover states
- Keyboard shortcuts

### Mobile Navigation

```tsx
<nav className="md:hidden fixed bottom-0 left-0 right-0 bg-card border-t">
  <div className="flex justify-around items-center h-16">
    <NavItem icon={Flame} label="Top Picks" href="/" />
    <NavItem icon={Calendar} label="Games" href="/games" />
    <NavItem icon={Search} label="Search" href="/search" />
    <NavItem icon={Star} label="Tracked" href="/tracked" />
  </div>
</nav>
```

## State Management

### React Query Setup

```typescript
// lib/queryClient.ts

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutes
      cacheTime: 30 * 60 * 1000,      // 30 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

// hooks/usePrediction.ts
export function usePrediction(
  playerName: string,
  statType: string,
  lineScore: number
) {
  return useQuery({
    queryKey: ['prediction', playerName, statType, lineScore],
    queryFn: () => fetchPrediction({ playerName, statType, lineScore }),
    enabled: !!playerName && !!statType && !!lineScore,
  })
}

// hooks/useWeekPredictions.ts
export function useWeekPredictions(week: number) {
  return useQuery({
    queryKey: ['predictions', 'week', week],
    queryFn: () => fetchWeekPredictions(week),
    staleTime: 10 * 60 * 1000,  // 10 minutes for bulk data
  })
}
```

### Global State (Zustand)

```typescript
// store/useFiltersStore.ts

interface FiltersState {
  confidenceMin: number
  positions: string[]
  propTypes: string[]
  sortBy: 'confidence' | 'edge' | 'time'
  setConfidenceMin: (min: number) => void
  setPositions: (positions: string[]) => void
  // ... other setters
}

export const useFiltersStore = create<FiltersState>((set) => ({
  confidenceMin: 60,
  positions: [],
  propTypes: [],
  sortBy: 'confidence',
  setConfidenceMin: (min) => set({ confidenceMin: min }),
  // ... other implementations
}))

// store/useTrackedBetsStore.ts

interface TrackedBet {
  id: string
  prediction: Prediction
  amount?: number
  addedAt: string
}

interface TrackedBetsState {
  bets: TrackedBet[]
  addBet: (prediction: Prediction, amount?: number) => void
  removeBet: (id: string) => void
  clearBets: () => void
}

export const useTrackedBetsStore = create<TrackedBetsState>(
  persist(
    (set) => ({
      bets: [],
      addBet: (prediction, amount) =>
        set((state) => ({
          bets: [...state.bets, {
            id: crypto.randomUUID(),
            prediction,
            amount,
            addedAt: new Date().toISOString()
          }]
        })),
      removeBet: (id) =>
        set((state) => ({
          bets: state.bets.filter(b => b.id !== id)
        })),
      clearBets: () => set({ bets: [] }),
    }),
    { name: 'tracked-bets' }
  )
)
```

## Performance Optimization

### Code Splitting

```typescript
// Lazy load heavy components
const RecentFormChart = lazy(() => import('@/components/stats/RecentFormChart'))
const SGPBuilder = lazy(() => import('@/components/game/SGPBuilder'))

// Use Suspense with loading fallback
<Suspense fallback={<LoadingSkeleton />}>
  <RecentFormChart data={stats} />
</Suspense>
```

### Image Optimization

```typescript
// Use Next.js Image component
import Image from 'next/image'

<Image
  src={player.photoUrl}
  alt={player.name}
  width={80}
  height={80}
  className="rounded-full"
  loading="lazy"
  placeholder="blur"
  blurDataURL="/placeholder-player.jpg"
/>
```

### API Response Caching

```typescript
// app/api/predictions/route.ts (Next.js API route as proxy)

export async function POST(request: Request) {
  const body = await request.json()

  // Cache prediction results
  const cacheKey = `prediction-${body.player_name}-${body.stat_type}-${body.line_score}`

  const cached = await redis.get(cacheKey)
  if (cached) return Response.json(JSON.parse(cached))

  const result = await fetch(`${BACKEND_URL}/api/predictions/predict`, {
    method: 'POST',
    body: JSON.stringify(body),
  }).then(r => r.json())

  // Cache for 5 minutes
  await redis.setex(cacheKey, 300, JSON.stringify(result))

  return Response.json(result)
}
```

## SEO & Metadata

```typescript
// app/page.tsx

export const metadata: Metadata = {
  title: 'NFL AI Predictions - Data-Driven Player Prop Analysis',
  description: 'Get AI-powered NFL player prop predictions with confidence scores, historical context, and expert analysis. Backed by 3 seasons of data.',
  openGraph: {
    title: 'NFL AI Predictions',
    description: 'AI-powered NFL prop bet analysis',
    images: ['/og-image.jpg'],
  },
}

// app/players/[playerId]/page.tsx

export async function generateMetadata({ params }): Promise<Metadata> {
  const player = await getPlayer(params.playerId)

  return {
    title: `${player.name} Predictions | NFL AI`,
    description: `AI-powered predictions for ${player.name} (${player.position}, ${player.team})`,
    openGraph: {
      images: [player.photoUrl],
    },
  }
}
```

## Accessibility

### WCAG 2.1 AA Compliance

```typescript
// All interactive elements have proper ARIA labels
<button
  aria-label={`View prediction details for ${player.name} ${statType}`}
  onClick={handleClick}
>
  View Details
</button>

// Keyboard navigation
<div
  role="tablist"
  onKeyDown={(e) => {
    if (e.key === 'ArrowRight') focusNextTab()
    if (e.key === 'ArrowLeft') focusPrevTab()
  }}
>
  {tabs.map(tab => (
    <button
      key={tab.id}
      role="tab"
      aria-selected={tab.id === activeTab}
      tabIndex={tab.id === activeTab ? 0 : -1}
    >
      {tab.label}
    </button>
  ))}
</div>

// Screen reader announcements
<div role="status" aria-live="polite" className="sr-only">
  {isLoading && "Generating prediction..."}
  {prediction && `Prediction complete: ${prediction.prediction} with ${prediction.confidence}% confidence`}
</div>

// Color contrast ratios meet AA standards (4.5:1 for normal text)
// Focus indicators visible
// All images have alt text
```

## Error Handling

```typescript
// Error boundary for component errors
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-4">
      <AlertCircle className="w-12 h-12 text-destructive mb-4" />
      <h2 className="text-2xl font-bold mb-2">Something went wrong</h2>
      <p className="text-muted-foreground mb-4">
        {error.message || "We couldn't load this page"}
      </p>
      <Button onClick={reset}>Try Again</Button>
    </div>
  )
}

// API error handling
export async function fetchPrediction(params: PredictionParams) {
  try {
    const response = await fetch('/api/predictions/predict', {
      method: 'POST',
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch prediction')
    }

    return response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Network error: Please check your connection')
  }
}
```

## Analytics & Tracking

```typescript
// Track user interactions
export function trackEvent(
  action: string,
  category: string,
  label?: string,
  value?: number
) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value,
    })
  }
}

// Usage
trackEvent('prediction_viewed', 'predictions', 'Patrick Mahomes - Passing Yards')
trackEvent('bet_tracked', 'user_actions', 'OVER', lineScore)
trackEvent('filter_applied', 'filters', 'confidence_min', 70)
```

## Testing Strategy

```typescript
// Unit tests (Vitest + React Testing Library)
describe('PredictionCard', () => {
  it('displays OVER prediction with correct confidence', () => {
    render(<PredictionCard prediction={mockOverPrediction} />)
    expect(screen.getByText('OVER')).toBeInTheDocument()
    expect(screen.getByText('68%')).toBeInTheDocument()
  })

  it('shows high confidence styling for 70%+', () => {
    render(<PredictionCard prediction={{ ...mock, confidence: 75 }} />)
    expect(screen.getByRole('progressbar')).toHaveClass('bg-confidence-high')
  })
})

// E2E tests (Playwright)
test('user can search for player and view prediction', async ({ page }) => {
  await page.goto('/')
  await page.fill('[placeholder="Search players..."]', 'Mahomes')
  await page.click('text=Patrick Mahomes')
  await expect(page).toHaveURL(/\/players\/mahomes/)
  await page.click('text=Passing Yards')
  await expect(page.locator('text=Projected')).toBeVisible()
})
```

## Development Timeline

### Phase 1: Foundation (Week 1)
- [ ] Next.js project setup
- [ ] Tailwind + shadcn/ui configuration
- [ ] API client setup
- [ ] Basic routing structure
- [ ] Design system implementation

### Phase 2: Core Features (Week 2-3)
- [ ] Prediction card component
- [ ] Player search
- [ ] Individual prediction view
- [ ] Recent form visualization
- [ ] Similar situations display

### Phase 3: Discovery Views (Week 4)
- [ ] Top picks page
- [ ] Game-by-game browse
- [ ] Filter bar
- [ ] Sort functionality
- [ ] Mobile navigation

### Phase 4: Advanced Features (Week 5)
- [ ] Bet tracking
- [ ] Player profiles
- [ ] SGP builder
- [ ] Comparison tools
- [ ] Notifications

### Phase 5: Polish & Deploy (Week 6)
- [ ] Loading states
- [ ] Error handling
- [ ] Accessibility audit
- [ ] Performance optimization
- [ ] SEO optimization
- [ ] Production deployment

## Deployment Configuration

### Environment Variables

```bash
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# .env.production (production)
NEXT_PUBLIC_API_URL=https://api.nflai.com
NEXT_PUBLIC_SITE_URL=https://nflai.com

# Optional
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
REDIS_URL=redis://...
```

### Vercel Configuration

```json
// vercel.json
{
  "buildCommand": "pnpm build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url"
  }
}
```

### Digital Ocean App Platform

```yaml
# .do/app.yaml
name: nfl-ai-frontend
services:
  - name: web
    github:
      repo: your-repo/nfl-ai
      branch: main
      deploy_on_push: true
    build_command: npm run build
    run_command: npm start
    envs:
      - key: NEXT_PUBLIC_API_URL
        value: ${api.PUBLIC_URL}
    instance_count: 1
    instance_size_slug: basic-xs
```

## Success Metrics

### Key Performance Indicators

**User Engagement**:
- Time on site
- Pages per session
- Return visitor rate
- Bet tracking adoption rate

**Prediction Quality**:
- User satisfaction ratings
- Prediction accuracy tracking
- Confidence calibration (does 70% = 70%?)

**Technical Performance**:
- Page load time <2s
- Time to interactive <3s
- Lighthouse score >90
- Zero critical accessibility violations

## Future Enhancements

### Phase 2 Features (Post-Launch)

1. **Live Tracking**: Real-time stat updates during games
2. **Prop Odds Integration**: Pull actual betting lines from APIs
3. **Line Movement Charts**: Show how lines have moved
4. **Community Features**: User comments, voting
5. **Bankroll Management**: Track bets, ROI, unit sizing
6. **Advanced Filters**: Prop builder, custom queries
7. **Push Notifications**: High-confidence alerts
8. **Dark Mode**: Theme toggle
9. **Localization**: Multi-language support
10. **Premium Features**: Advanced analytics, trends

---

**Ready to build**: Start with scaffolding and core prediction display, then iterate through browsing modes.
