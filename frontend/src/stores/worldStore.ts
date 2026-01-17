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

export const useWorldStore = create<WorldState>((set) => ({
  // Initial state
  isConnected: false,
  isLoading: true,
  cycleNumber: 0,
  agents: [],
  structures: [],
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
