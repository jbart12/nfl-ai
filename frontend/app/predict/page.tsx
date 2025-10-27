'use client'

import { useState } from 'react'
import { PredictionForm } from '@/components/prediction/PredictionForm'
import { PredictionCard } from '@/components/prediction/PredictionCard'
import { SimilarSituations } from '@/components/prediction/SimilarSituations'
import { RecentForm } from '@/components/stats/RecentForm'
import { fetchPrediction } from '@/lib/api'
import type { Prediction, PredictionRequest } from '@/types'

export default function PredictPage() {
  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (data: PredictionRequest) => {
    setIsLoading(true)
    setError(null)
    setPrediction(null)

    try {
      const result = await fetchPrediction(data)
      setPrediction(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate prediction')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">NFL Prop Prediction</h1>
          <p className="text-muted-foreground">
            Get AI-powered predictions backed by historical data and advanced analytics
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Form */}
          <div className="lg:col-span-1">
            <PredictionForm onSubmit={handleSubmit} isLoading={isLoading} />

            {error && (
              <div className="mt-4 p-4 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400">
                  <strong>Error:</strong> {error}
                </p>
                <p className="text-xs text-red-500 dark:text-red-500 mt-2">
                  Make sure the backend API is running on {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                </p>
              </div>
            )}
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2 space-y-6">
            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <svg className="animate-spin h-12 w-12 text-primary mx-auto mb-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <p className="text-lg font-medium">🤖 AI Analyzing...</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    Finding similar situations and generating prediction
                  </p>
                </div>
              </div>
            )}

            {prediction && (
              <>
                <PredictionCard prediction={prediction} />

                <div className="grid md:grid-cols-2 gap-6">
                  <RecentForm
                    games={prediction.current_stats.last_3_games}
                    lineScore={prediction.line_score}
                    week={prediction.week}
                    label="Recent Performance"
                  />

                  <SimilarSituations situations={prediction.similar_situations} />
                </div>

                {/* Full Reasoning */}
                <div className="bg-muted/50 p-6 rounded-lg border">
                  <h3 className="text-lg font-semibold mb-4">AI Reasoning</h3>
                  <p className="text-sm text-muted-foreground whitespace-pre-line">
                    {prediction.reasoning}
                  </p>
                </div>

                {/* Key Factors */}
                {prediction.key_factors.length > 0 && (
                  <div className="bg-green-50 dark:bg-green-950 p-6 rounded-lg border border-green-200 dark:border-green-800">
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span>💡</span> Key Factors
                    </h3>
                    <ul className="space-y-2">
                      {prediction.key_factors.map((factor, index) => (
                        <li key={index} className="text-sm flex items-start gap-2">
                          <span className="text-green-600 dark:text-green-400">•</span>
                          <span>{factor}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Risk Factors */}
                {prediction.risk_factors.length > 0 && (
                  <div className="bg-orange-50 dark:bg-orange-950 p-6 rounded-lg border border-orange-200 dark:border-orange-800">
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <span>⚠️</span> Risk Factors
                    </h3>
                    <ul className="space-y-2">
                      {prediction.risk_factors.map((risk, index) => (
                        <li key={index} className="text-sm flex items-start gap-2">
                          <span className="text-orange-600 dark:text-orange-400">⚠</span>
                          <span>{risk}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}

            {!isLoading && !prediction && !error && (
              <div className="text-center py-12 bg-muted/30 rounded-lg border border-dashed">
                <p className="text-muted-foreground">
                  Enter a player and prop to get started
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
