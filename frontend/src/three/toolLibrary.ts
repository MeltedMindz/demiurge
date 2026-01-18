/**
 * Agent Tool Library
 *
 * This module provides agents with access to powerful Three.js libraries
 * for shaping and modifying the 3D world. Agents can reference these tools
 * freely in their actions.
 */

// THREE types referenced in parameter definitions

// Tool definitions that agents can reference
export interface ToolDefinition {
  id: string
  name: string
  description: string
  capabilities: string[]
  category: ToolCategory
  parameters: ParameterDefinition[]
  examples: ToolExample[]
}

export type ToolCategory =
  | 'rendering'      // Visual quality and effects
  | 'particles'      // Particle systems
  | 'navigation'     // Pathfinding and movement
  | 'geometry'       // Mesh operations
  | 'postprocess'    // Screen effects
  | 'terrain'        // World shaping

export interface ParameterDefinition {
  name: string
  type: 'number' | 'string' | 'boolean' | 'vector3' | 'color' | 'array'
  description: string
  required: boolean
  default?: unknown
}

export interface ToolExample {
  description: string
  parameters: Record<string, unknown>
}

// Agent tool action request
export interface AgentToolRequest {
  agentId: string
  agentName: string
  toolId: string
  action: string
  parameters: Record<string, unknown>
  timestamp: number
  reasoning?: string  // Agent's explanation for using this tool
}

// Tool execution result
export interface ToolResult {
  success: boolean
  toolId: string
  action: string
  createdObjects?: string[]  // IDs of created objects
  modifiedObjects?: string[]
  effects?: string[]
  error?: string
}

/**
 * Complete Tool Library
 * Agents can browse and select from these tools
 */
