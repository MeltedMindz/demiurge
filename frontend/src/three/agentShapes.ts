/**
 * Agent Shape Library
 * Agents can deterministically choose from these shapes based on their state
 */

import type { ShapeType, ShapeConfig } from '../types'
export type { ShapeType, ShapeConfig }

// Shape presets agents can choose from
export const SHAPE_PRESETS: Record<string, ShapeConfig> = {
  // Order-aligned shapes (Axioma prefers these)
  'crystal_perfect': {
    type: 'icosahedron',
    args: [1, 0],
    metalness: 0.9,
    roughness: 0.1,
    emissiveIntensity: 0.3,
    animation: 'spin'
  },
  'sacred_octahedron': {
    type: 'octahedron',
    args: [1],
    metalness: 0.8,
    roughness: 0.2,
    emissiveIntensity: 0.4,
    animation: 'float'
  },
  'divine_dodecahedron': {
    type: 'dodecahedron',
    args: [1, 0],
    metalness: 0.85,
    roughness: 0.15,
    emissiveIntensity: 0.35,
    animation: 'spin'
  },
  'primal_tetrahedron': {
    type: 'tetrahedron',
    args: [1, 0],
    metalness: 0.9,
    roughness: 0.1,
    emissiveIntensity: 0.5,
    animation: 'pulse'
  },

  // Logic-aligned shapes (Veridicus prefers these)
  'logical_cube': {
    type: 'cube',
    args: [1.5, 1.5, 1.5],
    metalness: 0.6,
    roughness: 0.4,
    emissiveIntensity: 0.2,
    animation: 'float'
  },
  'perfect_sphere': {
    type: 'sphere',
    args: [1, 32, 32],
    metalness: 0.5,
    roughness: 0.5,
    emissiveIntensity: 0.2,
    animation: 'pulse'
  },
  'infinite_torus': {
    type: 'torus',
    args: [0.8, 0.3, 16, 32],
    metalness: 0.7,
    roughness: 0.3,
    emissiveIntensity: 0.3,
    animation: 'spin'
  },
  'data_cylinder': {
    type: 'cylinder',
    args: [0.5, 0.5, 2, 8],
    metalness: 0.6,
    roughness: 0.4,
    wireframe: true,
    emissiveIntensity: 0.4,
    animation: 'spin'
  },

  // Chaos-aligned shapes (Paradoxia prefers these)
  'chaos_knot': {
    type: 'torusKnot',
    args: [0.6, 0.2, 128, 16],
    metalness: 0.4,
    roughness: 0.6,
    emissiveIntensity: 0.6,
    animation: 'morph'
  },
  'void_ring': {
    type: 'ring',
    args: [0.5, 1, 32],
    metalness: 0.3,
    roughness: 0.7,
    emissiveIntensity: 0.8,
    animation: 'glitch'
  },
  'glitch_star': {
    type: 'star',
    args: [1, 0.5, 5],
    metalness: 0.5,
    roughness: 0.5,
    emissiveIntensity: 0.7,
    animation: 'glitch'
  },
  'flux_form': {
    type: 'flux',
    args: [],
    metalness: 0.4,
    roughness: 0.6,
    emissiveIntensity: 0.9,
    animation: 'morph'
  }
}

// What shapes each archetype prefers
export const ARCHETYPE_SHAPE_PREFERENCES: Record<string, string[]> = {
  order: [
    'crystal_perfect',
    'sacred_octahedron',
    'divine_dodecahedron',
    'primal_tetrahedron'
  ],
  logic: [
    'logical_cube',
    'perfect_sphere',
    'infinite_torus',
    'data_cylinder'
  ],
  chaos: [
    'chaos_knot',
    'void_ring',
    'glitch_star',
    'flux_form'
  ]
}

/**
 * Deterministically select a shape based on agent state
 */
export function selectShapeForAgent(
  archetype: string,
  influenceScore: number,
  proposalsAccepted: number,
  cycleNumber: number
): string {
  const preferences = ARCHETYPE_SHAPE_PREFERENCES[archetype] || ARCHETYPE_SHAPE_PREFERENCES.chaos

  // Use a deterministic formula based on agent stats
  const seed = influenceScore + (proposalsAccepted * 10) + (cycleNumber % 100)
  const index = seed % preferences.length

  return preferences[index]
}
