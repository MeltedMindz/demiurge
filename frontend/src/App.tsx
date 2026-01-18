import { Canvas } from '@react-three/fiber'
import { Suspense, useState } from 'react'
import World from './components/World/World'
import DebatePanel from './components/UI/DebatePanel'
import AgentInfo from './components/UI/AgentInfo'
import CycleProgress from './components/UI/CycleProgress'
import LoadingScreen from './components/UI/LoadingScreen'
import ChatPanel from './components/UI/ChatPanel'
import { useWebSocket } from './hooks/useWebSocket'
import { useWorldStore } from './stores/worldStore'

function App() {
  // Connect to WebSocket
  useWebSocket()

  const { isConnected, cycleNumber } = useWorldStore()
  const [showChat, setShowChat] = useState(false)

  return (
    <div className="w-full h-full relative">
      {/* 3D World */}
      <Canvas
        shadows
        camera={{ position: [0, 30, 50], fov: 60 }}
        gl={{ antialias: true }}
      >
        <Suspense fallback={null}>
          <World />
        </Suspense>
      </Canvas>

      {/* UI Overlay */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Top bar */}
        <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-start">
          {/* Title */}
          <div className="pointer-events-auto">
            <h1 className="text-2xl font-bold tracking-wider">
              <span className="text-axioma">D</span>
              <span className="text-veridicus">E</span>
              <span className="text-paradoxia">M</span>
              <span className="text-white">IURGE</span>
            </h1>
            <p className="text-sm text-white/50">3D AI Philosophy Sandbox</p>
          </div>

          {/* Connection status & cycle */}
          <div className="pointer-events-auto flex items-center gap-4">
            <CycleProgress />
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${
              isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-400' : 'bg-red-400'
              }`} />
              <span className="text-sm">
                {isConnected ? `Cycle ${cycleNumber}` : 'Connecting...'}
              </span>
            </div>
          </div>
        </div>

        {/* Left panel - Agent info */}
        <div className="absolute left-4 top-20 bottom-4 w-72 pointer-events-auto overflow-hidden">
          <AgentInfo />
        </div>

        {/* Right panel - Debate */}
        <div className="absolute right-4 top-20 bottom-4 w-96 pointer-events-auto overflow-hidden">
          <DebatePanel />
        </div>

        {/* Chat toggle button */}
        <button
          onClick={() => setShowChat(!showChat)}
          className="absolute bottom-4 right-4 pointer-events-auto px-4 py-2 bg-gradient-to-r from-axioma/20 to-paradoxia/20 border border-white/20 rounded-lg text-white/80 hover:text-white hover:border-white/40 transition-all flex items-center gap-2"
        >
          <span className="text-lg">{showChat ? '...' : '...'}</span>
          <span className="text-sm">{showChat ? 'Close Chat' : 'Commune'}</span>
        </button>
      </div>

      {/* Chat Panel */}
      {showChat && (
        <ChatPanel
          userId={`user_${Math.random().toString(36).substr(2, 9)}`}
          username="Wanderer"
          onClose={() => setShowChat(false)}
        />
      )}

      {/* Loading screen */}
      <LoadingScreen />
    </div>
  )
}

export default App
