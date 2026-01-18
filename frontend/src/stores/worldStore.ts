import { create } from 'zustand'
import type {
  Agent,
  Structure,
  WorldEffect,
  Weather,
  DebateState,
  DebatePhase,
  Proposal,
  Challenge,
  Vote
} from '../types'

interface WorldState {
  // Connection
  isConnected: boolean
  isLoading: boolean

  // World state
  cycleNumber: number
  agents: Agent[]
  structures: Structure[]
  effects: WorldEffect[]
  weather: Weather

  // Debate state
  debate: DebateState

  // Actions
  setConnected: (connected: boolean) => void
  setLoading: (loading: boolean) => void
  setCycleNumber: (cycle: number) => void
  setAgents: (agents: Agent[]) => void
  updateAgent: (agent: Partial<Agent> & { id: string }) => void
  addStructure: (structure: Structure) => void
  addEffect: (effect: WorldEffect) => void
  removeEffect: (effectId: string) => void
  setWeather: (weather: Weather) => void
  setDebatePhase: (phase: DebatePhase) => void
  setProposal: (proposal: Proposal | null) => void
  addChallenge: (challenge: Challenge) => void
  addVote: (vote: Vote) => void
  setDebateOutcome: (outcome: string) => void
  resetDebate: () => void
}

const initialDebateState: DebateState = {
  phase: 'idle',
  proposal: null,
  challenges: [],
  votes: {},
  outcome: null
}

// Default agents for offline/demo mode
const defaultAgents: Agent[] = [
  {
    id: 'axioma-default',
    name: 'Axioma',
    archetype: 'order',
    position: { x: -15, y: 0, z: 0 },
    rotation_y: 0,
    current_animation: 'idle',
    primary_color: '#FFD700',
    secondary_color: '#FFFFFF',
    glow_intensity: 1.2,
    influence_score: 100,
    proposals_made: 5,
    proposals_accepted: 3,
    shape_preset: 'crystal_perfect'
  },
  {
    id: 'veridicus-default',
    name: 'Veridicus',
    archetype: 'logic',
    position: { x: 15, y: 0, z: 0 },
    rotation_y: 0,
    current_animation: 'idle',
    primary_color: '#4169E1',
    secondary_color: '#C0C0C0',
    glow_intensity: 0.9,
    influence_score: 100,
    proposals_made: 4,
    proposals_accepted: 2,
    shape_preset: 'logical_cube'
  },
  {
    id: 'paradoxia-default',
    name: 'Paradoxia',
    archetype: 'chaos',
    position: { x: 0, y: 0, z: 15 },
    rotation_y: 0,
    current_animation: 'idle',
    primary_color: '#FF00FF',
    secondary_color: '#00FFFF',
    glow_intensity: 1.5,
    influence_score: 100,
    proposals_made: 6,
    proposals_accepted: 2,
    shape_preset: 'chaos_knot'
  }
]

