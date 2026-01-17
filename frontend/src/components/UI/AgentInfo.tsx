import { useWorldStore } from '../../stores/worldStore'
import type { Agent } from '../../types'

const ARCHETYPE_DESCRIPTIONS: Record<string, string> = {
  order: 'Agent of Divine Order',
  logic: 'Agent of Logic & Truth',
  chaos: 'Agent of Creative Chaos'
}

export default function AgentInfo() {
  const { agents } = useWorldStore()

  // Default agents if none loaded
  const displayAgents: Agent[] = agents.length > 0 ? agents : [
    {
      id: 'axioma',
      name: 'Axioma',
      archetype: 'order',
      position: { x: -15, y: 0, z: 0 },
      rotation_y: 0,
      current_animation: 'idle',
      primary_color: '#FFD700',
      secondary_color: '#FFFFFF',
      glow_intensity: 1.0,
      influence_score: 100,
      proposals_made: 0,
      proposals_accepted: 0
    },
    {
      id: 'veridicus',
      name: 'Veridicus',
      archetype: 'logic',
      position: { x: 15, y: 0, z: 0 },
      rotation_y: 0,
      current_animation: 'idle',
      primary_color: '#4169E1',
      secondary_color: '#C0C0C0',
      glow_intensity: 1.0,
      influence_score: 100,
      proposals_made: 0,
      proposals_accepted: 0
    },
    {
      id: 'paradoxia',
      name: 'Paradoxia',
      archetype: 'chaos',
      position: { x: 0, y: 0, z: 15 },
      rotation_y: 0,
      current_animation: 'idle',
      primary_color: '#FF00FF',
      secondary_color: '#00FFFF',
      glow_intensity: 1.5,
      influence_score: 100,
      proposals_made: 0,
      proposals_accepted: 0
    }
  ]

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header">Agents</div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {displayAgents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  )
}

function AgentCard({ agent }: { agent: Agent }) {
  const successRate = agent.proposals_made > 0
    ? Math.round((agent.proposals_accepted / agent.proposals_made) * 100)
    : 0

  return (
    <div
      className="p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
      style={{ borderLeftColor: agent.primary_color, borderLeftWidth: 3 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div>
          <div
            className="font-bold"
            style={{ color: agent.primary_color }}
          >
            {agent.name}
          </div>
          <div className="text-xs text-white/50">
            {ARCHETYPE_DESCRIPTIONS[agent.archetype]}
          </div>
        </div>
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
          style={{
            background: `${agent.primary_color}20`,
            color: agent.primary_color
          }}
        >
          {agent.influence_score}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex justify-between">
          <span className="text-white/50">Proposals:</span>
          <span>{agent.proposals_made}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-white/50">Accepted:</span>
          <span>{agent.proposals_accepted}</span>
        </div>
      </div>

      {/* Success rate bar */}
      {agent.proposals_made > 0 && (
        <div className="mt-2">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-white/50">Success Rate</span>
            <span style={{ color: agent.primary_color }}>{successRate}%</span>
          </div>
          <div className="h-1 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${successRate}%`,
                backgroundColor: agent.primary_color
              }}
            />
          </div>
        </div>
      )}

      {/* Animation state indicator */}
      <div className="mt-2 flex items-center gap-1">
        <div
          className={`w-1.5 h-1.5 rounded-full ${
            agent.current_animation === 'idle' ? 'bg-gray-400' :
            agent.current_animation === 'proposing' ? 'bg-green-400 animate-pulse' :
            agent.current_animation === 'challenging' ? 'bg-yellow-400 animate-pulse' :
            agent.current_animation === 'voting' ? 'bg-blue-400 animate-pulse' :
            'bg-white/50'
          }`}
        />
        <span className="text-xs text-white/40 capitalize">
          {agent.current_animation}
        </span>
      </div>
    </div>
  )
}
