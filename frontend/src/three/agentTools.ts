/**
 * Agent Tools System
 * Provides agents with tools to shape and modify the 3D environment
 * These tools integrate with various Three.js libraries
 */

import * as THREE from 'three'

// Tool categories available to agents
export type ToolCategory =
  | 'structure'     // Build temples, monuments, altars
  | 'terrain'       // Modify ground, create hills/valleys
  | 'particle'      // Create particle effects, nebulae
  | 'path'          // Create pathways, navigation routes
  | 'lighting'      // Add light sources, modify atmosphere
  | 'postprocess'   // Apply visual filters and effects
  | 'navigation'    // Define walkable areas, zones

// Structure types agents can create
export interface StructureDefinition {
  type: 'temple' | 'monument' | 'altar' | 'obelisk' | 'portal' | 'shrine' | 'tower' | 'dome' | 'pyramid' | 'spire'
  baseGeometry: 'box' | 'cylinder' | 'cone' | 'sphere' | 'icosahedron' | 'dodecahedron' | 'octahedron' | 'custom'
  scale: THREE.Vector3
  position: THREE.Vector3
  rotation: THREE.Euler
  material: {
    color: string
    metalness: number
    roughness: number
    emissive?: string
    emissiveIntensity?: number
    wireframe?: boolean
    transparent?: boolean
    opacity?: number
  }
  decorations?: DecorationConfig[]
  animation?: StructureAnimation
}

export interface DecorationConfig {
  type: 'floating_symbol' | 'light_beam' | 'particle_aura' | 'glow_ring' | 'orbit_objects'
  parameters: Record<string, number | string | boolean | string[]>
}

export interface StructureAnimation {
  type: 'rotate' | 'pulse' | 'float' | 'breathe'
  speed: number
  intensity: number
}

// Terrain modification types
export interface TerrainModification {
  type: 'elevation' | 'crater' | 'mound' | 'plateau' | 'valley' | 'ripple' | 'fracture'
  center: THREE.Vector2
  radius: number
  intensity: number
  falloff: 'linear' | 'smooth' | 'sharp'
  color?: string
}

// Particle effect definitions
export interface ParticleEffect {
  type: 'ascending' | 'descending' | 'orbital' | 'explosion' | 'nebula' | 'fireflies' | 'data_stream'
  position: THREE.Vector3
  color: string  // Primary color
  count: number
  lifetime: number
  speed: number
  spread: number
  size: number
  emissive?: boolean
}

// Path/route definitions
export interface PathDefinition {
  points: THREE.Vector3[]
  type: 'walking' | 'sacred' | 'forbidden' | 'processional'
  width: number
  material: {
    color: string
    emissive?: string
    pattern?: 'solid' | 'dashed' | 'glowing'
  }
  markers?: PathMarker[]
}

export interface PathMarker {
  position: THREE.Vector3
  type: 'waypoint' | 'milestone' | 'warning' | 'blessing'
}

// Lighting configurations
export interface LightingConfig {
  type: 'point' | 'spot' | 'beam' | 'ambient_zone' | 'god_rays'
  position: THREE.Vector3
  color: string
  intensity: number
  distance?: number
  angle?: number
  decay?: number
  castShadow?: boolean
  target?: THREE.Vector3
}

// Post-processing effects
export interface PostProcessEffect {
  type: 'bloom' | 'chromatic_aberration' | 'vignette' | 'noise' | 'scanlines' | 'god_rays' | 'glitch'
  intensity: number
  parameters?: Record<string, number | boolean>
}

// Zone definitions
export interface ZoneDefinition {
  type: 'sacred' | 'forbidden' | 'neutral' | 'chaos' | 'order' | 'logic'
  shape: 'circle' | 'rectangle' | 'polygon'
  position: THREE.Vector3
  size: THREE.Vector2 | number
  vertices?: THREE.Vector2[]  // For polygon
  effect?: string
  color: string
  intensity: number
}

// Complete tool action for agents
export interface AgentToolAction {
  toolId: string
  agentId: string
  category: ToolCategory
  timestamp: number
  action:
    | { type: 'create_structure', data: StructureDefinition }
    | { type: 'modify_terrain', data: TerrainModification }
    | { type: 'spawn_particles', data: ParticleEffect }
    | { type: 'create_path', data: PathDefinition }
    | { type: 'add_lighting', data: LightingConfig }
    | { type: 'apply_postprocess', data: PostProcessEffect }
    | { type: 'define_zone', data: ZoneDefinition }
}

/**
 * Structure preset library - agents can choose from these or customize
 */