export const TOOL_LIBRARY: ToolDefinition[] = [
  // ============================================
  // RENDERING TOOLS
  // ============================================
  {
    id: 'pathtracer',
    name: 'GPU Path Tracer',
    description: 'Photorealistic rendering with global illumination, soft shadows, and caustics',
    category: 'rendering',
    capabilities: [
      'Real-time path tracing',
      'Global illumination',
      'Soft shadows',
      'Physically accurate reflections',
      'Caustics and volumetric effects',
      'God rays and light shafts'
    ],
    parameters: [
      { name: 'bounces', type: 'number', description: 'Number of light bounces', required: false, default: 3 },
      { name: 'samples', type: 'number', description: 'Samples per pixel', required: false, default: 1 },
      { name: 'intensity', type: 'number', description: 'Light intensity multiplier', required: false, default: 1 }
    ],
    examples: [
      {
        description: 'Create divine light effect in temple',
        parameters: { bounces: 5, samples: 2, intensity: 1.5 }
      }
    ]
  },

  {
    id: 'tiles3d',
    name: '3D Tiles Renderer',
    description: 'Stream and render massive 3D datasets with level-of-detail management',
    category: 'terrain',
    capabilities: [
      'Render large 3D tile datasets',
      'Automatic level-of-detail',
      'Geographic coordinate support',
      'Efficient memory management',
      'Procedural terrain streaming'
    ],
    parameters: [
      { name: 'url', type: 'string', description: 'Tileset URL or procedural config', required: true },
      { name: 'maxDepth', type: 'number', description: 'Maximum LOD depth', required: false, default: 10 },
      { name: 'errorTarget', type: 'number', description: 'Screen space error target', required: false, default: 6 }
    ],
    examples: [
      {
        description: 'Create vast temple complex',
        parameters: { url: 'procedural://temple-complex', maxDepth: 8 }
      }
    ]
  },

  // ============================================
  // PARTICLE TOOLS
  // ============================================
  {
    id: 'quarks',
    name: 'Quarks Particle System',
    description: 'GPU-accelerated particle systems with complex behaviors and trails',
    category: 'particles',
    capabilities: [
      'GPU-accelerated rendering',
      'Particle trails and ribbons',
      'Bezier curve paths',
      'Force fields (gravity, vortex, turbulence)',
      'Sprite and mesh particles',
      'Sub-emitters'
    ],
    parameters: [
      { name: 'emitterType', type: 'string', description: 'Type: point, sphere, cone, box', required: true },
      { name: 'particleCount', type: 'number', description: 'Maximum particles', required: false, default: 1000 },
      { name: 'lifetime', type: 'number', description: 'Particle lifetime in seconds', required: false, default: 2 },
      { name: 'startColor', type: 'color', description: 'Initial particle color', required: false, default: '#FFFFFF' },
      { name: 'endColor', type: 'color', description: 'Final particle color', required: false, default: '#FFFFFF' },
      { name: 'startSize', type: 'number', description: 'Initial particle size', required: false, default: 0.1 },
      { name: 'endSize', type: 'number', description: 'Final particle size', required: false, default: 0 },
      { name: 'velocity', type: 'vector3', description: 'Initial velocity', required: false },
      { name: 'gravity', type: 'vector3', description: 'Gravity force', required: false },
      { name: 'turbulence', type: 'number', description: 'Turbulence intensity', required: false, default: 0 }
    ],
    examples: [
      {
        description: 'Sacred ascending energy',
        parameters: {
          emitterType: 'sphere',
          particleCount: 500,
          lifetime: 3,
          startColor: '#FFD700',
          endColor: '#FFFFFF',
          velocity: { x: 0, y: 2, z: 0 },
          turbulence: 0.3
        }
      },
      {
        description: 'Chaos reality distortion',
        parameters: {
          emitterType: 'point',
          particleCount: 2000,
          lifetime: 1,
          startColor: '#FF00FF',
          endColor: '#00FFFF',
          turbulence: 2.0,
          gravity: { x: 0, y: 0, z: 0 }
        }
      }
    ]
  },

  {
    id: 'nebula',
    name: 'Nebula Particle Engine',
    description: 'JSON-configurable particle systems with complex behaviors',
    category: 'particles',
    capabilities: [
      'JSON-based particle definitions',
      'Sprite and mesh particles',
      'Behaviors: gravity, rotation, scale, color',
      'Zone-based emission',
      'Particle pooling'
    ],
    parameters: [
      { name: 'preset', type: 'string', description: 'Preset: nebula, fire, smoke, magic, data', required: false },
      { name: 'rate', type: 'number', description: 'Emission rate per second', required: false, default: 100 },
      { name: 'life', type: 'number', description: 'Particle lifetime', required: false, default: 2 },
      { name: 'position', type: 'vector3', description: 'Emitter position', required: true },
      { name: 'color', type: 'color', description: 'Particle color', required: false, default: '#FFFFFF' }
    ],
    examples: [
      {
        description: 'Cosmic background nebula',
        parameters: {
          preset: 'nebula',
          rate: 50,
          life: 10,
          position: { x: 0, y: 20, z: 0 },
          color: '#8844FF'
        }
      }
    ]
  },

  // ============================================
  // NAVIGATION TOOLS
  // ============================================
  {
    id: 'pathfinding',
    name: 'Pathfinding System',
    description: 'A* pathfinding on navigation meshes with zone support',
    category: 'navigation',
    capabilities: [
      'A* pathfinding algorithm',
      'Navigation mesh support',
      'Waypoint systems',
      'Path smoothing',
      'Zone-based navigation',
      'Agent grouping'
    ],
    parameters: [
      { name: 'start', type: 'vector3', description: 'Start position', required: true },
      { name: 'end', type: 'vector3', description: 'End position', required: true },
      { name: 'zoneId', type: 'string', description: 'Navigation zone ID', required: false },
      { name: 'smooth', type: 'boolean', description: 'Smooth the path', required: false, default: true }
    ],
    examples: [
      {
        description: 'Create sacred pilgrimage path',
        parameters: {
          start: { x: 0, y: 0, z: 0 },
          end: { x: -25, y: 0, z: -10 },
          smooth: true
        }
      }
    ]
  },

  {
    id: 'recast',
    name: 'Recast Navigation',
    description: 'Dynamic navmesh generation with crowd simulation',
    category: 'navigation',
    capabilities: [
      'Dynamic navmesh generation',
      'Crowd simulation',
      'Obstacle avoidance',
      'Off-mesh connections (portals)',
      'Agent steering',
      'Tile-based updates'
    ],
    parameters: [
      { name: 'agentRadius', type: 'number', description: 'Agent collision radius', required: false, default: 0.5 },
      { name: 'agentHeight', type: 'number', description: 'Agent height', required: false, default: 2 },
      { name: 'maxSlope', type: 'number', description: 'Maximum walkable slope', required: false, default: 45 },
      { name: 'cellSize', type: 'number', description: 'Voxel cell size', required: false, default: 0.3 }
    ],
    examples: [
      {
        description: 'Generate temple navigation mesh',
        parameters: {
          agentRadius: 0.6,
          agentHeight: 1.8,
          maxSlope: 30
        }
      }
    ]
  },

  // ============================================
  // POST-PROCESSING TOOLS
  // ============================================
  {
    id: 'postprocess',
    name: 'Post-Processing Effects',
    description: 'Screen-space visual effects including bloom, glitch, and color grading',
    category: 'postprocess',
    capabilities: [
      'Bloom and glow',
      'Depth of field',
      'Motion blur',
      'Color grading',
      'Glitch effects',
      'Chromatic aberration',
      'Vignette',
      'God rays',
      'Custom shader passes'
    ],
    parameters: [
      { name: 'effect', type: 'string', description: 'Effect type', required: true },
      { name: 'intensity', type: 'number', description: 'Effect intensity', required: false, default: 1 },
      { name: 'color', type: 'color', description: 'Effect color (if applicable)', required: false }
    ],
    examples: [
      {
        description: 'Divine bloom effect',
        parameters: {
          effect: 'bloom',
          intensity: 1.5
        }
      },
      {
        description: 'Chaos glitch distortion',
        parameters: {
          effect: 'glitch',
          intensity: 2.0
        }
      },
      {
        description: 'Order zone color grading',
        parameters: {
          effect: 'colorGrade',
          color: '#FFD700',
          intensity: 0.3
        }
      }
    ]
  },

  // ============================================
  // GEOMETRY TOOLS
  // ============================================
  {
    id: 'meshbvh',
    name: 'Mesh BVH Operations',
    description: 'Accelerated raycasting and mesh operations using BVH structures',
    category: 'geometry',
    capabilities: [
      'Fast BVH-accelerated raycasting',
      'Mesh-to-mesh intersection',
      'Point containment tests',
      'Distance queries',
      'GPU raycasting',
      'Shapecast operations'
    ],
    parameters: [
      { name: 'operation', type: 'string', description: 'Operation: raycast, intersect, contains', required: true },
      { name: 'origin', type: 'vector3', description: 'Ray or point origin', required: true },
      { name: 'direction', type: 'vector3', description: 'Ray direction (for raycast)', required: false },
      { name: 'maxDistance', type: 'number', description: 'Maximum distance', required: false, default: 100 }
    ],
    examples: [
      {
        description: 'Check structure visibility',
        parameters: {
          operation: 'raycast',
          origin: { x: 0, y: 2, z: 0 },
          direction: { x: 1, y: 0, z: 0 }
        }
      }
    ]
  },

  {
    id: 'meshline',
    name: 'MeshLine Renderer',
    description: 'Beautiful variable-width line rendering with textures',
    category: 'geometry',
    capabilities: [
      'Variable width lines',
      'Textured lines',
      'Dashed lines',
      'Proper caps and joins',
      'Animated lines',
      'Glowing lines'
    ],
    parameters: [
      { name: 'points', type: 'array', description: 'Array of Vector3 points', required: true },
      { name: 'width', type: 'number', description: 'Line width', required: false, default: 0.1 },
      { name: 'color', type: 'color', description: 'Line color', required: false, default: '#FFFFFF' },
      { name: 'dashArray', type: 'number', description: 'Dash pattern (0 = solid)', required: false, default: 0 },
      { name: 'glow', type: 'boolean', description: 'Add glow effect', required: false, default: false }
    ],
    examples: [
      {
        description: 'Sacred geometry connection',
        parameters: {
          points: [{ x: 0, y: 0, z: 0 }, { x: 10, y: 5, z: 0 }],
          width: 0.2,
          color: '#FFD700',
          glow: true
        }
      },
      {
        description: 'Data flow visualization',
        parameters: {
          points: [{ x: 15, y: 0, z: 0 }, { x: 0, y: 3, z: 0 }],
          width: 0.1,
          color: '#00FFFF',
          dashArray: 0.1
        }
      }
    ]
  }
]

