import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import {
  OrbitControls,
  Environment,
  Grid,
  Stars,
  Float
} from '@react-three/drei'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import * as THREE from 'three'

import Agent from './Agent'
import Structure from './Structure'
import Terrain from './Terrain'
import { useWorldStore } from '../../stores/worldStore'

export default function World() {
  const groupRef = useRef<THREE.Group>(null)

  const { agents, structures } = useWorldStore()

  // Slow world rotation for ambience
  useFrame((_, delta) => {
    if (groupRef.current) {
      // Very subtle rotation
      // groupRef.current.rotation.y += delta * 0.01
    }
  })

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.3} />
      <directionalLight
        position={[50, 100, 50]}
        intensity={1}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-far={200}
        shadow-camera-left={-100}
        shadow-camera-right={100}
        shadow-camera-top={100}
        shadow-camera-bottom={-100}
      />

      {/* Colored point lights for atmosphere */}
      <pointLight position={[-30, 20, 0]} color="#FFD700" intensity={50} distance={60} />
      <pointLight position={[30, 20, 0]} color="#4169E1" intensity={50} distance={60} />
      <pointLight position={[0, 20, 30]} color="#FF00FF" intensity={50} distance={60} />

      {/* Environment */}
      <Stars radius={300} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />

      {/* Camera controls */}
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={20}
        maxDistance={150}
        minPolarAngle={0.2}
        maxPolarAngle={Math.PI / 2.2}
        target={[0, 0, 0]}
      />

      {/* World content */}
      <group ref={groupRef}>
        {/* Ground */}
        <Terrain />

        {/* Grid overlay */}
        <Grid
          position={[0, 0.01, 0]}
          args={[100, 100]}
          cellSize={5}
          cellThickness={0.5}
          cellColor="#333"
          sectionSize={20}
          sectionThickness={1}
          sectionColor="#444"
          fadeDistance={100}
          fadeStrength={1}
          followCamera={false}
        />

        {/* Agents */}
        {agents.map((agent) => (
          <Agent key={agent.id} agent={agent} />
        ))}

        {/* Structures */}
        {structures.map((structure) => (
          <Structure key={structure.id} structure={structure} />
        ))}

        {/* Center marker */}
        <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
          <mesh position={[0, 3, 0]}>
            <octahedronGeometry args={[0.5]} />
            <meshStandardMaterial
              color="#ffffff"
              emissive="#ffffff"
              emissiveIntensity={0.5}
              wireframe
            />
          </mesh>
        </Float>
      </group>

      {/* Post-processing */}
      <EffectComposer>
        <Bloom
          luminanceThreshold={0.5}
          luminanceSmoothing={0.9}
          intensity={0.5}
        />
        <Vignette darkness={0.5} offset={0.3} />
      </EffectComposer>
    </>
  )
}
