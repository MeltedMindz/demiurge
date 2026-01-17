import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Float } from '@react-three/drei'
import * as THREE from 'three'
import type { Structure as StructureType } from '../../types'

interface StructureProps {
  structure: StructureType
}

// Material presets
const MATERIALS: Record<string, { color: string, emissive: string, metalness: number, roughness: number }> = {
  crystal: { color: '#FFD700', emissive: '#FFD700', metalness: 0.9, roughness: 0.1 },
  stone: { color: '#808080', emissive: '#404040', metalness: 0.2, roughness: 0.8 },
  ethereal: { color: '#FF00FF', emissive: '#FF00FF', metalness: 0.5, roughness: 0.3 }
}

export default function Structure({ structure }: StructureProps) {
  const meshRef = useRef<THREE.Mesh>(null)

  // Get material properties
  const materialProps = useMemo(() => {
    const preset = MATERIALS[structure.material_preset] || MATERIALS.stone
    return {
      ...preset,
      color: structure.primary_color || preset.color,
      emissive: structure.glow_enabled ? (structure.primary_color || preset.emissive) : '#000000',
      emissiveIntensity: structure.glow_enabled ? 0.3 : 0
    }
  }, [structure.material_preset, structure.primary_color, structure.glow_enabled])

  // Structure-specific geometry
  const geometry = useMemo(() => {
    switch (structure.structure_type) {
      case 'temple':
        return (
          <group>
            {/* Base platform */}
            <mesh position={[0, 0.25, 0]} castShadow receiveShadow>
              <boxGeometry args={[4, 0.5, 4]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            {/* Pillars */}
            {[[-1.5, 1.5], [1.5, 1.5], [-1.5, -1.5], [1.5, -1.5]].map(([x, z], i) => (
              <mesh key={i} position={[x, 2, z]} castShadow>
                <cylinderGeometry args={[0.3, 0.3, 3, 8]} />
                <meshStandardMaterial {...materialProps} />
              </mesh>
            ))}
            {/* Roof */}
            <mesh position={[0, 4, 0]} castShadow>
              <coneGeometry args={[3, 1.5, 4]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
          </group>
        )

      case 'altar':
        return (
          <group>
            <mesh position={[0, 0.5, 0]} castShadow receiveShadow>
              <boxGeometry args={[2, 1, 1]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0, 1.3, 0]} castShadow>
              <sphereGeometry args={[0.3, 16, 16]} />
              <meshStandardMaterial
                {...materialProps}
                emissiveIntensity={0.8}
              />
            </mesh>
          </group>
        )

      case 'obelisk':
        return (
          <mesh castShadow>
            <cylinderGeometry args={[0.3, 0.5, 5, 4]} />
            <meshStandardMaterial {...materialProps} />
          </mesh>
        )

      case 'monument':
        return (
          <group>
            <mesh position={[0, 1, 0]} castShadow receiveShadow>
              <boxGeometry args={[1.5, 2, 1.5]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0, 2.5, 0]} castShadow>
              <octahedronGeometry args={[0.5]} />
              <meshStandardMaterial
                {...materialProps}
                emissiveIntensity={0.5}
              />
            </mesh>
          </group>
        )

      case 'library':
        return (
          <group>
            <mesh position={[0, 1.5, 0]} castShadow receiveShadow>
              <boxGeometry args={[3, 3, 2]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            {/* Doors */}
            <mesh position={[0, 0.75, 1.01]}>
              <boxGeometry args={[0.8, 1.5, 0.1]} />
              <meshStandardMaterial color="#2a2a2a" />
            </mesh>
          </group>
        )

      case 'floating_symbol':
        return (
          <Float speed={3} rotationIntensity={1} floatIntensity={1}>
            <mesh castShadow>
              <torusGeometry args={[0.8, 0.2, 16, 32]} />
              <meshStandardMaterial
                {...materialProps}
                emissiveIntensity={0.8}
              />
            </mesh>
            <mesh rotation={[0, 0, Math.PI / 2]}>
              <torusGeometry args={[0.8, 0.2, 16, 32]} />
              <meshStandardMaterial
                {...materialProps}
                emissiveIntensity={0.8}
              />
            </mesh>
          </Float>
        )

      case 'rift':
        return (
          <group>
            {/* Glowing crack in reality */}
            <mesh rotation={[0, 0, 0.2]} castShadow>
              <planeGeometry args={[0.3, 4]} />
              <meshBasicMaterial
                color={structure.primary_color || '#FF00FF'}
                side={THREE.DoubleSide}
              />
            </mesh>
            {/* Glow effect */}
            <mesh>
              <planeGeometry args={[2, 5]} />
              <meshBasicMaterial
                color={structure.primary_color || '#FF00FF'}
                transparent
                opacity={0.2}
                side={THREE.DoubleSide}
              />
            </mesh>
          </group>
        )

      default:
        // Default cube
        return (
          <mesh castShadow receiveShadow>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial {...materialProps} />
          </mesh>
        )
    }
  }, [structure.structure_type, materialProps])

  // Gentle floating/rotation for some structures
  useFrame((state, delta) => {
    if (!meshRef.current) return

    if (structure.glow_enabled) {
      meshRef.current.rotation.y += delta * 0.1
    }
  })

  const yOffset = structure.structure_type === 'floating_symbol' ? 3 : 0

  return (
    <group
      ref={meshRef}
      position={[structure.position.x, structure.position.y + yOffset, structure.position.z]}
      rotation={[0, (structure.rotation_y * Math.PI) / 180, 0]}
      scale={structure.scale}
    >
      {geometry}
    </group>
  )
}
