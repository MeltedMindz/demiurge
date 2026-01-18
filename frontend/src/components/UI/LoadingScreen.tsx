import { useState, useEffect } from 'react'
import { useWorldStore } from '../../stores/worldStore'

export default function LoadingScreen() {
  const { isLoading, isConnected, setLoading } = useWorldStore()
  const [showSkip, setShowSkip] = useState(false)

  // Show skip button after 3 seconds
  useEffect(() => {
    const timer = setTimeout(() => setShowSkip(true), 3000)
    return () => clearTimeout(timer)
  }, [])

  const handleSkip = () => {
    setLoading(false)
  }

  if (!isLoading && isConnected) {
    return null
  }

  // Allow dismissing if user clicks skip
  if (!isLoading) {
    return null
  }

  return (
    <div className="absolute inset-0 bg-black/90 flex items-center justify-center z-50">
      <div className="text-center">
        {/* Animated logo */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            {/* Outer ring */}
            <div className="w-24 h-24 rounded-full border-2 border-white/20 animate-spin" style={{ animationDuration: '3s' }}>
              <div className="absolute top-0 left-1/2 w-2 h-2 -translate-x-1/2 -translate-y-1 rounded-full bg-axioma" />
            </div>

            {/* Middle ring */}
            <div className="absolute inset-2 rounded-full border-2 border-white/30 animate-spin" style={{ animationDuration: '2s', animationDirection: 'reverse' }}>
              <div className="absolute top-0 left-1/2 w-2 h-2 -translate-x-1/2 -translate-y-1 rounded-full bg-veridicus" />
            </div>

            {/* Inner ring */}
            <div className="absolute inset-4 rounded-full border-2 border-white/40 animate-spin" style={{ animationDuration: '1.5s' }}>
              <div className="absolute top-0 left-1/2 w-2 h-2 -translate-x-1/2 -translate-y-1 rounded-full bg-paradoxia" />
            </div>

            {/* Center */}
            <div className="absolute inset-8 rounded-full bg-white/10 flex items-center justify-center">
              <div className="w-4 h-4 rounded-full bg-white animate-pulse" />
            </div>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold tracking-wider mb-2">
          <span className="text-axioma">D</span>
          <span className="text-veridicus">E</span>
          <span className="text-paradoxia">M</span>
          <span className="text-white">IURGE</span>
        </h1>

        {/* Subtitle */}
        <p className="text-white/50 mb-4">3D AI Philosophy Sandbox</p>

        {/* Status */}
        <p className="text-sm text-white/30 mb-4">
          {isConnected ? 'Loading world...' : 'Connecting to server...'}
        </p>

        {/* Skip button */}
        {showSkip && !isConnected && (
          <button
            onClick={handleSkip}
            className="px-6 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-white/70 hover:text-white transition-all"
          >
            Explore Without Server
          </button>
        )}
      </div>
    </div>
  )
}
