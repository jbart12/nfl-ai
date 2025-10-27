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

        {/* Setup Instructions */}
        <div className="mt-12 p-6 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800">
          <h3 className="text-lg font-semibold mb-3">🚀 Backend Setup Required</h3>
          <p className="text-sm mb-3">
            To use predictions, make sure the backend API is running:
          </p>
          <ol className="space-y-2 text-sm">
            <li>1. Start PostgreSQL and Qdrant (see docker-compose.yml)</li>
            <li>2. Navigate to backend directory</li>
            <li>3. Run: <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">uvicorn app.main:app --reload</code></li>
            <li>4. API should be available at http://localhost:8000</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
