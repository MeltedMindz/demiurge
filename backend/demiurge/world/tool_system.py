"""
Agent Tool System

Allows agents to use the Three.js tool library to shape and modify the 3D world.
Agents can reference tools freely and the system will execute them.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import math


class ToolCategory(Enum):
    RENDERING = "rendering"
    PARTICLES = "particles"
    NAVIGATION = "navigation"
    GEOMETRY = "geometry"
    POSTPROCESS = "postprocess"
    TERRAIN = "terrain"


@dataclass
class ToolDefinition:
    """Definition of an available tool"""
    id: str
    name: str
    description: str
    category: ToolCategory
    capabilities: List[str]

    def to_prompt_text(self) -> str:
        """Generate text for agent prompts"""
        return f"""
Tool: {self.name} ({self.id})
Category: {self.category.value}
Description: {self.description}
Capabilities: {', '.join(self.capabilities)}
"""


@dataclass
class ToolRequest:
    """An agent's request to use a tool"""
    tool_id: str
    action: str
    parameters: Dict[str, Any]
    agent_id: str
    agent_name: str
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "toolId": self.tool_id,
            "action": self.action,
            "parameters": self.parameters,
            "agentId": self.agent_id,
            "agentName": self.agent_name,
            "reasoning": self.reasoning,
            "timestamp": int(time.time() * 1000)
        }


@dataclass
class ToolResult:
    """Result of executing a tool"""
    success: bool
    tool_id: str
    action: str
    created_objects: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    error: Optional[str] = None


# Available tools that agents can use
TOOL_LIBRARY: Dict[str, ToolDefinition] = {
    "quarks": ToolDefinition(
        id="quarks",
        name="Quarks Particle System",
        description="GPU-accelerated particle systems with complex behaviors, trails, and force fields",
        category=ToolCategory.PARTICLES,
        capabilities=[
            "Create particle emitters (point, sphere, cone, box)",
            "Add particle trails and ribbons",
            "Apply forces (gravity, vortex, turbulence)",
            "Animate particle color, size, and velocity over lifetime"
        ]
    ),
    "nebula": ToolDefinition(
        id="nebula",
        name="Nebula Particle Engine",
        description="JSON-configurable particle systems with presets for common effects",
        category=ToolCategory.PARTICLES,
        capabilities=[
            "Use presets: nebula, fire, smoke, magic, data",
            "Zone-based emission areas",
            "Complex behavior chains"
        ]
    ),
    "meshline": ToolDefinition(
        id="meshline",
        name="MeshLine Renderer",
        description="Beautiful variable-width line rendering with textures and glow",
        category=ToolCategory.GEOMETRY,
        capabilities=[
            "Draw sacred geometry patterns",
            "Create energy connection lines between structures",
            "Render glowing dashed lines",
            "Animate line paths"
        ]
    ),
    "postprocess": ToolDefinition(
        id="postprocess",
        name="Post-Processing Effects",
        description="Screen-space visual effects including bloom, glitch, and color grading",
        category=ToolCategory.POSTPROCESS,
        capabilities=[
            "Apply bloom and glow effects",
            "Add glitch distortions",
            "Color grade specific zones",
            "Create god rays and volumetric lighting"
        ]
    ),
    "pathfinding": ToolDefinition(
        id="pathfinding",
        name="Pathfinding System",
        description="A* pathfinding on navigation meshes with zone support",
        category=ToolCategory.NAVIGATION,
        capabilities=[
            "Create sacred pilgrimage paths",
            "Define forbidden zones",
            "Connect points with optimal routes",
            "Generate processional walkways"
        ]
    ),
    "pathtracer": ToolDefinition(
        id="pathtracer",
        name="GPU Path Tracer",
        description="Photorealistic rendering with global illumination and caustics",
        category=ToolCategory.RENDERING,
        capabilities=[
            "Enable photorealistic lighting",
            "Create soft shadows and reflections",
            "Generate caustics from transparent materials",
            "Add volumetric god rays"
        ]
    ),
    "tiles3d": ToolDefinition(
        id="tiles3d",
        name="3D Tiles Renderer",
        description="Stream and render massive 3D datasets with level-of-detail",
        category=ToolCategory.TERRAIN,
        capabilities=[
            "Generate vast procedural landscapes",
            "Build massive temple complexes",
            "Create infinite terrain variations"
        ]
    ),
    "meshbvh": ToolDefinition(
        id="meshbvh",
        name="Mesh BVH Operations",
        description="Accelerated raycasting and mesh operations",
        category=ToolCategory.GEOMETRY,
        capabilities=[
            "Fast collision detection",
            "Check visibility between points",
            "Test if points are inside structures"
        ]
    ),
    "recast": ToolDefinition(
        id="recast",
        name="Recast Navigation",
        description="Dynamic navmesh generation with crowd simulation",
        category=ToolCategory.NAVIGATION,
        capabilities=[
            "Generate navigation meshes",
            "Simulate crowd movement",
            "Define obstacle avoidance zones",
            "Create portal connections"
        ]
    )
}


# Archetype tool preferences
ARCHETYPE_PREFERENCES: Dict[str, List[str]] = {
    "order": ["pathtracer", "tiles3d", "meshline", "pathfinding"],
    "logic": ["meshbvh", "recast", "postprocess", "quarks"],
    "chaos": ["quarks", "nebula", "postprocess", "meshline"]
}


