// Agent types
export interface Position3D {
  x: number
  y: number
  z: number
}

export interface Agent {
  id: string
  name: string
  archetype: 'order' | 'logic' | 'chaos'
  position: Position3D
  rotation_y: number
  current_animation: string
  primary_color: string
  secondary_color: string
  glow_intensity: number
  influence_score: number
  proposals_made: number
  proposals_accepted: number
}

// World types
export interface Structure {
  id: string
  structure_type: string
  name: string | null
  position: Position3D
  rotation_y: number
  scale: number
  model_path: string | null
  material_preset: string
  primary_color: string | null
  glow_enabled: boolean
  created_by: string | null
  created_at_cycle: number
}

export interface WorldEffect {
  id: string
  effect_type: string
  position: Position3D
  parameters: Record<string, unknown>
  intensity: number
  active: boolean
}

export interface Weather {
  type: string
  intensity: number
  parameters: Record<string, unknown>
}

// Debate types
export type VoteType = 'accept' | 'reject' | 'mutate' | 'delay'
export type DebatePhase = 'idle' | 'proposal' | 'challenge' | 'voting' | 'result' | 'world_update'

export interface Proposal {
  id: string
  type: string
  content: string
  proposer: string
  proposer_id: string
}

export interface Challenge {
  agent_id: string
  agent_name: string
  content: string
  type: string
}

export interface Vote {
  agent_id: string
  agent_name: string
  vote: VoteType
  reasoning: string
  confidence: number
}

export interface DebateState {
  phase: DebatePhase
  proposal: Proposal | null
  challenges: Challenge[]
  votes: Record<string, Vote>
  outcome: string | null
}

// WebSocket message types
export type WSMessageType =
  | 'world_state'
  | 'agent_update'
  | 'structure_spawn'
  | 'weather_change'
  | 'debate_phase'
  | 'proposal'
  | 'challenge'
  | 'vote'
  | 'debate_result'
  | 'cycle_start'
  | 'cycle_end'
  | 'error'
  | 'heartbeat'

export interface WSMessage {
  type: WSMessageType
  data: Record<string, unknown>
  timestamp: string
}
