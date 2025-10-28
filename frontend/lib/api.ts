import type { Prediction, PredictionRequest, Player, Game, Opportunity, OpportunityFilters } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function fetchPrediction(
  request: PredictionRequest
): Promise<Prediction> {
  const response = await fetch(`${API_URL}/api/v1/predictions/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch prediction' }))
    throw new Error(error.detail || 'Failed to fetch prediction')
  }

  return response.json()
}

export async function fetchPlayer(playerId: string): Promise<Player> {
  const response = await fetch(`${API_URL}/api/v1/players/${playerId}`)

  if (!response.ok) {
    throw new Error('Failed to fetch player')
  }

  return response.json()
}

export async function fetchCurrentSchedule(): Promise<Game[]> {
  const response = await fetch(`${API_URL}/api/v1/schedule/current`)

  if (!response.ok) {
    throw new Error('Failed to fetch schedule')
  }

  return response.json()
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_URL}/health`)

  if (!response.ok) {
    throw new Error('API is not healthy')
  }

  return response.json()
}

export async function fetchOpportunities(
  filters: OpportunityFilters = {}
): Promise<Opportunity[]> {
  const params = new URLSearchParams()

  if (filters.position) params.append('position', filters.position)
  if (filters.stat_type) params.append('stat_type', filters.stat_type)
  if (filters.min_confidence !== undefined) params.append('min_confidence', filters.min_confidence.toString())
  if (filters.min_edge !== undefined) params.append('min_edge', filters.min_edge.toString())
  if (filters.sort_by) params.append('sort_by', filters.sort_by)
  if (filters.limit) params.append('limit', filters.limit.toString())

  const url = `${API_URL}/api/v1/predictions/opportunities${params.toString() ? '?' + params.toString() : ''}`
  const response = await fetch(url)

  if (!response.ok) {
    throw new Error('Failed to fetch opportunities')
  }

  const data = await response.json()
  return data.opportunities || []
}
