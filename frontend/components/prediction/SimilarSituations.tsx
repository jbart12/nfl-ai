import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { SimilarSituation } from "@/types"

interface SimilarSituationsProps {
  situations: SimilarSituation[]
}

export function SimilarSituations({ situations }: SimilarSituationsProps) {
  if (situations.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">🔍 Similar Situations</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No similar historical situations found.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center justify-between">
          <span>🔍 AI Found {situations.length} Similar Situations</span>
          <Badge variant="outline" className="text-xs">RAG AI</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground mb-4">
          When {situations[0]?.player_name} had similar stats and context:
        </p>

        {situations.slice(0, 3).map((situation, index) => (
          <div
            key={situation.id}
            className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <p className="font-medium text-sm">{situation.game}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Similarity: {Math.round(situation.similarity_score * 100)}%
                </p>
              </div>
              {situation.outcome && (
                <Badge
                  variant={situation.outcome === 'OVER' ? 'success' : 'destructive'}
                  className="text-xs"
                >
                  {situation.outcome}
                  {situation.line && ` (${situation.line})`}
                </Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground">
              {situation.result}
            </p>
            {situation.narrative && (
              <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                {situation.narrative}
              </p>
            )}
          </div>
        ))}

        {situations.length > 3 && (
          <button className="w-full py-2 text-sm text-primary hover:underline">
            View All {situations.length} Similar Games →
          </button>
        )}

        {/* Hit Rate */}
        {situations.some(s => s.outcome) && (
          <div className="pt-3 border-t">
            <p className="text-sm font-medium">
              Historical Hit Rate:{" "}
              <span className="text-green-600">
                {situations.filter(s => s.outcome === 'OVER').length} of {situations.length} OVER
                {" "}({Math.round((situations.filter(s => s.outcome === 'OVER').length / situations.length) * 100)}%)
              </span>
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
