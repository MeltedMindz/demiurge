/**
 * ParticleEffects - Various particle systems for world atmosphere
 * Used by agents to create visual effects in their domains
 */
import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Points, PointMaterial } from '@react-three/drei'
import * as THREE from 'three'
import type { WorldEffect } from '../../types'

interface ParticleEffectsProps {
  effects: WorldEffect[]
}

// Individual particle system component
function ParticleSystem({ effect }: { effect: WorldEffect }) {
  const pointsRef = useRef<THREE.Points>(null)
  const timeRef = useRef(0)

  const { positions, colors, particleCount } = useMemo(() => {
    const count = (effect.parameters.count as number) || 100
    const spread = (effect.parameters.spread as number) || 5
    const pos = new Float32Array(count * 3)
    const col = new Float32Array(count * 3)

    const color = new THREE.Color(effect.parameters.color as string || '#FFFFFF')

    for (let i = 0; i < count; i++) {
      // Initial positions
      pos[i * 3] = (Math.random() - 0.5) * spread
      pos[i * 3 + 1] = Math.random() * spread
      pos[i * 3 + 2] = (Math.random() - 0.5) * spread

      // Colors with slight variation
      const colorVariation = 0.1 + Math.random() * 0.1
      col[i * 3] = color.r * (1 - colorVariation + Math.random() * colorVariation * 2)
      col[i * 3 + 1] = color.g * (1 - colorVariation + Math.random() * colorVariation * 2)
      col[i * 3 + 2] = color.b * (1 - colorVariation + Math.random() * colorVariation * 2)

    }

    return { positions: pos, colors: col, particleCount: count }
  }, [effect.parameters])

  useFrame((_, delta) => {
    if (!pointsRef.current) return
    timeRef.current += delta

    const positions = pointsRef.current.geometry.attributes.position.array as Float32Array
    const spread = (effect.parameters.spread as number) || 5
    const speed = (effect.parameters.speed as number) || 1

    for (let i = 0; i < particleCount; i++) {
      const idx = i * 3

      switch (effect.effect_type) {
        case 'ascending':
          positions[idx + 1] += delta * speed * 0.5
          positions[idx] += Math.sin(timeRef.current + i) * delta * 0.1
          // Reset when too high
          if (positions[idx + 1] > spread) {
            positions[idx + 1] = 0
            positions[idx] = (Math.random() - 0.5) * spread
            positions[idx + 2] = (Math.random() - 0.5) * spread
          }
          break

        case 'descending':
          positions[idx + 1] -= delta * speed * 0.3
          if (positions[idx + 1] < 0) {
            positions[idx + 1] = spread
          }
          break

        case 'orbital':
          const angle = timeRef.current * speed + i * 0.1
          const radius = 2 + Math.sin(i) * 1
          const y = positions[idx + 1]
          positions[idx] = Math.cos(angle) * radius
          positions[idx + 2] = Math.sin(angle) * radius
          positions[idx + 1] = y + Math.sin(timeRef.current * 2 + i) * delta * 0.5
          if (positions[idx + 1] > spread || positions[idx + 1] < 0) {
            positions[idx + 1] = Math.random() * spread
          }
          break

        case 'nebula':
          // Slow swirling motion
          const nebAngle = timeRef.current * 0.1 + i * 0.05
          positions[idx] += Math.cos(nebAngle) * delta * 0.1
          positions[idx + 2] += Math.sin(nebAngle) * delta * 0.1
          positions[idx + 1] += Math.sin(timeRef.current * 0.5 + i) * delta * 0.05
          // Keep within bounds
          if (Math.abs(positions[idx]) > spread) positions[idx] *= 0.9
          if (Math.abs(positions[idx + 2]) > spread) positions[idx + 2] *= 0.9
          break

        case 'fireflies':
          // Random wandering
          positions[idx] += (Math.random() - 0.5) * delta * speed
          positions[idx + 1] += (Math.random() - 0.5) * delta * speed * 0.5
          positions[idx + 2] += (Math.random() - 0.5) * delta * speed
          // Soft bounds
          if (Math.abs(positions[idx]) > spread) positions[idx] *= 0.95
          if (positions[idx + 1] > spread) positions[idx + 1] = spread
          if (positions[idx + 1] < 0.5) positions[idx + 1] = 0.5
          if (Math.abs(positions[idx + 2]) > spread) positions[idx + 2] *= 0.95
          break

        case 'data_stream':
          // Vertical data flow
          positions[idx + 1] -= delta * speed * 2
          if (positions[idx + 1] < 0) {
            positions[idx + 1] = spread
            positions[idx] = (Math.random() - 0.5) * spread * 0.5
            positions[idx + 2] = (Math.random() - 0.5) * spread * 0.5
          }
          break

        default:
          // Default floating
          positions[idx + 1] += Math.sin(timeRef.current + i * 0.1) * delta * 0.3
      }
    }

    pointsRef.current.geometry.attributes.position.needsUpdate = true
  })

  const size = (effect.parameters.size as number) || 0.1

  return (
    <group position={[effect.position.x, effect.position.y, effect.position.z]}>
      <Points ref={pointsRef} limit={particleCount}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particleCount}
            array={positions}
            itemSize={3}
          />
          <bufferAttribute
            attach="attributes-color"
            count={particleCount}
            array={colors}
            itemSize={3}
          />
        </bufferGeometry>
        <PointMaterial
          size={size}
          vertexColors
          transparent
          opacity={effect.intensity}
          sizeAttenuation
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </Points>
    </group>
  )
}

// Ambient world particles (always present)
function AmbientParticles() {
  const pointsRef = useRef<THREE.Points>(null)

  const { positions, count } = useMemo(() => {
    const c = 200
    const pos = new Float32Array(c * 3)
    const spread = 60

    for (let i = 0; i < c; i++) {
      pos[i * 3] = (Math.random() - 0.5) * spread
      pos[i * 3 + 1] = Math.random() * 15 + 0.5
      pos[i * 3 + 2] = (Math.random() - 0.5) * spread
    }

    return { positions: pos, count: c }
  }, [])

  useFrame((state) => {
    if (!pointsRef.current) return

    const positions = pointsRef.current.geometry.attributes.position.array as Float32Array

    for (let i = 0; i < count; i++) {
      const idx = i * 3
      // Gentle floating
      positions[idx + 1] += Math.sin(state.clock.elapsedTime * 0.5 + i * 0.1) * 0.002
    }

    pointsRef.current.geometry.attributes.position.needsUpdate = true
  })

  return (
    <Points ref={pointsRef} limit={count}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <PointMaterial
        size={0.05}
        color="#FFFFFF"
        transparent
        opacity={0.3}
        sizeAttenuation
        depthWrite={false}
      />
    </Points>
  )
}

export default function ParticleEffects({ effects }: ParticleEffectsProps) {
  // Filter for active particle-type effects
  const particleEffects = effects.filter(
    e => e.active && ['ascending', 'descending', 'orbital', 'nebula', 'fireflies', 'data_stream', 'particle_field'].includes(e.effect_type)
  )

  return (
    <group>
      {/* Ambient world particles */}
      <AmbientParticles />

      {/* Agent-created particle effects */}
      {particleEffects.map(effect => (
        <ParticleSystem key={effect.id} effect={effect} />
      ))}
    </group>
  )
}
