import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Float, Html } from '@react-three/drei'
import * as THREE from 'three'
import type { Agent as AgentType } from '../../types'
import { useWorldStore } from '../../stores/worldStore'

interface AgentProps {
  agent: AgentType
}

export default function Agent({ agent }: AgentProps) {
  const meshRef = useRef<THREE.Mesh>(null)
  const glowRef = useRef<THREE.Mesh>(null)

  const { debate } = useWorldStore()

  // Agent-specific geometry and styling
  const { geometry, material, glowColor } = useMemo(() => {
    switch (agent.archetype) {
      case 'order': // Axioma - crystalline
        return {
          geometry: <icosahedronGeometry args={[1, 0]} />,
          material: (
            <meshStandardMaterial
              color={agent.primary_color}
              metalness={0.8}
              roughness={0.2}
              emissive={agent.primary_color}
              emissiveIntensity={0.3}
            />
          ),
          glowColor: agent.primary_color
        }

      case 'logic': // Veridicus - data stream
        return {
          geometry: <boxGeometry args={[1.5, 2, 1.5]} />,
          material: (
            <meshStandardMaterial
              color={agent.primary_color}
              metalness={0.6}
              roughness={0.3}
              transparent
              opacity={0.8}
              emissive={agent.primary_color}
              emissiveIntensity={0.2}
            />
          ),
          glowColor: agent.primary_color
        }

      case 'chaos': // Paradoxia - shifting form
      default:
        return {
          geometry: <torusKnotGeometry args={[0.6, 0.2, 64, 16]} />,
          material: (
            <meshStandardMaterial
              color={agent.primary_color}
              metalness={0.4}
              roughness={0.5}
              emissive={agent.primary_color}
              emissiveIntensity={0.5}
            />
          ),
          glowColor: agent.primary_color
        }
    }
  }, [agent.archetype, agent.primary_color])

  // Animation
  useFrame((state, delta) => {
    if (!meshRef.current) return

    // Floating animation
    meshRef.current.position.y = 1.5 + Math.sin(state.clock.elapsedTime * 2) * 0.1

    // Rotation based on archetype
    if (agent.archetype === 'order') {
      meshRef.current.rotation.y += delta * 0.3
    } else if (agent.archetype === 'logic') {
      meshRef.current.rotation.y += delta * 0.1
    } else {
      // Chaos - irregular rotation
      meshRef.current.rotation.x += delta * 0.5
      meshRef.current.rotation.y += delta * 0.3
      meshRef.current.rotation.z += delta * 0.2
    }

    // Glow pulsing
    if (glowRef.current) {
      const scale = 1.5 + Math.sin(state.clock.elapsedTime * 3) * 0.1
      glowRef.current.scale.setScalar(scale)
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

  return (
    <group position={[agent.position.x, 0, agent.position.z]}>
      {/* Agent body with float effect for Paradoxia */}
      <Float
        speed={agent.archetype === 'chaos' ? 4 : 2}
        rotationIntensity={agent.archetype === 'chaos' ? 0.5 : 0.1}
        floatIntensity={agent.archetype === 'chaos' ? 0.5 : 0.2}
        enabled={true}
      >
        <mesh ref={meshRef} castShadow>
          {geometry}
          {material}
        </mesh>

        {/* Glow sphere */}
        <mesh ref={glowRef} scale={1.5}>
          <sphereGeometry args={[1, 16, 16]} />
          <meshBasicMaterial
            color={glowColor}
            transparent
            opacity={0.1 * agent.glow_intensity}
            side={THREE.BackSide}
          />
        </mesh>
      </Float>

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

      {/* Ground marker */}
      <mesh position={[0, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[1.5, 2, 32]} />
        <meshBasicMaterial
          color={agent.primary_color}
          transparent
          opacity={0.3}
        />
      </mesh>
    </group>
  )
}
