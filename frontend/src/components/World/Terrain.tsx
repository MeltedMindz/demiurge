import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export default function Terrain() {
  const meshRef = useRef<THREE.Mesh>(null)

  // Create ground geometry with subtle displacement
  const geometry = useMemo(() => {
    const geo = new THREE.PlaneGeometry(100, 100, 50, 50)
    const positions = geo.attributes.position

    // Add subtle height variation
    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i)
      const z = positions.getY(i) // Y in geometry is Z in world

      // Distance from center
      const dist = Math.sqrt(x * x + z * z)

      // Gentle bowl shape with noise
      const noise = Math.sin(x * 0.1) * Math.cos(z * 0.1) * 0.3
      const bowl = dist * 0.01
      const height = -bowl + noise

      positions.setZ(i, height)
    }

    geo.computeVertexNormals()
    return geo
  }, [])

  return (
    <>
      {/* Main ground */}
      <mesh
        ref={meshRef}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        receiveShadow
      >
        <primitive object={geometry} />
        <meshStandardMaterial
          color="#1a1a2e"
          metalness={0.2}
          roughness={0.8}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Agent domain zones */}
      {/* Axioma domain (order) - geometric pattern */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[-25, 0.02, 0]}
      >
        <circleGeometry args={[20, 6]} />
        <meshBasicMaterial
          color="#FFD700"
          transparent
          opacity={0.05}
        />
      </mesh>

      {/* Veridicus domain (logic) - square grid */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[25, 0.02, 0]}
      >
        <circleGeometry args={[20, 4]} />
        <meshBasicMaterial
          color="#4169E1"
          transparent
          opacity={0.05}
        />
      </mesh>

      {/* Paradoxia domain (chaos) - irregular */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.02, 25]}
      >
        <circleGeometry args={[20, 7]} />
        <meshBasicMaterial
          color="#FF00FF"
          transparent
          opacity={0.05}
        />
      </mesh>

      {/* Center arena */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.03, 0]}
      >
        <ringGeometry args={[8, 10, 32]} />
        <meshBasicMaterial
          color="#ffffff"
          transparent
          opacity={0.1}
        />
      </mesh>
    </>
  )
}
