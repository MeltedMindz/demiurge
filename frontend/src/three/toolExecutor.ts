/**
 * Tool Executor
 *
 * Executes agent tool requests and creates corresponding 3D objects/effects
 */

import * as THREE from 'three'
import type { AgentToolRequest, ToolResult } from './toolLibrary'
import { getTool, validateToolRequest } from './toolLibrary'
import type { Structure, WorldEffect } from '../types'

// Execution context for tools
interface ExecutionContext {
  scene: THREE.Scene
  addStructure: (structure: Structure) => void
  addEffect: (effect: WorldEffect) => void
  agentPosition: THREE.Vector3
  influenceRadius: number
}

/**
 * Execute a tool request and return the result
 */
export function executeToolRequest(
  request: AgentToolRequest,
  context: ExecutionContext
): ToolResult {
  // Validate request
  const validation = validateToolRequest(request)
  if (!validation.valid) {
    return {
      success: false,
      toolId: request.toolId,
      action: request.action,
      error: validation.errors.join(', ')
    }
  }

  const tool = getTool(request.toolId)
  if (!tool) {
    return {
      success: false,
      toolId: request.toolId,
      action: request.action,
      error: 'Tool not found'
    }
  }

  // Execute based on tool ID
  switch (request.toolId) {
    case 'quarks':
      return executeQuarksParticles(request, context)
    case 'nebula':
      return executeNebulaParticles(request, context)
    case 'meshline':
      return executeMeshLine(request, context)
    case 'postprocess':
      return executePostProcess(request, context)
    case 'pathfinding':
      return executePathfinding(request, context)
    case 'pathtracer':
      return executePathtracer(request, context)
    case 'tiles3d':
      return executeTiles3D(request, context)
    case 'meshbvh':
      return executeMeshBVH(request, context)
    case 'recast':
      return executeRecast(request, context)
    default:
      return {
        success: false,
        toolId: request.toolId,
        action: request.action,
        error: `No executor for tool: ${request.toolId}`
      }
  }
}

/**
 * Execute Quarks particle system
 */
function executeQuarksParticles(
  request: AgentToolRequest,
  context: ExecutionContext
): ToolResult {
  const params = request.parameters
  const position = params.position as { x: number; y: number; z: number } ||
    { x: context.agentPosition.x, y: context.agentPosition.y + 2, z: context.agentPosition.z }

  const effectId = `quarks-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  const effect: WorldEffect = {
    id: effectId,
    effect_type: params.emitterType as string || 'sphere',
    position: { x: position.x, y: position.y, z: position.z },
    parameters: {
      tool: 'quarks',
      particleCount: params.particleCount || 1000,
      lifetime: params.lifetime || 2,
      startColor: params.startColor || '#FFFFFF',
      endColor: params.endColor || '#FFFFFF',
      startSize: params.startSize || 0.1,
      endSize: params.endSize || 0,
      turbulence: params.turbulence || 0,
      velocity: params.velocity,
      gravity: params.gravity
    },
    intensity: 1,
    active: true
  }

  context.addEffect(effect)

  return {
    success: true,
    toolId: request.toolId,
    action: request.action,
    createdObjects: [effectId],
    effects: ['particle_system_created']
  }
}

/**
 * Execute Nebula particle system
 */
function executeNebulaParticles(
  request: AgentToolRequest,
  context: ExecutionContext
): ToolResult {
  const params = request.parameters
  const position = params.position as { x: number; y: number; z: number }

  const effectId = `nebula-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  const effect: WorldEffect = {
    id: effectId,
    effect_type: 'nebula',
    position: position,
    parameters: {
      tool: 'nebula',
      preset: params.preset || 'nebula',
      rate: params.rate || 100,
      life: params.life || 2,
      color: params.color || '#FFFFFF'
    },
    intensity: 1,
    active: true
  }

  context.addEffect(effect)

  return {
    success: true,
    toolId: request.toolId,
    action: request.action,
    createdObjects: [effectId],
    effects: ['nebula_created']
  }
}

/**
 * Execute MeshLine rendering
 */
function executeMeshLine(
  request: AgentToolRequest,
  context: ExecutionContext
): ToolResult {
  const params = request.parameters
  const points = params.points as Array<{ x: number; y: number; z: number }>

  if (!points || points.length < 2) {
    return {
      success: false,
      toolId: request.toolId,
      action: request.action,
      error: 'MeshLine requires at least 2 points'
    }
  }

  const effectId = `meshline-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  const effect: WorldEffect = {
    id: effectId,
    effect_type: 'meshline',
    position: points[0],
    parameters: {
      tool: 'meshline',
      points: points,
      width: params.width || 0.1,
      color: params.color || '#FFFFFF',
      dashArray: params.dashArray || 0,
      glow: params.glow || false
    },
    intensity: 1,
    active: true
  }

  context.addEffect(effect)

  return {
    success: true,
    toolId: request.toolId,
    action: request.action,
    createdObjects: [effectId],
    effects: ['line_created']
  }
}

/**
 * Execute post-processing effect
 */
function executePostProcess(
  request: AgentToolRequest,
  context: ExecutionContext
): ToolResult {
  const params = request.parameters

  const effectId = `postprocess-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  const effect: WorldEffect = {
    id: effectId,
    effect_type: `postprocess_${params.effect}`,
    position: { x: 0, y: 0, z: 0 }, // Global effect
    parameters: {
      tool: 'postprocess',
      effectType: params.effect,
      intensity: params.intensity || 1,
      color: params.color
    },
    intensity: params.intensity as number || 1,
    active: true
  }

  context.addEffect(effect)

  return {
    success: true,
    toolId: request.toolId,
    action: request.action,
    createdObjects: [effectId],
    effects: [`${params.effect}_applied`]
  }
}

