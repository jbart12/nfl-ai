'use client'

import { useState } from 'react'
import { Opportunity } from '@/types'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ChevronDown, ChevronUp, TrendingUp, Calendar, Clock } from 'lucide-react'

interface OpportunityCardProps {
  opportunity: Opportunity
}

export function OpportunityCard({ opportunity }: OpportunityCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const formatStatType = (stat: string) => {
    return stat
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const formatGameTime = (gameTime: string | null) => {
    if (!gameTime) return 'TBD'
    const date = new Date(gameTime)
    return date.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  const getEdgeColor = (edge: number) => {
    if (edge >= 10) return 'text-green-600 bg-green-50'
    if (edge >= 5) return 'text-emerald-600 bg-emerald-50'
    if (edge >= 2) return 'text-blue-600 bg-blue-50'
    return 'text-gray-600 bg-gray-50'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'bg-green-500'
    if (confidence >= 60) return 'bg-blue-500'
    if (confidence >= 40) return 'bg-yellow-500'
    return 'bg-gray-500'
  }

  return (
    <Card className="p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-bold">{opportunity.player_name}</h3>
            <Badge variant="outline" className="text-xs">
              {opportunity.player_position}
            </Badge>
            <span className="text-sm text-gray-600">
              {opportunity.team} @ {opportunity.opponent}
            </span>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span>Week {opportunity.week}</span>
            </div>
            {opportunity.game_time && (
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{formatGameTime(opportunity.game_time)}</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm font-medium text-gray-700">
              {formatStatType(opportunity.stat_type)}
            </span>
            <span className="text-sm text-gray-500">
              Line: {opportunity.line_score}
            </span>
            <Badge
              variant={opportunity.prediction === 'OVER' ? 'default' : 'secondary'}
              className={
                opportunity.prediction === 'OVER'
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-red-600 hover:bg-red-700'
              }
            >
              {opportunity.prediction}
            </Badge>
          </div>
        </div>

        <div className="flex flex-col items-end gap-2">
          <div className={`px-4 py-2 rounded-lg font-bold text-lg ${getEdgeColor(opportunity.edge)}`}>
            <div className="flex items-center gap-1">
              <TrendingUp className="w-5 h-5" />
              <span>+{opportunity.edge.toFixed(1)}</span>
            </div>
            <div className="text-xs font-normal text-gray-600">Edge</div>
          </div>

          <div className="text-center">
            <div className="text-sm font-semibold">{opportunity.confidence}%</div>
            <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full ${getConfidenceColor(opportunity.confidence)}`}
                style={{ width: `${opportunity.confidence}%` }}
              />
            </div>
            <div className="text-xs text-gray-500 mt-1">Confidence</div>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between mb-2">
        <div className="flex-1">
          <div className="text-sm text-gray-700">
            Projected: <span className="font-semibold">{opportunity.projected_value.toFixed(1)}</span>
          </div>
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
        >
          {isExpanded ? (
            <>
              <span>Hide Details</span>
              <ChevronUp className="w-4 h-4" />
            </>
          ) : (
            <>
              <span>Show Details</span>
              <ChevronDown className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-4 pt-4 border-t space-y-4">
          <div>
            <h4 className="font-semibold text-sm mb-2">Analysis</h4>
            <p className="text-sm text-gray-700 whitespace-pre-line">{opportunity.reasoning}</p>
          </div>

          {opportunity.key_factors.length > 0 && (
            <div>
              <h4 className="font-semibold text-sm mb-2 text-green-700">Key Factors</h4>
              <ul className="list-disc list-inside space-y-1">
                {opportunity.key_factors.map((factor, idx) => (
                  <li key={idx} className="text-sm text-gray-700">
                    {factor}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {opportunity.risk_factors.length > 0 && (
            <div>
              <h4 className="font-semibold text-sm mb-2 text-red-700">Risk Factors</h4>
              <ul className="list-disc list-inside space-y-1">
                {opportunity.risk_factors.map((factor, idx) => (
                  <li key={idx} className="text-sm text-gray-700">
                    {factor}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {opportunity.comparable_game && (
            <div>
              <h4 className="font-semibold text-sm mb-2">Comparable Game</h4>
              <p className="text-sm text-gray-700">{opportunity.comparable_game}</p>
            </div>
          )}

          <div className="text-xs text-gray-500">
            Generated: {new Date(opportunity.created_at).toLocaleString()}
          </div>
        </div>
      )}
    </Card>
  )
}
