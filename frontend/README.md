# NFL AI Frontend

Next.js web application for browsing AI-powered NFL player prop predictions.

## Quick Start

```bash
# Install dependencies
npm install
# or
pnpm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Run development server
npm run dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                  # Next.js 14+ App Router pages
│   ├── page.tsx         # Discovery view (Top Picks)
│   ├── games/           # Game-by-game browsing
│   ├── players/         # Player profiles
│   ├── search/          # Player search
│   └── tracked/         # User's tracked bets
├── components/          # React components
│   ├── prediction/      # Prediction display components
│   ├── stats/           # Statistical visualizations
│   ├── game/            # Game-related components
│   └── layout/          # Layout components (Header, Nav)
├── lib/                 # Utilities and API client
│   ├── api.ts          # API client functions
│   └── utils.ts        # Helper functions
├── types/              # TypeScript type definitions
│   └── index.ts        # All interfaces
└── hooks/              # Custom React hooks
    └── usePrediction.ts # Data fetching hooks
```

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Features Implemented

### Phase 1 (Current)
- ✅ Project scaffolding
- ✅ Type definitions
- ✅ API client setup
- ✅ Core prediction card component
- ✅ Discovery page (Top Picks)
- ✅ Responsive layout

### Phase 2 (Next)
- [ ] Game-by-game browsing
- [ ] Player search
- [ ] Filter bar
- [ ] Similar situations display
- [ ] Bet tracking

### Phase 3 (Future)
- [ ] Same Game Parlay builder
- [ ] Player profiles
- [ ] Live tracking
- [ ] Notifications

## Technology Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Data Fetching**: TanStack Query (React Query)
- **State**: Zustand
- **Charts**: Recharts
- **Icons**: Lucide React

## Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run production server
npm start

# Lint code
npm run lint
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Digital Ocean App Platform

See `DEPLOYMENT_GUIDE.md` in the project root for detailed instructions.

## API Integration

The frontend expects the FastAPI backend to be running on the URL specified in `NEXT_PUBLIC_API_URL`.

### Required Endpoints

- `POST /api/predictions/predict` - Get prediction for player prop
- `GET /api/players/{player_id}` - Get player details
- `GET /api/schedule/current` - Get current week schedule
- `GET /health` - Health check

### Future Endpoints

These will need to be added to the backend:

- `GET /api/predictions/week/{week}` - All predictions for a week
- `GET /api/predictions/game/{game_id}` - All predictions for a game
- `GET /api/predictions/top` - Highest confidence predictions

## Contributing

See `FRONTEND_PLAN.md` for the complete design and architecture documentation.
