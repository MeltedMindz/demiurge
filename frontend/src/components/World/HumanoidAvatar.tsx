/**
 * Humanoid Avatar Component
 *
 * Renders human-like 3D avatars for agents using VRM or GLTF models.
 * Supports animations, lip sync, and emotional expressions.
 */

import React, { useRef, useEffect, useState, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF, useAnimations } from '@react-three/drei'
import * as THREE from 'three'
import { VRM, VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

// Avatar configuration per agent archetype
export const AGENT_AVATARS: Record<string, AvatarConfig> = {
  order: {
    // Axioma - Regal, structured appearance
    modelUrl: '/models/avatars/axioma.vrm',
    fallbackUrl: '/models/avatars/axioma.glb',
    scale: 1.0,
    idleAnimation: 'idle_noble',
    talkAnimation: 'talk_formal',
    emoteAnimations: {
      pleased: 'gesture_approval',
      contemplative: 'gesture_think',
      concerned: 'gesture_worry'
    }
  },
  logic: {
    // Veridicus - Analytical, precise appearance
    modelUrl: '/models/avatars/veridicus.vrm',
    fallbackUrl: '/models/avatars/veridicus.glb',
    scale: 1.0,
    idleAnimation: 'idle_analytical',
    talkAnimation: 'talk_explain',
    emoteAnimations: {
      curious: 'gesture_question',
      excited: 'gesture_eureka',
      frustrated: 'gesture_dismiss'
    }
  },
  chaos: {
    // Paradoxia - Dynamic, unpredictable appearance
    modelUrl: '/models/avatars/paradoxia.vrm',
    fallbackUrl: '/models/avatars/paradoxia.glb',
    scale: 1.0,
    idleAnimation: 'idle_playful',
    talkAnimation: 'talk_animated',
    emoteAnimations: {
      excited: 'gesture_celebrate',
      inspired: 'gesture_magic',
      curious: 'gesture_mischief'
    }
  }
}

interface AvatarConfig {
  modelUrl: string
  fallbackUrl: string
  scale: number
  idleAnimation: string
  talkAnimation: string
  emoteAnimations: Record<string, string>
}

interface HumanoidAvatarProps {
  archetype: 'order' | 'logic' | 'chaos'
  position: [number, number, number]
  rotation?: [number, number, number]
  isTalking?: boolean
  emotionalState?: string
  lookAtTarget?: THREE.Vector3
  primaryColor?: string
  glowIntensity?: number
}

// Placeholder avatar using basic geometry until real models are loaded
const PlaceholderAvatar: React.FC<{
  archetype: string
  primaryColor: string
  glowIntensity: number
  isTalking: boolean
}> = ({ archetype, primaryColor, glowIntensity, isTalking }) => {
  const groupRef = useRef<THREE.Group>(null)
  const headRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (!groupRef.current) return

    // Subtle idle animation
    groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 2) * 0.05

    // Head movement when talking
    if (headRef.current && isTalking) {
      headRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 8) * 0.05
      headRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 6) * 0.03
    }
  })

  const bodyShape = useMemo(() => {
    switch (archetype) {
      case 'order':
        return { bodyWidth: 0.4, bodyHeight: 1.2, headSize: 0.25 }
      case 'logic':
        return { bodyWidth: 0.35, bodyHeight: 1.15, headSize: 0.28 }
      case 'chaos':
        return { bodyWidth: 0.38, bodyHeight: 1.1, headSize: 0.26 }
      default:
        return { bodyWidth: 0.4, bodyHeight: 1.2, headSize: 0.25 }
    }
  }, [archetype])

  return (
    <group ref={groupRef}>
      {/* Body */}
      <mesh position={[0, bodyShape.bodyHeight / 2, 0]} castShadow>
        <capsuleGeometry args={[bodyShape.bodyWidth, bodyShape.bodyHeight, 8, 16]} />
        <meshStandardMaterial
          color={primaryColor}
          emissive={primaryColor}
          emissiveIntensity={glowIntensity * 0.3}
          metalness={0.3}
          roughness={0.7}
        />
      </mesh>

      {/* Head */}
      <mesh
        ref={headRef}
        position={[0, bodyShape.bodyHeight + bodyShape.headSize + 0.1, 0]}
        castShadow
      >
        <sphereGeometry args={[bodyShape.headSize, 32, 32]} />
        <meshStandardMaterial
          color={primaryColor}
          emissive={primaryColor}
          emissiveIntensity={glowIntensity * 0.5}
          metalness={0.2}
          roughness={0.6}
        />
      </mesh>

      {/* Eyes glow */}
      <mesh position={[0.08, bodyShape.bodyHeight + bodyShape.headSize + 0.15, bodyShape.headSize - 0.05]}>
        <sphereGeometry args={[0.03, 16, 16]} />
        <meshBasicMaterial color="#FFFFFF" />
      </mesh>
      <mesh position={[-0.08, bodyShape.bodyHeight + bodyShape.headSize + 0.15, bodyShape.headSize - 0.05]}>
        <sphereGeometry args={[0.03, 16, 16]} />
        <meshBasicMaterial color="#FFFFFF" />
      </mesh>

      {/* Talking indicator */}
      {isTalking && (
        <mesh position={[0, bodyShape.bodyHeight + 0.3, 0.3]}>
          <ringGeometry args={[0.1, 0.15, 32]} />
          <meshBasicMaterial color={primaryColor} transparent opacity={0.6} side={THREE.DoubleSide} />
        </mesh>
      )}
    </group>
  )
}

