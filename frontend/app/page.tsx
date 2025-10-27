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
            Data-driven player prop analysis backed by 3 seasons of historical context
          </p>
          <Link
            href="/predict"
            className="inline-block bg-primary text-primary-foreground px-8 py-3 rounded-lg font-semibold hover:bg-primary/90 transition-colors"
          >
            Get Prediction →
          </Link>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-3">🤖</div>
            <h3 className="text-lg font-semibold mb-2">AI-Powered Analysis</h3>
            <p className="text-muted-foreground">
              Claude Sonnet 4.5 analyzes player stats, trends, and matchups to generate confident predictions
            </p>
          </div>

          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-3">📊</div>
            <h3 className="text-lg font-semibold mb-2">Historical Context</h3>
            <p className="text-muted-foreground">
              RAG system finds similar situations from 1,329 game narratives across multiple seasons
            </p>
          </div>

          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-3">🎯</div>
            <h3 className="text-lg font-semibold mb-2">Confidence Scores</h3>
            <p className="text-muted-foreground">
              Transparent confidence levels help you make informed decisions
            </p>
          </div>

          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-3">📈</div>
            <h3 className="text-lg font-semibold mb-2">Trend Analysis</h3>
            <p className="text-muted-foreground">
              Visual charts show recent form, season averages, and performance patterns
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
                <h4 className="font-semibold mb-1">Enter Player & Prop</h4>
                <p className="text-sm text-muted-foreground">
                  Search for any NFL player and select the prop you want to analyze
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">
                2
              </span>
              <div>
                <h4 className="font-semibold mb-1">AI Analyzes Data</h4>
                <p className="text-sm text-muted-foreground">
                  Our system finds similar historical situations from 1,300+ games and analyzes current season trends
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">
                3
              </span>
              <div>
                <h4 className="font-semibold mb-1">Get Prediction & Reasoning</h4>
                <p className="text-sm text-muted-foreground">
                  Receive OVER/UNDER prediction with confidence score, key factors, and full AI reasoning
                </p>
              </div>
            </li>
          </ol>

          <Link
            href="/predict"
            className="mt-6 inline-block w-full text-center bg-primary text-primary-foreground px-6 py-3 rounded-lg font-semibold hover:bg-primary/90 transition-colors"
          >
            Try it Now →
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
