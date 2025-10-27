import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface RecentFormProps {
  games: number[]
  lineScore: number
  week: number
  label?: string
}

export function RecentForm({ games, lineScore, week, label = "Last 5 Games" }: RecentFormProps) {
  const maxValue = Math.max(...games, lineScore)
  const minGames = Math.min(games.length, 5)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">📊 {label}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {games.slice(-minGames).reverse().map((value, index) => {
            const weekNum = week - index - 1
            const isOver = value > lineScore
            const percentage = (value / maxValue) * 100

            return (
              <div key={index} className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground w-12">
                  Week {weekNum}
                </span>
                <div className="flex-1 relative h-8 bg-secondary rounded overflow-hidden">
                  <div
                    className={cn(
                      "h-full transition-all duration-300 rounded",
                      isOver ? "bg-over" : "bg-under"
                    )}
                    style={{ width: `${percentage}%` }}
                  />
                  <span className="absolute left-2 top-1/2 -translate-y-1/2 text-xs font-medium text-white mix-blend-difference">
                    {value}
                  </span>
                </div>
                <div className="w-4">
                  {isOver ? (
                    <span className="text-green-600 text-lg">✓</span>
                  ) : (
                    <span className="text-red-600 text-lg">✗</span>
                  )}
                </div>
              </div>
            )
          })}
          <div className="pt-2 border-t flex items-center gap-3">
            <span className="text-xs text-muted-foreground w-12">Line</span>
            <div className="flex-1 text-xs font-medium text-muted-foreground">
              {lineScore}
            </div>
          </div>
        </div>

        {/* Trend Indicator */}
        {games.length >= 3 && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm">
              🔥 <span className="font-medium">Trend:</span>{" "}
              {(() => {
                const last3 = games.slice(-3)
                const avg3 = last3.reduce((a, b) => a + b, 0) / last3.length
                const allAvg = games.reduce((a, b) => a + b, 0) / games.length
                const diff = avg3 - allAvg

                if (diff > 10) return <span className="text-green-600">HOT 📈 (+{diff.toFixed(1)} vs season avg)</span>
                if (diff < -10) return <span className="text-red-600">COLD 📉 ({diff.toFixed(1)} vs season avg)</span>
                return <span className="text-muted-foreground">Steady →</span>
              })()}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
