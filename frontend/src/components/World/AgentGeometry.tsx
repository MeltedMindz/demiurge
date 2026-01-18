/**
 * AgentGeometry - Dynamic geometry factory for agent shapes
 * Agents can deterministically choose their form based on their state
 */
import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { ShapeConfig, ShapeType } from '../../types'
import { SHAPE_PRESETS, selectShapeForAgent } from '../../three/agentShapes'

interface AgentGeometryProps {
  shapePreset?: string
  customConfig?: ShapeConfig
  archetype: string
  primaryColor: string
  influenceScore: number
  proposalsAccepted: number
  cycleNumber: number
  animation?: 'spin' | 'pulse' | 'float' | 'morph' | 'glitch'
}

// Create geometry based on shape type
function createGeometry(type: ShapeType, args: number[]): THREE.BufferGeometry {
  switch (type) {
    case 'icosahedron':
      return new THREE.IcosahedronGeometry(args[0] ?? 1, args[1] ?? 0)
    case 'octahedron':
      return new THREE.OctahedronGeometry(args[0] ?? 1, args[1] ?? 0)
    case 'dodecahedron':
      return new THREE.DodecahedronGeometry(args[0] ?? 1, args[1] ?? 0)
    case 'tetrahedron':
      return new THREE.TetrahedronGeometry(args[0] ?? 1, args[1] ?? 0)
    case 'cube':
      return new THREE.BoxGeometry(args[0] ?? 1, args[1] ?? 1, args[2] ?? 1)
    case 'sphere':
      return new THREE.SphereGeometry(args[0] ?? 1, args[1] ?? 32, args[2] ?? 32)
    case 'torus':
      return new THREE.TorusGeometry(args[0] ?? 0.8, args[1] ?? 0.3, args[2] ?? 16, args[3] ?? 32)
    case 'torusKnot':
      return new THREE.TorusKnotGeometry(args[0] ?? 0.6, args[1] ?? 0.2, args[2] ?? 128, args[3] ?? 16)
    case 'cone':
      return new THREE.ConeGeometry(args[0] ?? 1, args[1] ?? 2, args[2] ?? 8)
    case 'cylinder':
      return new THREE.CylinderGeometry(args[0] ?? 0.5, args[1] ?? 0.5, args[2] ?? 2, args[3] ?? 8)
    case 'capsule':
      return new THREE.CapsuleGeometry(args[0] ?? 0.5, args[1] ?? 1, args[2] ?? 4, args[3] ?? 8)
    case 'ring':
      return new THREE.RingGeometry(args[0] ?? 0.5, args[1] ?? 1, args[2] ?? 32)
    case 'star':
      // Custom star geometry using extrude
      return createStarGeometry(args[0] ?? 1, args[1] ?? 0.5, args[2] ?? 5)
    case 'spiral':
      // Custom spiral using tube geometry
      return createSpiralGeometry(args[0] ?? 1, args[1] ?? 3, args[2] ?? 64)
    case 'fractal':
      // Sierpinski-like fractal using merged icosahedrons
      return createFractalGeometry(args[0] ?? 1, args[1] ?? 2)
    case 'void':
      // Inverted sphere for void/negative space
      const voidGeo = new THREE.SphereGeometry(args[0] ?? 1, 32, 32)
      voidGeo.scale(-1, -1, -1) // Invert normals
      return voidGeo
    case 'flux':
      // Use torus knot with special parameters for flux
      return new THREE.TorusKnotGeometry(0.6, 0.15, 200, 32, 3, 7)
    default:
      return new THREE.IcosahedronGeometry(1, 0)
  }
}

// Custom star geometry
function createStarGeometry(outerRadius: number, innerRadius: number, points: number): THREE.BufferGeometry {
  const shape = new THREE.Shape()
  const angleStep = Math.PI / points

  for (let i = 0; i < points * 2; i++) {
    const radius = i % 2 === 0 ? outerRadius : innerRadius
    const angle = i * angleStep - Math.PI / 2
    const x = Math.cos(angle) * radius
    const y = Math.sin(angle) * radius

    if (i === 0) {
      shape.moveTo(x, y)
    } else {
      shape.lineTo(x, y)
    }
  }
  shape.closePath()

  const extrudeSettings = {
    depth: 0.3,
    bevelEnabled: true,
    bevelThickness: 0.1,
    bevelSize: 0.1,
    bevelSegments: 2
  }

  return new THREE.ExtrudeGeometry(shape, extrudeSettings)
}

// Custom spiral geometry
function createSpiralGeometry(radius: number, turns: number, segments: number): THREE.BufferGeometry {
  const points: THREE.Vector3[] = []
  for (let i = 0; i <= segments; i++) {
    const t = i / segments
    const angle = t * Math.PI * 2 * turns
    const r = radius * (1 - t * 0.5)
    const y = t * 3 - 1.5
    points.push(new THREE.Vector3(
      Math.cos(angle) * r,
      y,
      Math.sin(angle) * r
    ))
  }
  const curve = new THREE.CatmullRomCurve3(points)
  return new THREE.TubeGeometry(curve, segments, 0.1, 8, false)
}