// Demo structures for offline mode
const defaultStructures: Structure[] = [
  {
    id: 'temple-order-1',
    structure_type: 'temple',
    name: 'Temple of Sacred Order',
    position: { x: -25, y: 0, z: -10 },
    rotation_y: 45,
    scale: 1.2,
    model_path: null,
    material_preset: 'crystal',
    primary_color: '#FFD700',
    glow_enabled: true,
    created_by: 'axioma-default',
    created_at_cycle: 1
  },
  {
    id: 'obelisk-1',
    structure_type: 'obelisk',
    name: 'Obelisk of Truth',
    position: { x: -20, y: 0, z: 5 },
    rotation_y: 0,
    scale: 1,
    model_path: null,
    material_preset: 'sacred_gold',
    primary_color: '#FFD700',
    glow_enabled: true,
    created_by: 'axioma-default',
    created_at_cycle: 2
  },
  {
    id: 'archive-1',
    structure_type: 'archive',
    name: 'Data Archive',
    position: { x: 25, y: 0, z: -8 },
    rotation_y: -30,
    scale: 1,
    model_path: null,
    material_preset: 'data_glass',
    primary_color: '#4169E1',
    glow_enabled: true,
    created_by: 'veridicus-default',
    created_at_cycle: 1
  },
  {
    id: 'tower-1',
    structure_type: 'tower',
    name: 'Logic Tower',
    position: { x: 20, y: 0, z: 8 },
    rotation_y: 15,
    scale: 0.8,
    model_path: null,
    material_preset: 'truth_metal',
    primary_color: '#C0C0C0',
    glow_enabled: false,
    created_by: 'veridicus-default',
    created_at_cycle: 3
  },
  {
    id: 'portal-1',
    structure_type: 'portal',
    name: 'Paradox Gate',
    position: { x: 5, y: 0, z: 25 },
    rotation_y: 0,
    scale: 1,
    model_path: null,
    material_preset: 'ethereal',
    primary_color: '#FF00FF',
    glow_enabled: true,
    created_by: 'paradoxia-default',
    created_at_cycle: 2
  },
  {
    id: 'rift-1',
    structure_type: 'rift',
    name: 'Reality Tear',
    position: { x: -8, y: 2, z: 20 },
    rotation_y: 45,
    scale: 1,
    model_path: null,
    material_preset: 'glitch',
    primary_color: '#00FFFF',
    glow_enabled: true,
    created_by: 'paradoxia-default',
    created_at_cycle: 4
  },
  {
    id: 'floating-1',
    structure_type: 'floating_symbol',
    name: 'Symbol of Unity',
    position: { x: 0, y: 0, z: 0 },
    rotation_y: 0,
    scale: 0.8,
    model_path: null,
    material_preset: 'crystal',
    primary_color: '#FFFFFF',
    glow_enabled: true,
    created_by: null,
    created_at_cycle: 1
  },
  {
    id: 'shrine-1',
    structure_type: 'shrine',
    name: 'Shrine of Balance',
    position: { x: 0, y: 0, z: -20 },
    rotation_y: 180,
    scale: 1,
    model_path: null,
    material_preset: 'stone',
    primary_color: '#808080',
    glow_enabled: false,
    created_by: null,
    created_at_cycle: 1
  }
]

export const useWorldStore = create<WorldState>((set) => ({
  // Initial state
  isConnected: false,
  isLoading: true,
  cycleNumber: 5,
  agents: defaultAgents,
  structures: defaultStructures,
  effects: [],
  weather: { type: 'clear', intensity: 0.5, parameters: {} },
  debate: initialDebateState,

  // Actions
  setConnected: (connected) => set({ isConnected: connected }),

  setLoading: (loading) => set({ isLoading: loading }),

  setCycleNumber: (cycle) => set({ cycleNumber: cycle }),

  setAgents: (agents) => set({ agents }),

  updateAgent: (update) => set((state) => ({
    agents: state.agents.map((agent) =>
      agent.id === update.id ? { ...agent, ...update } : agent
    )
  })),

  addStructure: (structure) => set((state) => ({
    structures: [...state.structures, structure]
  })),

  addEffect: (effect) => set((state) => ({
    effects: [...state.effects, effect]
  })),

  removeEffect: (effectId) => set((state) => ({
    effects: state.effects.filter(e => e.id !== effectId)
  })),

  setWeather: (weather) => set({ weather }),

  setDebatePhase: (phase) => set((state) => ({
    debate: { ...state.debate, phase }
  })),

  setProposal: (proposal) => set((state) => ({
    debate: { ...state.debate, proposal }
  })),

  addChallenge: (challenge) => set((state) => ({
    debate: {
      ...state.debate,
      challenges: [...state.debate.challenges, challenge]
    }
  })),

  addVote: (vote) => set((state) => ({
    debate: {
      ...state.debate,
      votes: { ...state.debate.votes, [vote.agent_name]: vote }
    }
  })),

  setDebateOutcome: (outcome) => set((state) => ({
    debate: { ...state.debate, outcome }
  })),

  resetDebate: () => set({ debate: initialDebateState })
}))
