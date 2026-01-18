import { useEffect, useRef, useCallback } from 'react'
import { useWorldStore } from '../stores/worldStore'
import type { WSMessage, Agent, Structure, Proposal, Challenge, Vote, DebatePhase } from '../types'

const WS_URL = import.meta.env.DEV
  ? 'ws://localhost:8000/ws'
  : `wss://${window.location.host}/ws`

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number>()

  const {
    setConnected,
    setLoading,
    setCycleNumber,
    setAgents,
    updateAgent,
    addStructure,
    setWeather,
    setDebatePhase,
    setProposal,
    addChallenge,
    addVote,
    setDebateOutcome,
    resetDebate
  } = useWorldStore()

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WSMessage = JSON.parse(event.data)
      console.log('WS Message:', message.type, message.data)

      switch (message.type) {
        case 'world_state':
          // Initial state or full update
          if (message.data.agents) {
            setAgents(message.data.agents as Agent[])
          }
          setLoading(false)
          break

        case 'agent_update':
          updateAgent(message.data as Partial<Agent> & { id: string })
          break

        case 'structure_spawn':
          addStructure(message.data as unknown as Structure)
          break

        case 'weather_change':
          setWeather({
            type: message.data.type as string,
            intensity: message.data.intensity as number,
            parameters: message.data.parameters as Record<string, unknown>
          })
          break

        case 'debate_phase':
          setDebatePhase(message.data.phase as DebatePhase)
          break

        case 'proposal':
          setProposal(message.data as unknown as Proposal)
          break

        case 'challenge':
          addChallenge(message.data as unknown as Challenge)
          break

        case 'vote':
          addVote(message.data as unknown as Vote)
          break

        case 'debate_result':
          setDebateOutcome(message.data.outcome as string)
          break

        case 'cycle_start':
          setCycleNumber(message.data.cycle_number as number)
          resetDebate()
          break

        case 'cycle_end':
          // Cycle completed
          break

        case 'heartbeat':
          // Server is alive
          break

        case 'error':
          console.error('WebSocket error:', message.data)
          break
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error)
    }
  }, [
    setConnected, setLoading, setCycleNumber, setAgents, updateAgent,
    addStructure, setWeather, setDebatePhase, setProposal,
    addChallenge, addVote, setDebateOutcome, resetDebate
  ])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    console.log('Connecting to WebSocket...')
    const ws = new WebSocket(WS_URL)

    ws.onopen = () => {
      console.log('WebSocket connected')
      setConnected(true)

      // Request initial state
      ws.send(JSON.stringify({ type: 'request_state' }))
    }

    ws.onmessage = handleMessage

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setConnected(false)

      // Attempt reconnect after 3 seconds
      reconnectTimeoutRef.current = window.setTimeout(() => {
        connect()
      }, 3000)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    wsRef.current = ws
  }, [handleMessage, setConnected])

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  // Heartbeat
  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'heartbeat' }))
      }
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  return wsRef.current
}
