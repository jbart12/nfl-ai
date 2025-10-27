import { Progress } from "@/components/ui/progress"
import { getConfidenceColor, getConfidenceLabel } from "@/lib/utils"
import { cn } from "@/lib/utils"

interface ConfidenceMeterProps {
  confidence: number
}

export function ConfidenceMeter({ confidence }: ConfidenceMeterProps) {
  const color = getConfidenceColor(confidence)
  const label = getConfidenceLabel(confidence)

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm text-muted-foreground">Confidence</span>
        <span className="text-2xl font-bold">{confidence}%</span>
      </div>
      <div className="relative">
        <div className="h-4 w-full overflow-hidden rounded-full bg-secondary">
          <div
            className={cn(
              "h-full transition-all duration-500 ease-out rounded-full",
              confidence >= 70 && "bg-confidence-high",
              confidence >= 50 && confidence < 70 && "bg-confidence-medium",
              confidence < 50 && "bg-confidence-low"
            )}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>
      <p className="text-xs text-muted-foreground text-center font-medium">
        {label} CONFIDENCE
      </p>
    </div>
  )
}
