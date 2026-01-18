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
  // Shape system - agents deterministically choose their form
  shape_preset?: string
  custom_shape_config?: ShapeConfig
}

// Shape configuration for agent forms
export interface ShapeConfig {
  type: ShapeType
  args: number[]
  wireframe?: boolean
  metalness?: number
  roughness?: number
  emissiveIntensity?: number
  animation?: 'spin' | 'pulse' | 'float' | 'morph' | 'glitch'
  scale?: number
}

export type ShapeType =
  | 'icosahedron'
  | 'octahedron'
  | 'dodecahedron'
  | 'tetrahedron'
  | 'cube'
  | 'sphere'
  | 'torus'
  | 'torusKnot'
  | 'cone'
  | 'cylinder'
  | 'capsule'
  | 'ring'
  | 'star'
  | 'spiral'
  | 'fractal'
  | 'void'
  | 'flux'

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

// Chat types
export type EmotionalState =
  | 'neutral'
  | 'curious'
  | 'pleased'
  | 'concerned'
  | 'excited'
  | 'contemplative'
  | 'frustrated'
  | 'inspired'

export interface ChatMessage {
  id: string
  type: 'user_message' | 'agent_response' | 'agent_to_agent' | 'agent_thought'
  from_entity: string
  to_entity: string
  content: string
  emotional_state?: EmotionalState
  timestamp: string
  conversation_id?: string
}

export interface Conversation {
  id: string
  participants: string[]
  topic?: string
  started_at: string
  is_active: boolean
}

export interface ActiveUser {
  user_id: string
  username: string
  connected_at: string
  last_active: string
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
  | 'chat_message'
  | 'chat_response'
  | 'agent_chat'
  | 'agent_thought'
  | 'agent_action'
  | 'user_presence'
  | 'send_chat'

export interface WSMessage {
  type: WSMessageType
  data: Record<string, unknown>
  timestamp: string
}
