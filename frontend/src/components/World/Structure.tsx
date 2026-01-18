import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Float } from '@react-three/drei'
import * as THREE from 'three'
import type { Structure as StructureType } from '../../types'

interface StructureProps {
  structure: StructureType
}

// Extended material presets for different archetypes
const MATERIALS: Record<string, {
  color: string
  emissive: string
  metalness: number
  roughness: number
  transmission?: number
  ior?: number
}> = {
  // Order materials
  crystal: { color: '#FFD700', emissive: '#FFD700', metalness: 0.9, roughness: 0.1 },
  sacred_gold: { color: '#F5D020', emissive: '#FFD700', metalness: 0.95, roughness: 0.05 },
  divine_marble: { color: '#FAFAFA', emissive: '#FFFFD0', metalness: 0.1, roughness: 0.3 },

  // Logic materials
  data_glass: { color: '#4169E1', emissive: '#00FFFF', metalness: 0.7, roughness: 0.1, transmission: 0.8, ior: 1.5 },
  truth_metal: { color: '#C0C0C0', emissive: '#4169E1', metalness: 0.85, roughness: 0.15 },
  circuit: { color: '#1a1a2e', emissive: '#00FFFF', metalness: 0.6, roughness: 0.3 },

  // Chaos materials
  ethereal: { color: '#FF00FF', emissive: '#FF00FF', metalness: 0.5, roughness: 0.3 },
  void: { color: '#0a0a0a', emissive: '#FF00FF', metalness: 0.3, roughness: 0.7 },
  paradox: { color: '#FF00FF', emissive: '#00FFFF', metalness: 0.4, roughness: 0.5 },
  glitch: { color: '#00FFFF', emissive: '#FF00FF', metalness: 0.6, roughness: 0.4 },

  // Neutral
  stone: { color: '#808080', emissive: '#404040', metalness: 0.2, roughness: 0.8 },
  obsidian: { color: '#1a1a1a', emissive: '#2a2a2a', metalness: 0.9, roughness: 0.1 }
}

