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

        {/* Demo Section */}
        <div className="bg-muted/50 p-8 rounded-lg border">
          <h3 className="text-2xl font-bold mb-4">Try a Prediction</h3>
          <p className="text-muted-foreground mb-6">
            The frontend is ready! Connect to the backend API to start generating predictions.
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Player</label>
              <input
                type="text"
                placeholder="Patrick Mahomes"
                className="w-full px-4 py-2 border rounded-lg"
                disabled
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Stat Type</label>
              <select className="w-full px-4 py-2 border rounded-lg" disabled>
                <option>Passing Yards</option>
                <option>Rushing Yards</option>
                <option>Receiving Yards</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Line</label>
              <input
                type="number"
                placeholder="265.5"
                className="w-full px-4 py-2 border rounded-lg"
                disabled
              />
            </div>

            <button
              className="w-full bg-primary text-primary-foreground px-6 py-3 rounded-lg font-semibold opacity-50 cursor-not-allowed"
              disabled
            >
              Get Prediction
            </button>

            <p className="text-sm text-muted-foreground text-center">
              💡 Install dependencies and start the backend API to enable predictions
            </p>
          </div>
        </div>

        {/* Setup Instructions */}
        <div className="mt-12 p-6 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800">
          <h3 className="text-lg font-semibold mb-3">🚀 Quick Setup</h3>
          <ol className="space-y-2 text-sm">
            <li>1. Install dependencies: <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">pnpm install</code></li>
            <li>2. Copy <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">.env.example</code> to <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">.env.local</code></li>
            <li>3. Start backend API (port 8000)</li>
            <li>4. Run <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">pnpm dev</code></li>
          </ol>
        </div>
      </div>
    </div>
  )
}