/**
 * Get tool by ID
 */
export function getTool(toolId: string): ToolDefinition | undefined {
  return TOOL_LIBRARY.find(t => t.id === toolId)
}

/**
 * Get tools by category
 */
export function getToolsByCategory(category: ToolCategory): ToolDefinition[] {
  return TOOL_LIBRARY.filter(t => t.category === category)
}

/**
 * Get all tool IDs
 */
export function getToolIds(): string[] {
  return TOOL_LIBRARY.map(t => t.id)
}

/**
 * Validate tool request parameters
 */
export function validateToolRequest(request: AgentToolRequest): { valid: boolean; errors: string[] } {
  const tool = getTool(request.toolId)
  if (!tool) {
    return { valid: false, errors: [`Unknown tool: ${request.toolId}`] }
  }

  const errors: string[] = []

  for (const param of tool.parameters) {
    if (param.required && !(param.name in request.parameters)) {
      errors.push(`Missing required parameter: ${param.name}`)
    }
  }

  return { valid: errors.length === 0, errors }
}

/**
 * Archetype tool preferences
 * Each archetype has tools they prefer to use
 */
export const ARCHETYPE_TOOL_PREFERENCES: Record<string, string[]> = {
  order: ['pathtracer', 'tiles3d', 'meshline', 'pathfinding'],
  logic: ['meshbvh', 'recast', 'postprocess', 'quarks'],
  chaos: ['quarks', 'nebula', 'postprocess', 'meshline']
}

/**
 * Get preferred tools for an archetype
 */
export function getPreferredTools(archetype: string): ToolDefinition[] {
  const preferredIds = ARCHETYPE_TOOL_PREFERENCES[archetype] || []
  return preferredIds.map(id => getTool(id)).filter((t): t is ToolDefinition => t !== undefined)
}

/**
 * Generate a deterministic tool action based on agent state
 */
export function suggestToolAction(
  agentId: string,
  archetype: string,
  cycleNumber: number,
  _context: string
): AgentToolRequest | null {
  const preferredTools = getPreferredTools(archetype)
  if (preferredTools.length === 0) return null

  // Deterministic selection based on cycle
  const toolIndex = cycleNumber % preferredTools.length
  const tool = preferredTools[toolIndex]

  // Get example parameters
  const example = tool.examples[cycleNumber % tool.examples.length]

  return {
    agentId,
    agentName: archetype,
    toolId: tool.id,
    action: 'create',
    parameters: example.parameters,
    timestamp: Date.now(),
    reasoning: `Using ${tool.name} to ${example.description}`
  }
}
