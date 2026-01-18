import { useEffect, useState } from 'react'
import { useWorldStore } from '../../stores/worldStore'

const PHASE_DURATIONS: Record<string, number> = {
  proposal: 15,
  challenge: 20,
  voting: 15,
  result: 10,
  world_update: 5
}

export default function CycleProgress() {
  const { debate } = useWorldStore()
  const [progress, setProgress] = useState(0)
  const [timeLeft, setTimeLeft] = useState(0)

  useEffect(() => {
    if (debate.phase === 'idle') {
      setProgress(0)
      setTimeLeft(0)
      return
    }

    const duration = PHASE_DURATIONS[debate.phase] || 10
    let elapsed = 0

    const interval = setInterval(() => {
      elapsed += 0.1
      const newProgress = Math.min((elapsed / duration) * 100, 100)
      setProgress(newProgress)
      setTimeLeft(Math.max(0, Math.ceil(duration - elapsed)))
    }, 100)

    return () => clearInterval(interval)
  }, [debate.phase])

  if (debate.phase === 'idle') {
    return null
  }

  return (
    <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-black/50 border border-white/10">
      {/* Phase name */}
      <div className="text-sm font-medium capitalize">
        {debate.phase.replace('_', ' ')}
      </div>

      {/* Progress bar */}
      <div className="w-24 h-2 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-axioma via-veridicus to-paradoxia transition-all duration-100"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Time remaining */}
      <div className="text-sm text-white/50 w-8 text-right">
        {timeLeft}s
      </div>
    </div>
  )
}
