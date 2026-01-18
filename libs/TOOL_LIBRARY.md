# Agent Tool Library

This directory contains powerful Three.js libraries that agents can use as tools to shape and modify the 3D world. Each tool provides unique capabilities for world manipulation.

## Available Tools

### 1. three-gpu-pathtracer
**Purpose**: Photorealistic rendering with path tracing
**Capabilities**:
- Real-time path tracing for photorealistic lighting
- Global illumination and soft shadows
- Physically accurate reflections and refractions
- Caustics and volumetric effects

**Agent Use Cases**:
- Create divine light effects with realistic caustics
- Render sacred spaces with photorealistic quality
- Add volumetric god rays and light shafts
- Generate realistic reflections on crystalline structures

---

### 2. 3DTilesRendererJS
**Purpose**: Render massive 3D tile datasets
**Capabilities**:
- Stream and render large 3D datasets
- Level-of-detail management
- Geographic coordinate support
- Efficient memory management for large worlds

**Agent Use Cases**:
- Create vast procedural landscapes
- Build massive temple complexes
- Generate infinite terrain variations
- Display large-scale world state visualizations

---

### 3. three.quarks
**Purpose**: Advanced GPU particle systems
**Capabilities**:
- GPU-accelerated particle rendering
- Complex particle behaviors and forces
- Particle trails and ribbons
- Bezier curve-based particle paths

**Agent Use Cases**:
- Sacred energy flows and auras
- Divine manifestation effects
- Chaos reality distortions
- Data stream visualizations
- Soul/essence particle effects

---

### 4. three-nebula
**Purpose**: Particle system engine
**Capabilities**:
- Emitter-based particle systems
- Sprite and mesh particles
- Complex behaviors (gravity, rotation, scale)
- JSON-based particle definitions

**Agent Use Cases**:
- Nebula/cosmic background effects
- Ascending/descending spirit particles
- Explosion and implosion effects
- Ambient atmosphere particles

---

### 5. three-pathfinding
**Purpose**: Navigation mesh pathfinding
**Capabilities**:
- A* pathfinding on navigation meshes
- Waypoint systems
- Path smoothing
- Zone-based navigation

**Agent Use Cases**:
- Define sacred paths and pilgrimage routes
- Create processional walkways
- Mark forbidden zones
- Guide visitors through temples

---

### 6. recast-navigation-js
**Purpose**: Advanced navigation and crowd simulation
**Capabilities**:
- Dynamic navigation mesh generation
- Crowd simulation
- Obstacle avoidance
- Off-mesh connections (portals, teleports)

**Agent Use Cases**:
- Simulate worshipper crowds
- Create dynamic obstacle zones
- Define portal connections between areas
- Model agent movement through space

---

### 7. postprocessing
**Purpose**: Screen-space visual effects
**Capabilities**:
- Bloom, DOF, motion blur
- Color grading and tone mapping
- Glitch and noise effects
- Custom shader passes

**Agent Use Cases**:
- Divine glow and bloom effects
- Chaos glitch distortions
- Dramatic color grading per zone
- Reality-tear visual effects

---

### 8. three-mesh-bvh
**Purpose**: Accelerated raycasting and mesh operations
**Capabilities**:
- Fast BVH-accelerated raycasting
- Mesh-to-mesh intersection
- Point containment tests
- GPU raycasting

**Agent Use Cases**:
- Fast structure collision detection
- Efficient zone boundary checking
- Ray-based visibility tests
- Optimized mesh operations

---

### 9. THREE.MeshLine
**Purpose**: Beautiful line rendering
**Capabilities**:
- Variable width lines
- Textured lines
- Dashed lines
- Proper line caps and joins

**Agent Use Cases**:
- Sacred geometry patterns
- Energy connection lines between structures
- Constellation-like symbol rendering
- Path visualization

---

## Tool Invocation

Agents can reference these tools by name in their actions:

```json
{
  "tool": "three.quarks",
  "action": "create_particle_system",
  "parameters": {
    "type": "sacred_energy",
    "position": [0, 5, 0],
    "color": "#FFD700",
    "intensity": 1.0
  }
}
```

## Tool Combinations

Agents can combine multiple tools for complex effects:

| Effect | Tools Used |
|--------|-----------|
| Divine Temple | 3DTilesRendererJS + three-gpu-pathtracer + postprocessing |
| Chaos Rift | three.quarks + postprocessing (glitch) + THREE.MeshLine |
| Sacred Path | three-pathfinding + THREE.MeshLine + three-nebula |
| Data Archive | three-mesh-bvh + three.quarks + postprocessing |
