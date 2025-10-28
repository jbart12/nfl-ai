import Link from 'next/link'

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            AI-Powered NFL Predictions
          </h2>
          <p className="text-xl text-muted-foreground mb-8">
            Discover the best betting opportunities with data-driven analysis
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/opportunities"
              className="inline-block bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition-all shadow-lg"
            >
              View Opportunities →
            </Link>
            <Link
              href="/predict"
              className="inline-block bg-primary text-primary-foreground px-8 py-3 rounded-lg font-semibold hover:bg-primary/90 transition-colors"
            >
              Search Player
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="p-6 border rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950">
            <div className="text-3xl mb-3">🎯</div>
            <h3 className="text-lg font-semibold mb-2">Automated Discovery</h3>
            <p className="text-muted-foreground">
              System generates predictions every 6 hours for all notable props - no manual searching needed
            </p>
          </div>

          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-3">📊</div>
            <h3 className="text-lg font-semibold mb-2">Edge Calculation</h3>
            <p className="text-muted-foreground">
              Instantly see which props offer the best value with projected value vs. line comparison
            </p>
          </div>

          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-3">🤖</div>
            <h3 className="text-lg font-semibold mb-2">AI-Powered Analysis</h3>
            <p className="text-muted-foreground">
              Claude Sonnet 4.5 analyzes player stats, trends, and matchups using 1,300+ game narratives
            </p>
          </div>

          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-3">🔍</div>
            <h3 className="text-lg font-semibold mb-2">Smart Filtering</h3>
            <p className="text-muted-foreground">
              Filter by position, stat type, confidence, and edge to find your perfect opportunities
            </p>
          </div>
        </div>

        {/* Example Section */}
        <div className="bg-muted/50 p-8 rounded-lg border">
          <h3 className="text-2xl font-bold mb-4">How It Works</h3>
          <ol className="space-y-4">
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">
                1
              </span>
              <div>
                <h4 className="font-semibold mb-1">Automated Prediction Generation</h4>
                <p className="text-sm text-muted-foreground">
                  Every 6 hours, the system analyzes upcoming games and generates predictions for all notable props
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">
                2
              </span>
              <div>
                <h4 className="font-semibold mb-1">Browse Opportunities by Edge</h4>
                <p className="text-sm text-muted-foreground">
                  View predictions sorted by edge (projected value vs line) to find the best opportunities
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">
                3
              </span>
              <div>
                <h4 className="font-semibold mb-1">Filter & Analyze</h4>
                <p className="text-sm text-muted-foreground">
                  Filter by position, stat type, confidence, and edge. Expand predictions to see full AI reasoning and historical context
                </p>
              </div>
            </li>
          </ol>

          <Link
            href="/opportunities"
            className="mt-6 inline-block w-full text-center bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition-all"
          >
            View Opportunities →
          </Link>
        </div>

        {/* Quick Start */}
        <div className="mt-12 p-6 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
          <h3 className="text-lg font-semibold mb-3">✅ Docker Setup Active</h3>
          <p className="text-sm mb-3">
            Everything is running via Docker Compose on unique ports:
          </p>
          <ul className="space-y-2 text-sm">
            <li>• Frontend: <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">http://localhost:13000</code></li>
            <li>• API: <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">http://localhost:18000</code></li>
            <li>• PostgreSQL: Port 15432</li>
            <li>• Qdrant: Port 16333</li>
            <li>• Redis: Port 16379</li>
          </ul>
          <p className="text-xs mt-3 text-muted-foreground">
            Start: <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">docker-compose up -d</code> •
            Stop: <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded ml-1">docker-compose down</code>
          </p>
        </div>
      </div>
    </div>
  )
}
