import { useWorldStore } from '../../stores/worldStore'

const PHASE_LABELS: Record<string, string> = {
  idle: 'Awaiting Next Cycle',
  proposal: 'Proposal Phase',
  challenge: 'Challenge Phase',
  voting: 'Voting Phase',
  result: 'Processing Result',
  world_update: 'Updating World'
}

const VOTE_COLORS: Record<string, string> = {
  accept: 'text-green-400',
  reject: 'text-red-400',
  mutate: 'text-yellow-400',
  delay: 'text-blue-400'
}

export default function DebatePanel() {
  const { debate, cycleNumber } = useWorldStore()

  return (
    <div className="panel h-full flex flex-col">
      {/* Header */}
      <div className="panel-header flex justify-between items-center">
        <span>Debate</span>
        <span className="text-sm text-white/50">Cycle {cycleNumber}</span>
      </div>

      {/* Phase indicator */}
      <div className="px-4 py-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            debate.phase === 'idle' ? 'bg-gray-400' : 'bg-green-400 animate-pulse'
          }`} />
          <span className="font-medium">{PHASE_LABELS[debate.phase]}</span>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Current Proposal */}
        {debate.proposal && (
          <div className="space-y-2">
            <div className="text-sm text-white/50">PROPOSAL</div>
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <span className={`font-medium ${getAgentColor(debate.proposal.proposer)}`}>
                  {debate.proposal.proposer}
                </span>
                <span className="text-xs text-white/30">
                  {debate.proposal.type}
                </span>
              </div>
              <p className="text-sm text-white/80">
                {debate.proposal.content}
              </p>
            </div>
          </div>
        )}

        {/* Challenges */}
        {debate.challenges.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm text-white/50">CHALLENGES</div>
            {debate.challenges.map((challenge, i) => (
              <div
                key={i}
                className="p-3 rounded-lg bg-white/5 border border-white/10"
              >
                <div className={`font-medium mb-1 ${getAgentColor(challenge.agent_name)}`}>
                  {challenge.agent_name}
                </div>
                <p className="text-sm text-white/70">{challenge.content}</p>
              </div>
            ))}
          </div>
        )}

        {/* Votes */}
        {Object.keys(debate.votes).length > 0 && (
          <div className="space-y-2">
            <div className="text-sm text-white/50">VOTES</div>
            <div className="grid gap-2">
              {Object.values(debate.votes).map((vote) => (
                <div
                  key={vote.agent_id}
                  className="p-3 rounded-lg bg-white/5 border border-white/10"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`font-medium ${getAgentColor(vote.agent_name)}`}>
                      {vote.agent_name}
                    </span>
                    <span className={`text-sm font-bold uppercase ${VOTE_COLORS[vote.vote]}`}>
                      {vote.vote}
                    </span>
                  </div>
                  <p className="text-xs text-white/60">{vote.reasoning}</p>
                  <div className="mt-1 flex items-center gap-1">
                    <div className="text-xs text-white/40">Confidence:</div>
                    <div className="flex-1 h-1 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-white/50 rounded-full"
                        style={{ width: `${vote.confidence * 100}%` }}
                      />
                    </div>
                    <div className="text-xs text-white/40">
                      {Math.round(vote.confidence * 100)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Outcome */}
        {debate.outcome && (
          <div className="space-y-2">
            <div className="text-sm text-white/50">OUTCOME</div>
            <div className={`p-4 rounded-lg text-center font-bold uppercase ${
              debate.outcome === 'accepted' ? 'bg-green-500/20 text-green-400' :
              debate.outcome === 'rejected' ? 'bg-red-500/20 text-red-400' :
              debate.outcome === 'mutated' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-blue-500/20 text-blue-400'
            }`}>
              {debate.outcome}
            </div>
          </div>
        )}

        {/* Empty state */}
        {debate.phase === 'idle' && !debate.proposal && (
          <div className="flex items-center justify-center h-32 text-white/30 text-sm">
            Waiting for next debate cycle...
          </div>
        )}
      </div>
    </div>
  )
}

function getAgentColor(name: string): string {
  switch (name) {
    case 'Axioma':
      return 'text-axioma'
    case 'Veridicus':
      return 'text-veridicus'
    case 'Paradoxia':
      return 'text-paradoxia'
    default:
      return 'text-white'
  }
}