// VRM Avatar loader and renderer
const VRMAvatar: React.FC<{
  url: string
  isTalking: boolean
  emotionalState?: string
  lookAtTarget?: THREE.Vector3
}> = ({ url, isTalking, emotionalState, lookAtTarget }) => {
  const [vrm, setVrm] = useState<VRM | null>(null)
  const mixerRef = useRef<THREE.AnimationMixer | null>(null)

  useEffect(() => {
    const loader = new GLTFLoader()
    loader.register((parser) => new VRMLoaderPlugin(parser))

    loader.load(
      url,
      (gltf) => {
        const loadedVrm = gltf.userData.vrm as VRM
        if (loadedVrm) {
          VRMUtils.removeUnnecessaryVertices(gltf.scene)
          VRMUtils.removeUnnecessaryJoints(gltf.scene)
          loadedVrm.scene.traverse((obj) => {
            obj.frustumCulled = false
          })
          setVrm(loadedVrm)
          mixerRef.current = new THREE.AnimationMixer(loadedVrm.scene)
        }
      },
      undefined,
      (error) => {
        console.error('Error loading VRM:', error)
      }
    )

    return () => {
      if (vrm) {
        VRMUtils.deepDispose(vrm.scene)
      }
    }
  }, [url])

  useFrame((state, delta) => {
    if (vrm) {
      // Update VRM
      vrm.update(delta)

      // Look at target - VRM lookAt expects an Object3D
      if (lookAtTarget && vrm.lookAt) {
        // Create a target object if needed
        const targetObj = new THREE.Object3D()
        targetObj.position.copy(lookAtTarget)
        vrm.lookAt.target = targetObj
      }

      // Talking animation - move mouth blend shapes
      if (isTalking && vrm.expressionManager) {
        const mouthValue = (Math.sin(state.clock.elapsedTime * 15) + 1) / 2 * 0.5
        vrm.expressionManager.setValue('aa', mouthValue)
      } else if (vrm.expressionManager) {
        vrm.expressionManager.setValue('aa', 0)
      }

      // Emotional expressions
      if (emotionalState && vrm.expressionManager) {
        switch (emotionalState) {
          case 'pleased':
          case 'excited':
            vrm.expressionManager.setValue('happy', 0.7)
            break
          case 'concerned':
          case 'frustrated':
            vrm.expressionManager.setValue('sad', 0.5)
            break
          case 'curious':
            vrm.expressionManager.setValue('surprised', 0.4)
            break
          default:
            vrm.expressionManager.setValue('neutral', 1)
        }
      }

      // Update animation mixer
      if (mixerRef.current) {
        mixerRef.current.update(delta)
      }
    }
  })

  if (!vrm) return null

  return <primitive object={vrm.scene} />
}

