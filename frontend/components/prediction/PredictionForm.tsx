'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface PredictionFormProps {
  onSubmit: (data: {
    player_name: string
    stat_type: string
    line_score: number
  }) => void
  isLoading?: boolean
}

export function PredictionForm({ onSubmit, isLoading }: PredictionFormProps) {
  const [playerName, setPlayerName] = useState('')
  const [statType, setStatType] = useState('passing_yards')
  const [lineScore, setLineScore] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (playerName && lineScore) {
      onSubmit({
        player_name: playerName,
        stat_type: statType,
        line_score: parseFloat(lineScore),
      })
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Get AI Prediction</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Player Name
            </label>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder="Patrick Mahomes"
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
            <p className="text-xs text-muted-foreground mt-1">
              Enter full name (e.g., "Patrick Mahomes")
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Stat Type
            </label>
            <select
              value={statType}
              onChange={(e) => setStatType(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="passing_yards">Passing Yards</option>
              <option value="passing_touchdowns">Passing TDs</option>
              <option value="rushing_yards">Rushing Yards</option>
              <option value="rushing_touchdowns">Rushing TDs</option>
              <option value="receiving_yards">Receiving Yards</option>
              <option value="receiving_receptions">Receptions</option>
              <option value="receiving_touchdowns">Receiving TDs</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Line Score
            </label>
            <input
              type="number"
              step="0.5"
              value={lineScore}
              onChange={(e) => setLineScore(e.target.value)}
              placeholder="265.5"
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
            <p className="text-xs text-muted-foreground mt-1">
              The betting line you want to analyze
            </p>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary text-primary-foreground px-6 py-3 rounded-lg font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Analyzing...
              </span>
            ) : (
              'Generate Prediction'
            )}
          </button>
        </form>
      </CardContent>
    </Card>
  )
}
