import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Float, Html } from '@react-three/drei'
import * as THREE from 'three'
import type { Agent as AgentType } from '../../types'
import { useWorldStore } from '../../stores/worldStore'
import AgentGeometry from './AgentGeometry'
import HumanoidAvatar from './HumanoidAvatar'

// Display mode for agents
export type AgentDisplayMode = 'humanoid' | 'geometric' | 'hybrid'

interface AgentProps {
  agent: AgentType
  displayMode?: AgentDisplayMode
}

export default function Agent({ agent, displayMode = 'humanoid' }: AgentProps) {
  const glowRef = useRef<THREE.Mesh>(null)
  const { debate, cycleNumber } = useWorldStore()

  // Animation speed varies by archetype
  const floatConfig = useMemo(() => {
    switch (agent.archetype) {
      case 'order':
        return { speed: 2, rotationIntensity: 0.1, floatIntensity: 0.2 }
      case 'logic':
        return { speed: 1.5, rotationIntensity: 0.05, floatIntensity: 0.15 }
      case 'chaos':
        return { speed: 4, rotationIntensity: 0.5, floatIntensity: 0.5 }
      default:
        return { speed: 2, rotationIntensity: 0.2, floatIntensity: 0.3 }
    }
  }, [agent.archetype])

  // Glow pulsing animation
  useFrame((state) => {
    if (glowRef.current) {
      const intensity = agent.archetype === 'chaos'
        ? 1.5 + Math.sin(state.clock.elapsedTime * 5) * 0.3 + Math.sin(state.clock.elapsedTime * 7.3) * 0.2
        : 1.5 + Math.sin(state.clock.elapsedTime * 3) * 0.1
      glowRef.current.scale.setScalar(intensity)
    }
  })

  // Check if this agent is currently speaking
  const isSpeaking = useMemo(() => {
    if (debate.phase === 'proposal' && debate.proposal?.proposer === agent.name) {
      return true
    }
    if (debate.phase === 'challenge') {
      return debate.challenges.some(c => c.agent_name === agent.name)
    }
    if (debate.phase === 'voting') {
      return agent.name in debate.votes
    }
    return false
  }, [debate, agent.name])

  // Get current speech content
  const speechContent = useMemo(() => {
    if (debate.phase === 'proposal' && debate.proposal?.proposer === agent.name) {
      return debate.proposal.content
    }
    if (debate.phase === 'challenge') {
      const challenge = debate.challenges.find(c => c.agent_name === agent.name)
      return challenge?.content
    }
    if (debate.phase === 'voting' && agent.name in debate.votes) {
      const vote = debate.votes[agent.name]
      return `${vote.vote.toUpperCase()}: ${vote.reasoning}`
    }
    return null
  }, [debate, agent.name])

  // Determine animation type based on archetype and state
  const animationType = useMemo(() => {
    if (agent.archetype === 'chaos') {
      return isSpeaking ? 'glitch' : 'morph'
    }
    if (agent.archetype === 'order') {
      return 'spin'
    }
    return isSpeaking ? 'pulse' : 'float'
  }, [agent.archetype, isSpeaking])

  // Determine emotional state for avatar
  const emotionalState = useMemo(() => {
    if (isSpeaking) return 'excited'
    return 'neutral'
  }, [isSpeaking])

  return (
    <group position={[agent.position.x, 0, agent.position.z]}>
      {/* Humanoid Avatar Mode */}
      {displayMode === 'humanoid' && (
        <HumanoidAvatar
          archetype={agent.archetype}
          position={[0, 0, 0]}
          rotation={[0, agent.rotation_y, 0]}
          isTalking={isSpeaking}
          emotionalState={emotionalState}
          primaryColor={agent.primary_color}
          glowIntensity={agent.glow_intensity}
        />
      )}

      {/* Geometric Mode - Original abstract forms */}
      {displayMode === 'geometric' && (
        <Float
          speed={floatConfig.speed}
          rotationIntensity={floatConfig.rotationIntensity}
          floatIntensity={floatConfig.floatIntensity}
          enabled={true}
        >
          <group position={[0, 1.5, 0]}>
            <AgentGeometry
              shapePreset={agent.shape_preset}
              customConfig={agent.custom_shape_config}
              archetype={agent.archetype}
              primaryColor={agent.primary_color}
              influenceScore={agent.influence_score}
              proposalsAccepted={agent.proposals_accepted}
              cycleNumber={cycleNumber}
              animation={animationType}
            />

            <mesh ref={glowRef} scale={1.5}>
              <sphereGeometry args={[1, 16, 16]} />
              <meshBasicMaterial
                color={agent.primary_color}
                transparent
                opacity={0.1 * agent.glow_intensity}
                side={THREE.BackSide}
              />
            </mesh>
          </group>
        </Float>
      )}

      {/* Hybrid Mode - Humanoid with floating geometric element */}
      {displayMode === 'hybrid' && (
        <>
          <HumanoidAvatar
            archetype={agent.archetype}
            position={[0, 0, 0]}
            rotation={[0, agent.rotation_y, 0]}
            isTalking={isSpeaking}
            emotionalState={emotionalState}
            primaryColor={agent.primary_color}
            glowIntensity={agent.glow_intensity * 0.5}
          />
          <Float
            speed={floatConfig.speed * 1.5}
            rotationIntensity={floatConfig.rotationIntensity * 2}
            floatIntensity={0.3}
            enabled={true}
          >
            <group position={[0, 3, 0]} scale={0.3}>
              <AgentGeometry
                shapePreset={agent.shape_preset}
                customConfig={agent.custom_shape_config}
                archetype={agent.archetype}
                primaryColor={agent.primary_color}
                influenceScore={agent.influence_score}
                proposalsAccepted={agent.proposals_accepted}
                cycleNumber={cycleNumber}
                animation={animationType}
              />
            </group>
          </Float>
        </>
      )}

      {/* Glow effect for humanoid modes */}
      {(displayMode === 'humanoid' || displayMode === 'hybrid') && (
        <mesh ref={glowRef} position={[0, 1, 0]} scale={2}>
          <sphereGeometry args={[1, 16, 16]} />
          <meshBasicMaterial
            color={agent.primary_color}
            transparent
            opacity={0.05 * agent.glow_intensity}
            side={THREE.BackSide}
          />
        </mesh>
      )}

      {/* Name label */}
      <Html
        position={[0, 3.5, 0]}
        center
        style={{
          color: agent.primary_color,
          fontWeight: 'bold',
          fontSize: '14px',
          textShadow: `0 0 10px ${agent.primary_color}`,
          whiteSpace: 'nowrap',
          pointerEvents: 'none'
        }}
      >
        {agent.name}
      </Html>

      {/* Speech bubble */}
      {isSpeaking && speechContent && (
        <Html
          position={[0, 5, 0]}
          center
          style={{
            background: 'rgba(0,0,0,0.9)',
            border: `1px solid ${agent.primary_color}`,
            borderRadius: '8px',
            padding: '12px 16px',
            maxWidth: '250px',
            color: '#fff',
            fontSize: '12px',
            lineHeight: '1.4',
            boxShadow: `0 0 20px ${agent.primary_color}40`,
            pointerEvents: 'none'
          }}
        >
          {speechContent.length > 150
            ? speechContent.slice(0, 150) + '...'
            : speechContent}
        </Html>
      )}

      {/* Ground marker - archetype-specific pattern */}
      <group position={[0, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        {agent.archetype === 'order' && (
          <>
            {/* Sacred geometry pattern for order */}
            <mesh>
              <ringGeometry args={[1.5, 2, 6]} />
              <meshBasicMaterial color={agent.primary_color} transparent opacity={0.3} />
            </mesh>
            <mesh rotation={[0, 0, Math.PI / 6]}>
              <ringGeometry args={[1.8, 2.2, 6]} />
              <meshBasicMaterial color={agent.primary_color} transparent opacity={0.2} />
            </mesh>
          </>
        )}
        {agent.archetype === 'logic' && (
          <>
            {/* Grid pattern for logic */}
            <mesh>
              <ringGeometry args={[1.5, 2, 4]} />
              <meshBasicMaterial color={agent.primary_color} transparent opacity={0.3} />
            </mesh>
            <mesh rotation={[0, 0, Math.PI / 4]}>
              <ringGeometry args={[1.0, 1.4, 4]} />
              <meshBasicMaterial color={agent.primary_color} transparent opacity={0.2} />
            </mesh>
          </>
        )}
        {agent.archetype === 'chaos' && (
          <>
            {/* Irregular pattern for chaos */}
            <mesh>
              <ringGeometry args={[1.5, 2, 7]} />
              <meshBasicMaterial color={agent.primary_color} transparent opacity={0.3} />
            </mesh>
            <mesh rotation={[0, 0, Math.PI / 3]}>
              <ringGeometry args={[1.2, 1.6, 5]} />
              <meshBasicMaterial color={agent.secondary_color} transparent opacity={0.25} />
            </mesh>
          </>
        )}
      </group>
    </group>
  )
}
