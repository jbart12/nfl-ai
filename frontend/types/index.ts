// Core prediction types
export interface Prediction {
  player_name: string
  player_id: string
  position: string
  team: string
  opponent: string
  week: number
  stat_type: string
  line_score: number
  prediction: 'OVER' | 'UNDER'
  confidence: number
  projected_value: number
  edge: number

  reasoning: string
  key_factors: string[]
  risk_factors: string[]

  current_stats: {
    games_played: number
    avg_per_game: number
    last_3_games: number[]
    min: number
    max: number
    std_dev: number
  }

  similar_situations: SimilarSituation[]

  metadata: {
    model: string
    generated_at: string
  }
}

export interface SimilarSituation {
  id: string
  similarity_score: number
  player_name: string
  game: string
  result: string
  narrative: string
  outcome?: 'OVER' | 'UNDER'
  line?: number
}

export interface Game {
  id: string
  home_team: string
  away_team: string
  week: number
  season: number
  game_time: string
  spread?: number
  total?: number
  is_completed: boolean
  home_score?: number
  away_score?: number
}

export interface Player {
  id: string
  name: string
  position: string
  team: string
  photo_url?: string
  jersey_number?: number
}

export interface PredictionRequest {
  player_name: string
  stat_type: string
  line_score: number
  opponent?: string
}