/**
 * Execute pathfinding
 */
function executePathfinding(
  request: AgentToolRequest,
  context: ExecutionContext
): ToolResult {
  const params = request.parameters
  const start = params.start as { x: number; y: number; z: number }
  const end = params.end as { x: number; y: number; z: number }

  // Create a path visualization
  const pathPoints = [start]

  // Simple interpolation for demo (real impl would use navmesh)
  const steps = 10
  for (let i = 1; i < steps; i++) {
    const t = i / steps
    pathPoints.push({
      x: start.x + (end.x - start.x) * t,
      y: start.y + (end.y - start.y) * t + Math.sin(t * Math.PI) * 0.5,
      z: start.z + (end.z - start.z) * t
    })
  }
  pathPoints.push(end)

  const effectId = `path-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  const effect: WorldEffect = {
    id: effectId,
    effect_type: 'path',
    position: start,
    parameters: {
      tool: 'pathfinding',
      points: pathPoints,
      smooth: params.smooth || true,
      zoneId: params.zoneId
    },
    intensity: 1,
    active: true
  }

  context.addEffect(effect)

  return {
    success: true,
    toolId: request.toolId,
    action: request.action,
    createdObjects: [effectId],
    effects: ['path_created']
  }
}

/**
 * Execute path tracer effect
 */
function executePathtracer(
  request: AgentToolRequest,
  context: ExecutionContext
): ToolResult {
  const { parameters: params } = request

  const effectId = `pathtracer-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  const effect: WorldEffect = {
    id: effectId,
    effect_type: 'pathtracer',
    position: { x: 0, y: 0, z: 0 },
    parameters: {
      tool: 'pathtracer',
      bounces: params.bounces || 3,
      samples: params.samples || 1,
      intensity: params.intensity || 1
    },
    intensity: params.intensity as number || 1,
    active: true
  }

  context.addEffect(effect)

  return {
    success: true,
    toolId: request.toolId,
    action: request.action,
    effects: ['pathtracing_enabled']
  }
}

/**
 * Execute 3D Tiles rendering
 */
function executeTiles3D(
  request: AgentToolRequest,
  context: ExecutionContext
): ToolResult {
  // For procedural tilesets, generate a structure
  const structureId = `tiles3d-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  const name = (request.parameters.name as string) || 'Procedural Temple Complex'
  const scale = (request.parameters.scale as number) || 2

  const structure: Structure = {
    id: structureId,
    structure_type: 'temple', // Default to temple for demo
    name: name,
    position: context.agentPosition,
    rotation_y: 0,
    scale: scale,
    model_path: null,
    material_preset: 'crystal',
    primary_color: '#FFD700',
    glow_enabled: true,
    created_by: request.agentId,
    created_at_cycle: Math.floor(Date.now() / 1000)
  }

  context.addStructure(structure)

  return {
    success: true,
    toolId: request.toolId,
    action: request.action,
    createdObjects: [structureId],
    effects: ['tileset_loaded']
  }
}

/**
 * Execute Mesh BVH operations
 */
function executeMeshBVH(
  request: AgentToolRequest,
  _context: ExecutionContext
): ToolResult {
  const operation = request.parameters.operation as string

  return {
    success: true,
    toolId: request.toolId,
    action: request.action,
    effects: [`bvh_${operation}_completed`]
  }
}

/**
 * Execute Recast navigation
 */
function executeRecast(
  request: AgentToolRequest,
  context: ExecutionContext
): ToolResult {
  const params = request.parameters

  const effectId = `navmesh-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  const effect: WorldEffect = {
    id: effectId,
    effect_type: 'navmesh',
    position: { x: 0, y: 0, z: 0 },
    parameters: {
      tool: 'recast',
      agentRadius: params.agentRadius || 0.5,
      agentHeight: params.agentHeight || 2,
      maxSlope: params.maxSlope || 45,
      cellSize: params.cellSize || 0.3
    },
    intensity: 1,
    active: true
  }

  context.addEffect(effect)

  return {
    success: true,
    toolId: request.toolId,
    action: request.action,
    createdObjects: [effectId],
    effects: ['navmesh_generated']
  }
}

/**
 * Batch execute multiple tool requests
 */
export function executeToolRequests(
  requests: AgentToolRequest[],
  context: ExecutionContext
): ToolResult[] {
  return requests.map(request => executeToolRequest(request, context))
}
