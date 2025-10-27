import type { Prediction, PredictionRequest, Player, Game } from '@/types'

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