export default function Structure({ structure }: StructureProps) {
  const groupRef = useRef<THREE.Group>(null)
  const glowRef = useRef<THREE.Mesh>(null)
  const timeRef = useRef(0)

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
  const geometryElement = useMemo(() => {
    switch (structure.structure_type) {
      case 'temple':
        return (
          <group>
            {/* Base platform with steps */}
            <mesh position={[0, 0.15, 0]} castShadow receiveShadow>
              <boxGeometry args={[5, 0.3, 5]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0, 0.4, 0]} castShadow receiveShadow>
              <boxGeometry args={[4.5, 0.2, 4.5]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0, 0.6, 0]} castShadow receiveShadow>
              <boxGeometry args={[4, 0.2, 4]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            {/* Pillars */}
            {[[-1.5, 1.5], [1.5, 1.5], [-1.5, -1.5], [1.5, -1.5]].map(([x, z], i) => (
              <mesh key={i} position={[x, 2.2, z]} castShadow>
                <cylinderGeometry args={[0.25, 0.3, 3, 8]} />
                <meshStandardMaterial {...materialProps} />
              </mesh>
            ))}
            {/* Roof */}
            <mesh position={[0, 4.2, 0]} castShadow>
              <coneGeometry args={[2.8, 1.5, 4]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            {/* Capstone */}
            <mesh position={[0, 5.2, 0]}>
              <octahedronGeometry args={[0.3]} />
              <meshStandardMaterial {...materialProps} emissiveIntensity={0.6} />
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
            <Float speed={2} floatIntensity={0.3}>
              <mesh position={[0, 1.5, 0]} castShadow>
                <dodecahedronGeometry args={[0.3]} />
                <meshStandardMaterial {...materialProps} emissiveIntensity={0.8} />
              </mesh>
            </Float>
          </group>
        )

      case 'obelisk':
        return (
          <group>
            <mesh position={[0, 0.2, 0]} castShadow receiveShadow>
              <boxGeometry args={[1, 0.4, 1]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0, 2.7, 0]} castShadow>
              <cylinderGeometry args={[0.2, 0.45, 4.5, 4]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0, 5.2, 0]}>
              <coneGeometry args={[0.3, 0.6, 4]} />
              <meshStandardMaterial {...materialProps} emissiveIntensity={0.5} />
            </mesh>
          </group>
        )

      case 'monument':
        return (
          <group>
            <mesh position={[0, 1, 0]} castShadow receiveShadow>
              <boxGeometry args={[1.5, 2, 1.5]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <Float speed={1.5} floatIntensity={0.2}>
              <mesh position={[0, 2.8, 0]} castShadow>
                <octahedronGeometry args={[0.5]} />
                <meshStandardMaterial {...materialProps} emissiveIntensity={0.5} />
              </mesh>
            </Float>
          </group>
        )

      case 'portal':
        return (
          <group>
            {/* Outer ring */}
            <mesh rotation={[0, 0, 0]}>
              <torusGeometry args={[2, 0.3, 16, 32]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            {/* Inner void */}
            <mesh>
              <circleGeometry args={[1.7, 32]} />
              <meshBasicMaterial
                color={structure.primary_color || '#FF00FF'}
                transparent
                opacity={0.4}
                side={THREE.DoubleSide}
              />
            </mesh>
            {/* Energy swirl */}
            <Float speed={4} rotationIntensity={2}>
              <mesh rotation={[0, 0, Math.PI / 4]}>
                <torusGeometry args={[1, 0.1, 8, 32]} />
                <meshStandardMaterial {...materialProps} emissiveIntensity={0.8} />
              </mesh>
            </Float>
          </group>
        )

      case 'tower':
        return (
          <group>
            <mesh position={[0, 2.5, 0]} castShadow receiveShadow>
              <cylinderGeometry args={[1.2, 1.5, 5, 6]} />
              <meshStandardMaterial {...materialProps} wireframe={structure.material_preset === 'data_glass'} />
            </mesh>
            <mesh position={[0, 5.5, 0]} castShadow>
              <coneGeometry args={[1.4, 1.5, 6]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
          </group>
        )

      case 'dome':
        return (
          <group>
            <mesh position={[0, 0.15, 0]} castShadow receiveShadow>
              <cylinderGeometry args={[2.5, 2.5, 0.3, 32]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0, 1.5, 0]} castShadow>
              <sphereGeometry args={[2, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
              <meshStandardMaterial {...materialProps} side={THREE.DoubleSide} />
            </mesh>
          </group>
        )

      case 'pyramid':
        return (
          <group>
            <mesh position={[0, 1.5, 0]} castShadow receiveShadow>
              <coneGeometry args={[2, 3, 4]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            {/* Capstone */}
            <Float speed={1} floatIntensity={0.1}>
              <mesh position={[0, 3.2, 0]}>
                <coneGeometry args={[0.3, 0.4, 4]} />
                <meshStandardMaterial {...materialProps} emissiveIntensity={0.6} />
              </mesh>
            </Float>
          </group>
        )

      case 'spire':
        return (
          <group>
            <mesh position={[0, 0.5, 0]} castShadow receiveShadow>
              <dodecahedronGeometry args={[0.8]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0, 2.5, 0]} castShadow>
              <coneGeometry args={[0.6, 3, 12]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0, 4.5, 0]}>
              <octahedronGeometry args={[0.2]} />
              <meshStandardMaterial {...materialProps} emissiveIntensity={0.8} />
            </mesh>
          </group>
        )

      case 'shrine':
        return (
          <group>
            {/* Base */}
            <mesh position={[0, 0.25, 0]} castShadow receiveShadow>
              <boxGeometry args={[2.5, 0.5, 2.5]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            {/* Arch */}
            <mesh position={[-0.8, 1.5, 0]} castShadow>
              <boxGeometry args={[0.2, 2, 0.2]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0.8, 1.5, 0]} castShadow>
              <boxGeometry args={[0.2, 2, 0.2]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            <mesh position={[0, 2.7, 0]} castShadow>
              <torusGeometry args={[0.8, 0.1, 8, 16, Math.PI]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            {/* Sacred object */}
            <Float speed={2} floatIntensity={0.2}>
              <mesh position={[0, 1.2, 0]}>
                <icosahedronGeometry args={[0.25]} />
                <meshStandardMaterial {...materialProps} emissiveIntensity={0.7} />
              </mesh>
            </Float>
          </group>
        )

      case 'library':
      case 'archive':
        return (
          <group>
            <mesh position={[0, 1.5, 0]} castShadow receiveShadow>
              <boxGeometry args={[3, 3, 2]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            {/* Door */}
            <mesh position={[0, 0.75, 1.01]}>
              <boxGeometry args={[0.8, 1.5, 0.1]} />
              <meshStandardMaterial color="#2a2a2a" metalness={0.5} roughness={0.5} />
            </mesh>
            {/* Data streams (for archives) */}
            {structure.material_preset === 'data_glass' && (
              <Float speed={3} floatIntensity={0.5}>
                <mesh position={[0, 4, 0]}>
                  <boxGeometry args={[0.1, 2, 0.1]} />
                  <meshBasicMaterial color="#00FFFF" transparent opacity={0.7} />
                </mesh>
              </Float>
            )}
          </group>
        )

      case 'floating_symbol':
        return (
          <Float speed={3} rotationIntensity={1} floatIntensity={1}>
            <mesh castShadow>
              <torusGeometry args={[0.8, 0.2, 16, 32]} />
              <meshStandardMaterial {...materialProps} emissiveIntensity={0.8} />
            </mesh>
            <mesh rotation={[Math.PI / 2, 0, 0]}>
              <torusGeometry args={[0.8, 0.2, 16, 32]} />
              <meshStandardMaterial {...materialProps} emissiveIntensity={0.8} />
            </mesh>
          </Float>
        )

      case 'rift':
        return (
          <group>
            {/* Glowing crack in reality */}
            <mesh rotation={[0, 0, 0.2]} castShadow>
              <planeGeometry args={[0.3, 4]} />
              <meshBasicMaterial color={structure.primary_color || '#FF00FF'} side={THREE.DoubleSide} />
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
            {/* Particles emanating */}
            {[...Array(5)].map((_, i) => (
              <Float key={i} speed={2 + i * 0.5} floatIntensity={0.5}>
                <mesh position={[(Math.random() - 0.5) * 2, (i - 2) * 0.8, 0.1]}>
                  <sphereGeometry args={[0.05, 8, 8]} />
                  <meshBasicMaterial color={structure.primary_color || '#FF00FF'} />
                </mesh>
              </Float>
            ))}
          </group>
        )

      case 'beacon':
        return (
          <group>
            <mesh position={[0, 1, 0]} castShadow>
              <cylinderGeometry args={[0.3, 0.5, 2, 8]} />
              <meshStandardMaterial {...materialProps} />
            </mesh>
            {/* Light beam */}
            <mesh position={[0, 6, 0]}>
              <cylinderGeometry args={[0, 0.5, 10, 16]} />
              <meshBasicMaterial
                color={structure.primary_color || materialProps.emissive}
                transparent
                opacity={0.3}
              />
            </mesh>
          </group>
        )

      default:
        return (
          <mesh castShadow receiveShadow>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial {...materialProps} />
          </mesh>
        )
    }
  }, [structure.structure_type, materialProps, structure.primary_color, structure.material_preset])

  // Animations based on structure type
  useFrame((_, delta) => {
    if (!groupRef.current) return
    timeRef.current += delta

    // Gentle rotation for glowing structures
    if (structure.glow_enabled) {
      groupRef.current.rotation.y += delta * 0.1
    }

    // Type-specific animations
    if (structure.structure_type === 'portal') {
      groupRef.current.rotation.y += delta * 0.3
    }

    if (structure.structure_type === 'rift') {
      // Slight pulsing
      const scale = 1 + Math.sin(timeRef.current * 3) * 0.05
      groupRef.current.scale.setScalar(scale * structure.scale)
    }

    // Glow pulsing
    if (glowRef.current && structure.glow_enabled) {
      const intensity = 0.15 + Math.sin(timeRef.current * 2) * 0.05
      ;(glowRef.current.material as THREE.MeshBasicMaterial).opacity = intensity
    }
  })

  const yOffset = structure.structure_type === 'floating_symbol' ? 3 :
                  structure.structure_type === 'portal' ? 2.5 : 0

  return (
    <group
      ref={groupRef}
      position={[structure.position.x, structure.position.y + yOffset, structure.position.z]}
      rotation={[0, (structure.rotation_y * Math.PI) / 180, 0]}
      scale={structure.scale}
    >
      {geometryElement}

      {/* Ambient glow for enabled structures */}
      {structure.glow_enabled && (
        <mesh ref={glowRef}>
          <sphereGeometry args={[3, 16, 16]} />
          <meshBasicMaterial
            color={structure.primary_color || materialProps.emissive}
            transparent
            opacity={0.15}
            side={THREE.BackSide}
          />
        </mesh>
      )}
    </group>
  )
}