export const STRUCTURE_PRESETS: Record<string, Partial<StructureDefinition>> = {
  // Order-aligned structures
  'temple_of_order': {
    type: 'temple',
    baseGeometry: 'box',
    scale: new THREE.Vector3(4, 6, 4),
    material: {
      color: '#FFD700',
      metalness: 0.8,
      roughness: 0.2,
      emissive: '#FFD700',
      emissiveIntensity: 0.2
    },
    decorations: [
      { type: 'light_beam', parameters: { height: 20, width: 2 } },
      { type: 'floating_symbol', parameters: { symbol: 'triangle', orbit: true } }
    ],
    animation: { type: 'breathe', speed: 0.5, intensity: 0.05 }
  },
  'sacred_obelisk': {
    type: 'obelisk',
    baseGeometry: 'custom',
    scale: new THREE.Vector3(1, 8, 1),
    material: {
      color: '#FFFFFF',
      metalness: 0.9,
      roughness: 0.1,
      emissive: '#FFD700',
      emissiveIntensity: 0.3
    },
    animation: { type: 'pulse', speed: 1, intensity: 0.1 }
  },

  // Logic-aligned structures
  'data_archive': {
    type: 'tower',
    baseGeometry: 'cylinder',
    scale: new THREE.Vector3(3, 5, 3),
    material: {
      color: '#4169E1',
      metalness: 0.7,
      roughness: 0.3,
      wireframe: true,
      emissive: '#4169E1',
      emissiveIntensity: 0.4
    },
    decorations: [
      { type: 'particle_aura', parameters: { type: 'data_stream', color: '#00FFFF' } }
    ],
    animation: { type: 'rotate', speed: 0.2, intensity: 1 }
  },
  'truth_altar': {
    type: 'altar',
    baseGeometry: 'octahedron',
    scale: new THREE.Vector3(2, 2, 2),
    material: {
      color: '#C0C0C0',
      metalness: 0.6,
      roughness: 0.4,
      emissive: '#4169E1',
      emissiveIntensity: 0.2
    },
    animation: { type: 'float', speed: 0.5, intensity: 0.2 }
  },

  // Chaos-aligned structures
  'chaos_portal': {
    type: 'portal',
    baseGeometry: 'custom',
    scale: new THREE.Vector3(3, 5, 0.5),
    material: {
      color: '#FF00FF',
      metalness: 0.5,
      roughness: 0.5,
      transparent: true,
      opacity: 0.8,
      emissive: '#FF00FF',
      emissiveIntensity: 0.8
    },
    decorations: [
      { type: 'particle_aura', parameters: { type: 'nebula', colors: ['#FF00FF', '#00FFFF', '#FFFF00'] } },
      { type: 'glow_ring', parameters: { pulsing: true } }
    ],
    animation: { type: 'pulse', speed: 2, intensity: 0.3 }
  },
  'paradox_spire': {
    type: 'spire',
    baseGeometry: 'dodecahedron',
    scale: new THREE.Vector3(2, 6, 2),
    material: {
      color: '#FF00FF',
      metalness: 0.4,
      roughness: 0.6,
      emissive: '#00FFFF',
      emissiveIntensity: 0.5
    },
    animation: { type: 'rotate', speed: 0.5, intensity: 1 }
  }
}

/**
 * Particle effect presets
 */
export const PARTICLE_PRESETS: Record<string, Partial<ParticleEffect>> = {
  'sacred_ascending': {
    type: 'ascending',
    color: '#FFD700',
    count: 100,
    lifetime: 5,
    speed: 0.5,
    spread: 2,
    size: 0.1,
    emissive: true
  },
  'logic_stream': {
    type: 'data_stream',
    color: '#4169E1',
    count: 200,
    lifetime: 3,
    speed: 1,
    spread: 0.5,
    size: 0.05,
    emissive: true
  },
  'chaos_nebula': {
    type: 'nebula',
    color: '#FF00FF',
    count: 500,
    lifetime: 10,
    speed: 0.2,
    spread: 5,
    size: 0.2,
    emissive: true
  },
  'fireflies': {
    type: 'fireflies',
    color: '#FFFF00',
    count: 50,
    lifetime: 8,
    speed: 0.3,
    spread: 10,
    size: 0.15,
    emissive: true
  }
}

/**
 * Calculate influence zone for an agent's tools
 */
export function calculateInfluenceRadius(influenceScore: number): number {
  // Base radius 5, scales up to 20 based on influence
  return 5 + (influenceScore / 100) * 15
}

/**
 * Check if a position is within an agent's influence zone
 */
export function isWithinInfluence(
  agentPosition: THREE.Vector3,
  targetPosition: THREE.Vector3,
  influenceScore: number
): boolean {
  const radius = calculateInfluenceRadius(influenceScore)
  const distance = agentPosition.distanceTo(targetPosition)
  return distance <= radius
}

/**
 * Generate a deterministic action based on agent state
 */
export function generateDeterministicAction(
  agentId: string,
  archetype: string,
  influenceScore: number,
  cycleNumber: number
): AgentToolAction | null {
  // Use deterministic seed from agent state
  const seed = hashString(`${agentId}-${cycleNumber}`)

  // Only create structure occasionally (1 in 10 cycles on average)
  if (seed % 10 !== 0) return null

  const category: ToolCategory = 'structure'
  const presetKeys = Object.keys(STRUCTURE_PRESETS)

  // Filter presets by archetype preference
  const preferredPresets = presetKeys.filter(key => {
    if (archetype === 'order') return key.includes('order') || key.includes('obelisk') || key.includes('temple')
    if (archetype === 'logic') return key.includes('data') || key.includes('truth') || key.includes('archive')
    if (archetype === 'chaos') return key.includes('chaos') || key.includes('paradox') || key.includes('portal')
    return true
  })

  const selectedPreset = preferredPresets[seed % preferredPresets.length]
  const preset = STRUCTURE_PRESETS[selectedPreset]

  // Generate position within influence radius
  const radius = calculateInfluenceRadius(influenceScore)
  const angle = (seed * 137.508) % (2 * Math.PI) // Golden angle for good distribution
  const distance = (seed % 100) / 100 * radius * 0.8 // Stay within 80% of max radius

  const position = new THREE.Vector3(
    Math.cos(angle) * distance,
    0,
    Math.sin(angle) * distance
  )

  return {
    toolId: `tool-${seed}`,
    agentId,
    category,
    timestamp: Date.now(),
    action: {
      type: 'create_structure',
      data: {
        ...preset,
        position,
        rotation: new THREE.Euler(0, angle, 0),
        scale: preset.scale || new THREE.Vector3(1, 1, 1)
      } as StructureDefinition
    }
  }
}

// Simple hash function for deterministic randomness
function hashString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  return Math.abs(hash)
}