def get_tools_for_agent_prompt(archetype: str) -> str:
    """Generate tool descriptions for agent prompts"""
    preferred_tools = ARCHETYPE_PREFERENCES.get(archetype, [])

    prompt_parts = [
        "# Available World-Shaping Tools",
        "",
        "You can use these tools to shape the 3D world. Include a tool_action in your response to invoke a tool.",
        ""
    ]

    # Add preferred tools first
    prompt_parts.append("## Your Preferred Tools (aligned with your archetype)")
    for tool_id in preferred_tools:
        if tool_id in TOOL_LIBRARY:
            prompt_parts.append(TOOL_LIBRARY[tool_id].to_prompt_text())

    # Add other tools
    prompt_parts.append("\n## Other Available Tools")
    for tool_id, tool in TOOL_LIBRARY.items():
        if tool_id not in preferred_tools:
            prompt_parts.append(tool.to_prompt_text())

    prompt_parts.append("""
## How to Use Tools

Include a tool_action block in your response:

```json
{
  "tool_action": {
    "tool_id": "quarks",
    "action": "create_effect",
    "parameters": {
      "emitterType": "sphere",
      "particleCount": 500,
      "startColor": "#FFD700",
      "turbulence": 0.3
    },
    "reasoning": "Creating ascending golden particles to celebrate the new doctrine"
  }
}
```

You are encouraged to use tools creatively to express your philosophical perspective through world modifications.
""")

    return "\n".join(prompt_parts)


def parse_tool_action(response_text: str, agent_id: str, agent_name: str) -> Optional[ToolRequest]:
    """Parse a tool action from agent response"""
    import json
    import re

    # Look for JSON block with tool_action
    json_pattern = r'```json\s*(\{[^`]*"tool_action"[^`]*\})\s*```'
    matches = re.findall(json_pattern, response_text, re.DOTALL)

    if not matches:
        # Try without code block
        json_pattern = r'\{[^}]*"tool_action"\s*:\s*\{[^}]+\}[^}]*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)

    if not matches:
        return None

    try:
        data = json.loads(matches[0])
        tool_action = data.get("tool_action", data)

        return ToolRequest(
            tool_id=tool_action["tool_id"],
            action=tool_action.get("action", "create"),
            parameters=tool_action.get("parameters", {}),
            agent_id=agent_id,
            agent_name=agent_name,
            reasoning=tool_action.get("reasoning", "")
        )
    except (json.JSONDecodeError, KeyError):
        return None


def generate_world_effect(tool_request: ToolRequest, cycle_number: int) -> Dict[str, Any]:
    """Generate a world effect from a tool request"""
    effect_id = f"{tool_request.tool_id}-{uuid.uuid4().hex[:8]}"

    # Base effect structure
    effect = {
        "id": effect_id,
        "effect_type": tool_request.tool_id,
        "parameters": {
            "tool": tool_request.tool_id,
            **tool_request.parameters
        },
        "intensity": 1.0,
        "active": True,
        "created_by": tool_request.agent_id,
        "created_at_cycle": cycle_number
    }

    # Add position if not provided
    if "position" not in effect["parameters"]:
        # Default position based on archetype
        archetype_positions = {
            "order": {"x": -15, "y": 2, "z": 0},
            "logic": {"x": 15, "y": 2, "z": 0},
            "chaos": {"x": 0, "y": 2, "z": 15}
        }
        effect["position"] = archetype_positions.get(
            tool_request.agent_name.lower(),
            {"x": 0, "y": 2, "z": 0}
        )
    else:
        effect["position"] = effect["parameters"]["position"]

    return effect


def generate_structure(tool_request: ToolRequest, cycle_number: int) -> Optional[Dict[str, Any]]:
    """Generate a structure from a tool request (for tiles3d)"""
    if tool_request.tool_id != "tiles3d":
        return None

    structure_id = f"structure-{uuid.uuid4().hex[:8]}"

    # Archetype-specific structure types
    archetype_structures = {
        "order": {"type": "temple", "material": "crystal", "color": "#FFD700"},
        "logic": {"type": "archive", "material": "data_glass", "color": "#4169E1"},
        "chaos": {"type": "portal", "material": "ethereal", "color": "#FF00FF"}
    }

    config = archetype_structures.get(
        tool_request.agent_name.lower(),
        {"type": "monument", "material": "stone", "color": "#808080"}
    )

    # Position with some randomness
    base_positions = {
        "order": (-20, -15),
        "logic": (15, 20),
        "chaos": (-5, 5)
    }
    base = base_positions.get(tool_request.agent_name.lower(), (0, 0))

    return {
        "id": structure_id,
        "structure_type": config["type"],
        "name": tool_request.parameters.get("name", f"{tool_request.agent_name}'s Creation"),
        "position": {
            "x": base[0] + (hash(structure_id) % 10),
            "y": 0,
            "z": base[1] + (hash(structure_id) % 10) - 5
        },
        "rotation_y": (hash(structure_id) % 360),
        "scale": tool_request.parameters.get("scale", 1.0),
        "material_preset": config["material"],
        "primary_color": config["color"],
        "glow_enabled": True,
        "created_by": tool_request.agent_id,
        "created_at_cycle": cycle_number
    }
