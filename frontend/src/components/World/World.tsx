import { useRef, useMemo, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import {
  OrbitControls,
  Grid,
  Stars,
  Float,
  Sky,
  Cloud,
  Sparkles
} from '@react-three/drei'
import { EffectComposer, Bloom, Vignette, ChromaticAberration } from '@react-three/postprocessing'
import * as THREE from 'three'

import Agent, { AgentDisplayMode } from './Agent'
import Structure from './Structure'
import Terrain from './Terrain'
import ParticleEffects from './ParticleEffects'
import { useWorldStore } from '../../stores/worldStore'

// Mystical fog component
function MysticalFog() {
  const fogRef = useRef<THREE.Fog>(null)

  useFrame((state) => {
    if (fogRef.current) {
      // Subtle fog density variation
      const variation = Math.sin(state.clock.elapsedTime * 0.1) * 10
      fogRef.current.far = 150 + variation
    }
  })

  return <fog ref={fogRef} attach="fog" args={['#0a0a15', 50, 150]} />
}

// Floating mystical orbs in the environment
function AmbientOrbs() {
  const orbPositions = useMemo(() => {
    const positions: [number, number, number][] = []
    for (let i = 0; i < 20; i++) {
      positions.push([
        (Math.random() - 0.5) * 80,
        5 + Math.random() * 30,
        (Math.random() - 0.5) * 80
      ])
    }
    return positions
  }, [])

  return (
    <>
      {orbPositions.map((pos, i) => (
        <Float key={i} speed={1 + Math.random()} floatIntensity={2}>
          <mesh position={pos}>
            <sphereGeometry args={[0.1 + Math.random() * 0.2, 8, 8]} />
            <meshBasicMaterial
              color={['#FFD700', '#4169E1', '#FF00FF', '#00FFFF'][i % 4]}
              transparent
              opacity={0.6}
            />
          </mesh>
        </Float>
      ))}
    </>
  )
}

// Central altar/platform where debates happen
function CentralPlatform() {
  const platformRef = useRef<THREE.Group>(null)

  useFrame((state) => {
    if (platformRef.current) {
      // Subtle glow pulse
      platformRef.current.children.forEach((child, i) => {
        if (child instanceof THREE.Mesh && child.material instanceof THREE.MeshStandardMaterial) {
          child.material.emissiveIntensity = 0.3 + Math.sin(state.clock.elapsedTime * 2 + i) * 0.1
        }
      })
    }
  })

  return (
    <group ref={platformRef} position={[0, 0.02, 0]}>
      {/* Main circular platform */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <ringGeometry args={[0, 8, 64]} />
        <meshStandardMaterial
          color="#1a1a2e"
          emissive="#FFD700"
          emissiveIntensity={0.2}
          metalness={0.8}
          roughness={0.3}
        />
      </mesh>

      {/* Inner sacred geometry */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <ringGeometry args={[2, 2.2, 6]} />
        <meshStandardMaterial
          color="#FFD700"
          emissive="#FFD700"
          emissiveIntensity={0.5}
          transparent
          opacity={0.7}
        />
      </mesh>

      {/* Triangle markers for each agent position */}
      {[0, 120, 240].map((angle, i) => {
        const rad = (angle * Math.PI) / 180
        const x = Math.cos(rad) * 6
        const z = Math.sin(rad) * 6
        const colors = ['#FFD700', '#4169E1', '#FF00FF']
        return (
          <mesh key={i} position={[x, 0.02, z]} rotation={[-Math.PI / 2, 0, rad]}>
            <circleGeometry args={[0.8, 3]} />
            <meshStandardMaterial
              color={colors[i]}
              emissive={colors[i]}
              emissiveIntensity={0.4}
              transparent
              opacity={0.6}
            />
          </mesh>
        )
      })}

      {/* Pillar of light effect at center */}
      <mesh position={[0, 15, 0]}>
        <cylinderGeometry args={[0.5, 2, 30, 16, 1, true]} />
        <meshBasicMaterial
          color="#ffffff"
          transparent
          opacity={0.05}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  )
}

// Ethereal columns around the debate area
function EtherealColumns() {
  const columns = useMemo(() => {
    const cols: { pos: [number, number, number]; height: number; color: string }[] = []
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2
      cols.push({
        pos: [Math.cos(angle) * 25, 0, Math.sin(angle) * 25],
        height: 15 + Math.random() * 10,
        color: i % 2 === 0 ? '#2a2a4e' : '#1e1e3e'
      })
    }
    return cols
  }, [])

  return (
    <>
      {columns.map((col, i) => (
        <group key={i} position={col.pos}>
          {/* Column base */}
          <mesh position={[0, 0.5, 0]} castShadow>
            <cylinderGeometry args={[1.5, 2, 1, 8]} />
            <meshStandardMaterial color={col.color} metalness={0.6} roughness={0.4} />
          </mesh>

          {/* Column shaft */}
          <mesh position={[0, col.height / 2 + 1, 0]} castShadow>
            <cylinderGeometry args={[1, 1, col.height, 8]} />
            <meshStandardMaterial color={col.color} metalness={0.5} roughness={0.5} />
          </mesh>

          {/* Glowing orb on top */}
          <Float speed={2} floatIntensity={0.5}>
            <mesh position={[0, col.height + 2, 0]}>
              <sphereGeometry args={[0.5, 16, 16]} />
              <meshStandardMaterial
                color="#ffffff"
                emissive={['#FFD700', '#4169E1', '#FF00FF'][i % 3]}
                emissiveIntensity={1}
              />
            </mesh>
          </Float>
        </group>
      ))}
    </>
  )
}

export default function World() {
  const groupRef = useRef<THREE.Group>(null)
  const { agents, structures, effects } = useWorldStore()

  // Agent display mode - can be switched via UI
  const [displayMode] = useState<AgentDisplayMode>('humanoid')

  return (
    <>
      {/* Mystical fog */}
      <MysticalFog />

      {/* Sky and environment */}
      <Sky
        distance={450000}
        sunPosition={[0, -1, 0]}
        inclination={0}
        azimuth={0.25}
        rayleigh={0.5}
      />

      {/* Lighting - Enhanced for dramatic effect */}
      <ambientLight intensity={0.15} color="#8888ff" />

      {/* Main dramatic light from above */}
      <directionalLight
        position={[0, 100, 0]}
        intensity={0.8}
        color="#ffffff"
        castShadow
        shadow-mapSize={[4096, 4096]}
        shadow-camera-far={200}
        shadow-camera-left={-50}
        shadow-camera-right={50}
        shadow-camera-top={50}
        shadow-camera-bottom={-50}
        shadow-bias={-0.0001}
      />

      {/* Rim lighting for dramatic silhouettes */}
      <directionalLight position={[-50, 30, -50]} intensity={0.3} color="#4169E1" />
      <directionalLight position={[50, 30, -50]} intensity={0.3} color="#FFD700" />

      {/* Agent-specific spotlights */}
      <spotLight
        position={[-15, 20, 0]}
        angle={0.3}
        penumbra={0.8}
        intensity={100}
        color="#FFD700"
        castShadow
        target-position={[-10, 0, 0]}
      />
      <spotLight
        position={[15, 20, 0]}
        angle={0.3}
        penumbra={0.8}
        intensity={100}
        color="#4169E1"
        castShadow
        target-position={[10, 0, 0]}
      />
      <spotLight
        position={[0, 20, 15]}
        angle={0.3}
        penumbra={0.8}
        intensity={100}
        color="#FF00FF"
        castShadow
        target-position={[0, 0, 10]}
      />

      {/* Hemisphere light for better ambient */}
      <hemisphereLight args={['#4444aa', '#222233', 0.4]} />

      {/* Environment */}
      <Stars radius={400} depth={100} count={8000} factor={6} saturation={0.5} fade speed={0.5} />

      {/* Mystical sparkles */}
      <Sparkles
        count={200}
        scale={100}
        size={3}
        speed={0.5}
        opacity={0.5}
        color="#FFD700"
      />

      {/* Subtle clouds */}
      <group position={[0, 60, 0]}>
        <Cloud opacity={0.1} speed={0.1} segments={20} color="#4444aa" />
        <Cloud position={[-30, 10, -20]} opacity={0.08} speed={0.15} segments={15} color="#6644aa" />
        <Cloud position={[40, -5, 30]} opacity={0.06} speed={0.12} segments={18} color="#4466aa" />
      </group>

      {/* Camera controls - adjusted for humanoid scale */}
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={10}
        maxDistance={100}
        minPolarAngle={0.3}
        maxPolarAngle={Math.PI / 2.1}
        target={[0, 1, 0]}
        enableDamping={true}
        dampingFactor={0.05}
      />

      {/* World content */}
      <group ref={groupRef}>
        {/* Ground */}
        <Terrain />

        {/* Central platform */}
        <CentralPlatform />

        {/* Ethereal columns */}
        <EtherealColumns />

        {/* Ambient floating orbs */}
        <AmbientOrbs />

        {/* Subtle grid (more mystical) */}
        <Grid
          position={[0, 0.02, 0]}
          args={[200, 200]}
          cellSize={10}
          cellThickness={0.3}
          cellColor="#1a1a3a"
          sectionSize={50}
          sectionThickness={0.5}
          sectionColor="#2a2a5a"
          fadeDistance={80}
          fadeStrength={1.5}
          followCamera={false}
          infiniteGrid
        />

        {/* Agents - now with humanoid avatars */}
        {agents.map((agent) => (
          <Agent key={agent.id} agent={agent} displayMode={displayMode} />
        ))}

        {/* Structures */}
        {structures.map((structure) => (
          <Structure key={structure.id} structure={structure} />
        ))}

        {/* Particle effects */}
        <ParticleEffects effects={effects} />

        {/* Central focus point - floating crystalline structure */}
        <Float speed={1} rotationIntensity={0.3} floatIntensity={0.3}>
          <group position={[0, 8, 0]}>
            <mesh>
              <octahedronGeometry args={[1]} />
              <meshStandardMaterial
                color="#ffffff"
                emissive="#ffffff"
                emissiveIntensity={0.8}
                metalness={0.9}
                roughness={0.1}
                transparent
                opacity={0.8}
              />
            </mesh>
            <mesh rotation={[0, Math.PI / 4, 0]}>
              <octahedronGeometry args={[0.6]} />
              <meshStandardMaterial
                color="#FFD700"
                emissive="#FFD700"
                emissiveIntensity={0.5}
                wireframe
              />
            </mesh>
          </group>
        </Float>
      </group>

      {/* Enhanced post-processing */}
      <EffectComposer>
        <Bloom
          luminanceThreshold={0.4}
          luminanceSmoothing={0.9}
          intensity={0.8}
          radius={0.8}
        />
        <Vignette darkness={0.6} offset={0.2} />
        <ChromaticAberration
          offset={new THREE.Vector2(0.0005, 0.0005)}
          radialModulation={true}
          modulationOffset={0.5}
        />
      </EffectComposer>
    </>
  )
}
