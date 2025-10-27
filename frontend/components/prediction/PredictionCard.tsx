import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ConfidenceMeter } from "./ConfidenceMeter"
import { formatStatType } from "@/lib/utils"
import type { Prediction } from "@/types"

interface PredictionCardProps {
  prediction: Prediction
}

export function PredictionCard({ prediction }: PredictionCardProps) {
  const edge = prediction.projected_value - prediction.line_score
  const edgeSign = edge >= 0 ? "+" : ""

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-xl mb-1">
              {prediction.player_name}
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              {prediction.position}, {prediction.team} • Week {prediction.week} vs {prediction.opponent}
            </p>
          </div>
          <Badge
            variant={prediction.prediction === 'OVER' ? 'success' : 'destructive'}
            className="text-base px-3 py-1"
          >
            {prediction.prediction}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Main Prediction */}
        <div className="text-center py-4 bg-muted/50 rounded-lg">
          <p className="text-sm text-muted-foreground mb-1">
            {formatStatType(prediction.stat_type)}
          </p>
          <p className="text-3xl font-bold mb-2">
            {prediction.prediction} {prediction.line_score}
          </p>
          <p className="text-sm text-muted-foreground">
            Projected: <span className="font-semibold">{prediction.projected_value}</span>
            {" "}
            <span className={edge >= 0 ? "text-green-600" : "text-red-600"}>
              ({edgeSign}{edge.toFixed(1)})
            </span>
          </p>
        </div>

        {/* Confidence Meter */}
        <ConfidenceMeter confidence={prediction.confidence} />

        {/* TL;DR Section */}
        <div className="space-y-3">
          <div className="flex items-start gap-2">
            <span className="text-lg">💡</span>
            <div className="flex-1">
              <p className="font-medium text-sm mb-1">TL;DR</p>
              {prediction.key_factors.length > 0 && (
                <p className="text-sm text-muted-foreground">
                  {prediction.key_factors[0]}
                </p>
              )}
              {prediction.risk_factors.length > 0 && (
                <p className="text-sm text-orange-600 dark:text-orange-400 mt-1">
                  Risk: {prediction.risk_factors[0]}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Season Stats */}
        <div className="space-y-2">
          <p className="text-sm font-medium">2025 Season Stats</p>
          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="p-2 bg-muted/50 rounded">
              <p className="text-xs text-muted-foreground">Games</p>
              <p className="text-lg font-semibold">{prediction.current_stats.games_played}</p>
            </div>
            <div className="p-2 bg-muted/50 rounded">
              <p className="text-xs text-muted-foreground">Average</p>
              <p className="text-lg font-semibold">{prediction.current_stats.avg_per_game.toFixed(1)}</p>
            </div>
            <div className="p-2 bg-muted/50 rounded">
              <p className="text-xs text-muted-foreground">Range</p>
              <p className="text-lg font-semibold">
                {prediction.current_stats.min}-{prediction.current_stats.max}
              </p>
            </div>
          </div>
        </div>

        {/* View Details Button */}
        <button className="w-full py-2 px-4 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
          View Full Analysis →
        </button>
      </CardContent>
    </Card>
  )
}
