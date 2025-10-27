import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 70) return 'confidence-high'
  if (confidence >= 50) return 'confidence-medium'
  return 'confidence-low'
}

export function getConfidenceLabel(confidence: number): string {
  if (confidence >= 70) return 'HIGH'
  if (confidence >= 50) return 'MODERATE'
  return 'LOW'
}

export function formatStatType(statType: string): string {
  return statType
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  })
}