// GLTF Avatar (for Ready Player Me or custom models)
const GLTFAvatar: React.FC<{
  url: string
  isTalking: boolean
  emotionalState?: string
}> = ({ url, isTalking }) => {
  const { scene, animations } = useGLTF(url)
  const { actions } = useAnimations(animations, scene)
  const clonedScene = useMemo(() => scene.clone(), [scene])

  useEffect(() => {
    // Play idle animation
    const idleAction = actions['idle'] || actions['Idle'] || Object.values(actions)[0]
    if (idleAction) {
      idleAction.play()
    }
  }, [actions])

  useEffect(() => {
    // Handle talking animation
    const talkAction = actions['talk'] || actions['Talk'] || actions['talking']
    const idleAction = actions['idle'] || actions['Idle'] || Object.values(actions)[0]

    if (isTalking && talkAction) {
      talkAction.reset().fadeIn(0.2).play()
      if (idleAction) idleAction.fadeOut(0.2)
    } else if (!isTalking && idleAction) {
      idleAction.reset().fadeIn(0.2).play()
      if (talkAction) talkAction.fadeOut(0.2)
    }
  }, [isTalking, actions])

  return <primitive object={clonedScene} />
}

// Main component
export const HumanoidAvatar: React.FC<HumanoidAvatarProps> = ({
  archetype,
  position,
  rotation = [0, 0, 0],
  isTalking = false,
  emotionalState,
  lookAtTarget,
  primaryColor = '#FFFFFF',
  glowIntensity = 1.0
}) => {
  const [modelLoaded, setModelLoaded] = useState(false)
  const [modelType, setModelType] = useState<'vrm' | 'gltf' | 'placeholder'>('placeholder')
  const config = AGENT_AVATARS[archetype]

  // Try to load VRM first, then GLTF, fallback to placeholder
  useEffect(() => {
    const tryLoadModel = async () => {
      try {
        // Check if VRM exists
        const vrmResponse = await fetch(config.modelUrl, { method: 'HEAD' })
        if (vrmResponse.ok) {
          setModelType('vrm')
          setModelLoaded(true)
          return
        }
      } catch {
        // VRM not available
      }

      try {
        // Check if GLTF exists
        const gltfResponse = await fetch(config.fallbackUrl, { method: 'HEAD' })
        if (gltfResponse.ok) {
          setModelType('gltf')
          setModelLoaded(true)
          return
        }
      } catch {
        // GLTF not available
      }

      // Use placeholder
      setModelType('placeholder')
      setModelLoaded(true)
    }

    tryLoadModel()
  }, [config])

  return (
    <group position={position} rotation={rotation}>
      {modelType === 'placeholder' && (
        <PlaceholderAvatar
          archetype={archetype}
          primaryColor={primaryColor}
          glowIntensity={glowIntensity}
          isTalking={isTalking}
        />
      )}

      {modelType === 'vrm' && modelLoaded && (
        <VRMAvatar
          url={config.modelUrl}
          isTalking={isTalking}
          emotionalState={emotionalState}
          lookAtTarget={lookAtTarget}
        />
      )}

      {modelType === 'gltf' && modelLoaded && (
        <GLTFAvatar
          url={config.fallbackUrl}
          isTalking={isTalking}
          emotionalState={emotionalState}
        />
      )}

      {/* Name label floating above */}
      <group position={[0, 2.5, 0]}>
        {/* This could be replaced with Text from drei */}
      </group>
    </group>
  )
}

export default HumanoidAvatar