// Fractal geometry (simplified Sierpinski-like)
function createFractalGeometry(size: number, depth: number): THREE.BufferGeometry {
  const geometries: THREE.BufferGeometry[] = []

  function addLevel(s: number, x: number, y: number, z: number, d: number) {
    if (d <= 0) {
      const geo = new THREE.TetrahedronGeometry(s, 0)
      geo.translate(x, y, z)
      geometries.push(geo)
      return
    }

    const ns = s / 2
    const offset = s * 0.4
    addLevel(ns, x, y + offset, z, d - 1)
    addLevel(ns, x - offset, y - offset/2, z - offset, d - 1)
    addLevel(ns, x + offset, y - offset/2, z - offset, d - 1)
    addLevel(ns, x, y - offset/2, z + offset, d - 1)
  }

  addLevel(size, 0, 0, 0, Math.min(depth, 3))

  // Merge all geometries
  const merged = new THREE.BufferGeometry()
  const positions: number[] = []
  const normals: number[] = []

  geometries.forEach(geo => {
    const pos = geo.getAttribute('position')
    const norm = geo.getAttribute('normal')
    for (let i = 0; i < pos.count; i++) {
      positions.push(pos.getX(i), pos.getY(i), pos.getZ(i))
      normals.push(norm.getX(i), norm.getY(i), norm.getZ(i))
    }
  })

  merged.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
  merged.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3))

  return merged
}

export default function AgentGeometry({
  shapePreset,
  customConfig,
  archetype,
  primaryColor,
  influenceScore,
  proposalsAccepted,
  cycleNumber,
  animation
}: AgentGeometryProps) {
  const meshRef = useRef<THREE.Mesh>(null)
  const timeRef = useRef(0)

  // Determine shape config from preset, custom, or agent state
  const shapeConfig = useMemo(() => {
    // Priority: custom config > explicit preset > deterministic selection
    if (customConfig) {
      return customConfig
    }

    if (shapePreset && SHAPE_PRESETS[shapePreset]) {
      return SHAPE_PRESETS[shapePreset]
    }

    // Deterministic shape selection based on agent state
    const selectedPreset = selectShapeForAgent(archetype, influenceScore, proposalsAccepted, cycleNumber)
    return SHAPE_PRESETS[selectedPreset] || SHAPE_PRESETS['crystal_perfect']
  }, [shapePreset, customConfig, archetype, influenceScore, proposalsAccepted, cycleNumber])

  // Create geometry
  const geometry = useMemo(() => {
    return createGeometry(shapeConfig.type, shapeConfig.args)
  }, [shapeConfig.type, JSON.stringify(shapeConfig.args)])

  // Animation handling
  useFrame((_, delta) => {
    if (!meshRef.current) return

    timeRef.current += delta
    const t = timeRef.current
    const animType = animation || shapeConfig.animation || 'float'

    switch (animType) {
      case 'spin':
        meshRef.current.rotation.y += delta * 0.5
        break

      case 'pulse':
        const pulseScale = 1 + Math.sin(t * 3) * 0.1
        meshRef.current.scale.setScalar(pulseScale * (shapeConfig.scale || 1))
        break

      case 'float':
        meshRef.current.position.y = Math.sin(t * 2) * 0.2
        meshRef.current.rotation.y += delta * 0.2
        break

      case 'morph':
        // Simulate morphing with scale oscillation
        const morphX = 1 + Math.sin(t * 2) * 0.15
        const morphY = 1 + Math.sin(t * 2.5) * 0.1
        const morphZ = 1 + Math.sin(t * 1.8) * 0.12
        meshRef.current.scale.set(morphX, morphY, morphZ)
        meshRef.current.rotation.x += delta * 0.3
        meshRef.current.rotation.z += delta * 0.2
        break

      case 'glitch':
        // Random scale/position glitches
        if (Math.random() < 0.02) {
          meshRef.current.position.x = (Math.random() - 0.5) * 0.3
          meshRef.current.position.z = (Math.random() - 0.5) * 0.3
          meshRef.current.scale.setScalar(0.8 + Math.random() * 0.4)
        } else {
          // Smooth return to center
          meshRef.current.position.x *= 0.95
          meshRef.current.position.z *= 0.95
          meshRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.1)
        }
        meshRef.current.rotation.y += delta * 0.4
        break
    }
  })

  return (
    <mesh
      ref={meshRef}
      geometry={geometry}
      scale={shapeConfig.scale || 1}
      castShadow
      receiveShadow
    >
      <meshStandardMaterial
        color={primaryColor}
        metalness={shapeConfig.metalness ?? 0.7}
        roughness={shapeConfig.roughness ?? 0.3}
        wireframe={shapeConfig.wireframe || false}
        emissive={primaryColor}
        emissiveIntensity={shapeConfig.emissiveIntensity ?? 0.3}
      />
    </mesh>
  )
}
