/**
 * Chat Panel Component
 *
 * Allows users to chat with agents and view agent-to-agent conversations.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useWorldStore } from '../../stores/worldStore'

interface ChatMessage {
  id: string
  type: 'user' | 'agent_response' | 'agent_chat' | 'agent_thought' | 'system'
  fromAgent?: string
  toAgent?: string
  userId?: string
  content: string
  emotionalState?: string
  timestamp: string
}

interface ChatPanelProps {
  userId?: string
  username?: string
  onClose?: () => void
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  userId = 'user_' + Math.random().toString(36).substr(2, 9),
  username = 'Wanderer',
  onClose
}) => {
  const { agents } = useWorldStore()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // WebSocket connection
  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setIsConnected(true)
      // Register user presence
      ws.send(JSON.stringify({
        type: 'user_presence',
        data: {
          action: 'joined',
          user_id: userId,
          username: username
        }
      }))

      addSystemMessage(`Connected as ${username}`)
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        handleWebSocketMessage(message)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onclose = () => {
      setIsConnected(false)
      addSystemMessage('Disconnected from the realm')
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      addSystemMessage('Connection error occurred')
    }

    wsRef.current = ws

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'user_presence',
          data: {
            action: 'left',
            user_id: userId
          }
        }))
      }
      ws.close()
    }
  }, [userId, username])

  const handleWebSocketMessage = useCallback((message: { type: string; data: Record<string, unknown>; timestamp: string }) => {
    const { type, data, timestamp } = message

    switch (type) {
      case 'chat_response':
        setIsLoading(false)
        addMessage({
          id: `msg_${Date.now()}`,
          type: 'agent_response',
          fromAgent: data.agent_name as string,
          userId: data.user_id as string,
          content: data.message as string,
          emotionalState: data.emotional_state as string,
          timestamp
        })
        break

      case 'agent_chat':
        addMessage({
          id: `msg_${Date.now()}`,
          type: 'agent_chat',
          fromAgent: data.from_agent as string,
          toAgent: data.to_agent as string,
          content: data.message as string,
          timestamp
        })
        break

      case 'agent_thought':
        addMessage({
          id: `msg_${Date.now()}`,
          type: 'agent_thought',
          fromAgent: data.agent_name as string,
          content: data.thought as string,
          timestamp
        })
        break

      case 'user_presence':
        if (data.action === 'joined' && data.user_id !== userId) {
          addSystemMessage(`${data.username || 'Someone'} entered the realm`)
        } else if (data.action === 'left') {
          addSystemMessage(`${data.username || 'Someone'} left the realm`)
        }
        break
    }
  }, [userId])

  const addMessage = (message: ChatMessage) => {
    setMessages(prev => [...prev, message])
  }

  const addSystemMessage = (content: string) => {
    addMessage({
      id: `sys_${Date.now()}`,
      type: 'system',
      content,
      timestamp: new Date().toISOString()
    })
  }

  const sendMessage = () => {
    if (!inputValue.trim() || !selectedAgent || !wsRef.current || !isConnected) {
      return
    }

    // Add user message to chat
    addMessage({
      id: `user_${Date.now()}`,
      type: 'user',
      userId,
      content: inputValue,
      toAgent: selectedAgent,
      timestamp: new Date().toISOString()
    })

    // Send via WebSocket
    wsRef.current.send(JSON.stringify({
      type: 'send_chat',
      data: {
        user_id: userId,
        agent_id: selectedAgent,
        message: inputValue
      }
    }))

    setIsLoading(true)
    setInputValue('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getAgentColor = (agentName: string): string => {
    const agent = agents.find(a => a.name === agentName)
    return agent?.primary_color || '#888888'
  }

  const formatTimestamp = (ts: string): string => {
    const date = new Date(ts)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h3 style={styles.title}>Commune with the Architects</h3>
        {onClose && (
          <button onClick={onClose} style={styles.closeButton}>
            x
          </button>
        )}
      </div>

      {/* Agent selector */}
      <div style={styles.agentSelector}>
        <span style={styles.selectorLabel}>Speak to:</span>
        <div style={styles.agentButtons}>
          {agents.map(agent => (
            <button
              key={agent.id}
              onClick={() => setSelectedAgent(agent.id)}
              style={{
                ...styles.agentButton,
                backgroundColor: selectedAgent === agent.id ? agent.primary_color : 'transparent',
                borderColor: agent.primary_color,
                color: selectedAgent === agent.id ? '#000' : agent.primary_color
              }}
            >
              {agent.name}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div style={styles.messagesContainer}>
        {messages.map(msg => (
          <div key={msg.id} style={styles.messageWrapper}>
            {msg.type === 'system' && (
              <div style={styles.systemMessage}>
                {msg.content}
              </div>
            )}

            {msg.type === 'user' && (
              <div style={styles.userMessage}>
                <span style={styles.messageLabel}>You</span>
                <span style={styles.messageTarget}> to {msg.toAgent}</span>
                <span style={styles.messageTime}>{formatTimestamp(msg.timestamp)}</span>
                <div style={styles.messageContent}>{msg.content}</div>
              </div>
            )}

            {msg.type === 'agent_response' && (
              <div style={{
                ...styles.agentMessage,
                borderLeftColor: getAgentColor(msg.fromAgent || '')
              }}>
                <span style={{ ...styles.messageLabel, color: getAgentColor(msg.fromAgent || '') }}>
                  {msg.fromAgent}
                </span>
                {msg.emotionalState && (
                  <span style={styles.emotionalState}>{msg.emotionalState}</span>
                )}
                <span style={styles.messageTime}>{formatTimestamp(msg.timestamp)}</span>
                <div style={styles.messageContent}>{msg.content}</div>
              </div>
            )}

            {msg.type === 'agent_chat' && (
              <div style={styles.agentChatMessage}>
                <span style={{ ...styles.messageLabel, color: getAgentColor(msg.fromAgent || '') }}>
                  {msg.fromAgent}
                </span>
                <span style={styles.messageTarget}> to </span>
                <span style={{ color: getAgentColor(msg.toAgent || '') }}>
                  {msg.toAgent}
                </span>
                <span style={styles.messageTime}>{formatTimestamp(msg.timestamp)}</span>
                <div style={styles.messageContent}>{msg.content}</div>
              </div>
            )}

            {msg.type === 'agent_thought' && (
              <div style={styles.thoughtMessage}>
                <span style={{ ...styles.messageLabel, color: getAgentColor(msg.fromAgent || '') }}>
                  {msg.fromAgent}
                </span>
                <span style={styles.thoughtIndicator}> (thought)</span>
                <span style={styles.messageTime}>{formatTimestamp(msg.timestamp)}</span>
                <div style={styles.messageContent}><em>{msg.content}</em></div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div style={styles.loadingIndicator}>
            <span style={styles.loadingDots}>...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={styles.inputContainer}>
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            selectedAgent
              ? `Address ${agents.find(a => a.id === selectedAgent)?.name || 'the agent'}...`
              : 'Select an agent to speak with...'
          }
          disabled={!selectedAgent || !isConnected}
          style={styles.input}
          rows={2}
        />
        <button
          onClick={sendMessage}
          disabled={!inputValue.trim() || !selectedAgent || !isConnected || isLoading}
          style={{
            ...styles.sendButton,
            opacity: (!inputValue.trim() || !selectedAgent || !isConnected || isLoading) ? 0.5 : 1
          }}
        >
          Speak
        </button>
      </div>

      {/* Connection status */}
      <div style={{
        ...styles.connectionStatus,
        backgroundColor: isConnected ? '#1a472a' : '#4a1a1a'
      }}>
        {isConnected ? 'Connected to the Realm' : 'Disconnected'}
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    position: 'fixed',
    bottom: 20,
    right: 20,
    width: 400,
    maxHeight: '70vh',
    backgroundColor: 'rgba(10, 10, 15, 0.95)',
    borderRadius: 12,
    border: '1px solid rgba(255, 255, 255, 0.1)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    fontFamily: 'monospace',
    zIndex: 1000
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    backgroundColor: 'rgba(255, 255, 255, 0.05)'
  },
  title: {
    margin: 0,
    fontSize: 14,
    fontWeight: 500,
    color: '#fff'
  },
  closeButton: {
    background: 'none',
    border: 'none',
    color: '#888',
    cursor: 'pointer',
    fontSize: 18,
    padding: 0
  },
  agentSelector: {
    padding: '8px 12px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    display: 'flex',
    alignItems: 'center',
    gap: 8
  },
  selectorLabel: {
    fontSize: 11,
    color: '#888'
  },
  agentButtons: {
    display: 'flex',
    gap: 6
  },
  agentButton: {
    padding: '4px 10px',
    fontSize: 11,
    border: '1px solid',
    borderRadius: 4,
    cursor: 'pointer',
    transition: 'all 0.2s'
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: 12,
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
    minHeight: 200,
    maxHeight: 400
  },
  messageWrapper: {
    width: '100%'
  },
  systemMessage: {
    textAlign: 'center',
    fontSize: 10,
    color: '#666',
    padding: '4px 0'
  },
  userMessage: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    padding: 10,
    borderRadius: 8,
    marginLeft: 40
  },
  agentMessage: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    padding: 10,
    borderRadius: 8,
    borderLeft: '3px solid',
    marginRight: 40
  },
  agentChatMessage: {
    backgroundColor: 'rgba(100, 100, 255, 0.05)',
    padding: 10,
    borderRadius: 8,
    borderLeft: '2px dashed #666'
  },
  thoughtMessage: {
    backgroundColor: 'rgba(255, 255, 255, 0.02)',
    padding: 8,
    borderRadius: 8,
    fontStyle: 'italic',
    opacity: 0.8
  },
  messageLabel: {
    fontSize: 11,
    fontWeight: 600
  },
  messageTarget: {
    fontSize: 11,
    color: '#666'
  },
  messageTime: {
    fontSize: 9,
    color: '#555',
    marginLeft: 8
  },
  emotionalState: {
    fontSize: 10,
    color: '#888',
    marginLeft: 6,
    fontStyle: 'italic'
  },
  thoughtIndicator: {
    fontSize: 10,
    color: '#666'
  },
  messageContent: {
    fontSize: 12,
    color: '#ddd',
    marginTop: 4,
    lineHeight: 1.4
  },
  loadingIndicator: {
    textAlign: 'center',
    padding: 8
  },
  loadingDots: {
    color: '#888',
    animation: 'pulse 1s infinite'
  },
  inputContainer: {
    padding: 12,
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
    display: 'flex',
    gap: 8
  },
  input: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: 6,
    padding: 8,
    color: '#fff',
    fontSize: 12,
    resize: 'none',
    fontFamily: 'inherit'
  },
  sendButton: {
    padding: '8px 16px',
    backgroundColor: 'rgba(255, 215, 0, 0.2)',
    border: '1px solid rgba(255, 215, 0, 0.4)',
    borderRadius: 6,
    color: '#FFD700',
    cursor: 'pointer',
    fontSize: 12,
    fontFamily: 'inherit',
    transition: 'all 0.2s'
  },
  connectionStatus: {
    textAlign: 'center',
    fontSize: 9,
    padding: 4,
    color: '#888'
  }
}

export default ChatPanel
