"""
World State Management
Manages the 3D world state, structures, effects, and weather
"""
import math
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import uuid4
from dataclasses import dataclass, field
import logging

logger = logging.getLogger("demiurge.world")


@dataclass
class Position3D:
    """3D position"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Structure:
    """A structure in the world"""
    id: str
    structure_type: str
    name: Optional[str]
    position: Position3D
    rotation_y: float = 0.0
    scale: float = 1.0
    model_path: Optional[str] = None
    material_preset: str = "stone"
    primary_color: Optional[str] = None
    glow_enabled: bool = False
    created_by: Optional[str] = None
    created_at_cycle: int = 0
    associated_doctrine_id: Optional[str] = None
    integrity: float = 1.0
    active: bool = True

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "structure_type": self.structure_type,
            "name": self.name,
            "position": {"x": self.position.x, "y": self.position.y, "z": self.position.z},
            "rotation_y": self.rotation_y,
            "scale": self.scale,
            "model_path": self.model_path,
            "material_preset": self.material_preset,
            "primary_color": self.primary_color,
            "glow_enabled": self.glow_enabled,
            "created_by": self.created_by,
            "created_at_cycle": self.created_at_cycle,
            "associated_doctrine_id": self.associated_doctrine_id,
            "integrity": self.integrity,
            "active": self.active
        }


@dataclass
class WorldEffect:
    """A visual effect in the world"""
    id: str
    effect_type: str
    position: Position3D
    parameters: Dict = field(default_factory=dict)
    associated_with: Optional[str] = None
    association_type: Optional[str] = None
    intensity: float = 1.0
    active: bool = True

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "effect_type": self.effect_type,
            "position": {"x": self.position.x, "y": self.position.y, "z": self.position.z},
            "parameters": self.parameters,
            "associated_with": self.associated_with,
            "association_type": self.association_type,
            "intensity": self.intensity,
            "active": self.active
        }


@dataclass
class WeatherState:
    """Current weather state"""
    weather_type: str = "clear"
    intensity: float = 0.5
    parameters: Dict = field(default_factory=dict)
    triggered_by_doctrine_id: Optional[str] = None
    started_at_cycle: int = 0

    def to_dict(self) -> Dict:
        return {
            "type": self.weather_type,
            "intensity": self.intensity,
            "parameters": self.parameters,
            "triggered_by_doctrine_id": self.triggered_by_doctrine_id,
            "started_at_cycle": self.started_at_cycle
        }


class WorldState:
    """
    Manages the complete 3D world state.

    Features:
    - Structure spawning and placement
    - Terrain modification tracking
    - Weather system
    - Effect management
    - Spatial queries
    """

    # World boundaries
    WORLD_SIZE = 100.0  # -50 to +50
    MIN_STRUCTURE_DISTANCE = 5.0

    # Structure templates
    STRUCTURE_TEMPLATES = {
        "temple": {"model": "temple.glb", "scale": 2.0, "glow": True},
        "altar": {"model": "altar.glb", "scale": 1.0, "glow": True},
        "obelisk": {"model": "obelisk.glb", "scale": 1.5, "glow": True},
        "monument": {"model": "monument.glb", "scale": 1.2, "glow": False},
        "library": {"model": "library.glb", "scale": 1.8, "glow": False},
        "floating_symbol": {"model": "symbol.glb", "scale": 0.5, "glow": True},
        "rift": {"model": "rift.glb", "scale": 1.0, "glow": True}
    }

    # Agent domain zones
    AGENT_DOMAINS = {
        "Axioma": {"center": (-25, 0), "radius": 20, "style": "geometric"},
        "Veridicus": {"center": (25, 0), "radius": 20, "style": "analytical"},
        "Paradoxia": {"center": (0, 25), "radius": 20, "style": "chaotic"}
    }

    def __init__(self):
        self.structures: List[Structure] = []
        self.effects: List[WorldEffect] = []
        self.weather = WeatherState()
        self.terrain_modifications: List[Dict] = []

        # Spatial index for quick lookups
        self._structure_grid: Dict[Tuple[int, int], List[str]] = {}

    def spawn_structure(
        self,
        structure_type: str,
        doctrine_content: str,
        proposer: str,
        cycle_number: int,
        doctrine_id: str,
        color: Optional[str] = None
    ) -> Structure:
        """Spawn a new structure based on a doctrine"""

        # Find suitable position
        position = self._find_spawn_position(proposer)

        # Get template
        template = self.STRUCTURE_TEMPLATES.get(structure_type, {})

        # Generate name from doctrine
        name = self._generate_structure_name(structure_type, doctrine_content, cycle_number)

        # Create structure
        structure = Structure(
            id=str(uuid4()),
            structure_type=structure_type,
            name=name,
            position=position,
            rotation_y=random.uniform(0, 360),
            scale=template.get("scale", 1.0),
            model_path=f"models/{template.get('model', 'default.glb')}",
            material_preset=self._get_material_for_proposer(proposer),
            primary_color=color,
            glow_enabled=template.get("glow", False),
            created_by=proposer,
            created_at_cycle=cycle_number,
            associated_doctrine_id=doctrine_id
        )

        self.structures.append(structure)
        self._add_to_grid(structure)

        # Maybe spawn associated effects
        if structure.glow_enabled:
            self._spawn_structure_effects(structure)

        logger.info(f"Spawned {structure_type} at ({position.x:.1f}, {position.z:.1f})")
        return structure

    def _find_spawn_position(self, proposer: str) -> Position3D:
        """Find a valid position for a new structure"""

        # Prefer spawning in proposer's domain
        domain = self.AGENT_DOMAINS.get(proposer, {})
        center = domain.get("center", (0, 0))
        radius = domain.get("radius", 30)

        for _ in range(50):  # Max attempts
            # Random position within domain
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(5, radius)

            x = center[0] + math.cos(angle) * dist
            z = center[1] + math.sin(angle) * dist

            # Clamp to world bounds
            x = max(-self.WORLD_SIZE/2 + 5, min(self.WORLD_SIZE/2 - 5, x))
            z = max(-self.WORLD_SIZE/2 + 5, min(self.WORLD_SIZE/2 - 5, z))

            # Check for collisions
            if self._is_position_valid(x, z):
                return Position3D(x, 0, z)

        # Fallback: spiral outward from center
        return self._spiral_position(len(self.structures))

    def _spiral_position(self, index: int) -> Position3D:
        """Generate position using golden ratio spiral"""
        golden_ratio = 1.618033988749895
        angle = index * 2 * math.pi / (golden_ratio * golden_ratio)
        radius = 10 + math.sqrt(index) * 5

        x = math.cos(angle) * radius
        z = math.sin(angle) * radius

        return Position3D(x, 0, z)

    def _is_position_valid(self, x: float, z: float) -> bool:
        """Check if position is valid (not too close to other structures)"""
        for structure in self.structures:
            if not structure.active:
                continue

            dx = structure.position.x - x
            dz = structure.position.z - z
            dist = math.sqrt(dx*dx + dz*dz)

            if dist < self.MIN_STRUCTURE_DISTANCE:
                return False

        return True

    def _add_to_grid(self, structure: Structure):
        """Add structure to spatial grid"""
        grid_x = int(structure.position.x // 10)
        grid_z = int(structure.position.z // 10)
        key = (grid_x, grid_z)

        if key not in self._structure_grid:
            self._structure_grid[key] = []
        self._structure_grid[key].append(structure.id)

    def _generate_structure_name(
        self,
        structure_type: str,
        doctrine_content: str,
        cycle_number: int
    ) -> str:
        """Generate a meaningful name for a structure"""
        # Extract key words from doctrine
        words = doctrine_content.split()[:5]
        key_phrase = " ".join(words)

        type_names = {
            "temple": "Temple",
            "altar": "Altar",
            "obelisk": "Obelisk",
            "monument": "Monument",
            "library": "Archive",
            "floating_symbol": "Sign",
            "rift": "Schism"
        }

        base_name = type_names.get(structure_type, "Structure")
        return f"{base_name} of Cycle {cycle_number}"

    def _get_material_for_proposer(self, proposer: str) -> str:
        """Get material preset based on proposer"""
        materials = {
            "Axioma": "crystal",
            "Veridicus": "stone",
            "Paradoxia": "ethereal"
        }
        return materials.get(proposer, "stone")

    def _spawn_structure_effects(self, structure: Structure):
        """Spawn visual effects for a structure"""
        if structure.structure_type == "floating_symbol":
            # Light beam effect
            effect = WorldEffect(
                id=str(uuid4()),
                effect_type="light_beam",
                position=Position3D(
                    structure.position.x,
                    structure.position.y + 5,
                    structure.position.z
                ),
                parameters={
                    "color": structure.primary_color or "#FFFFFF",
                    "width": 0.5,
                    "height": 20
                },
                associated_with=structure.id,
                association_type="structure"
            )
            self.effects.append(effect)

        elif structure.structure_type == "temple":
            # Particle field
            effect = WorldEffect(
                id=str(uuid4()),
                effect_type="particle_field",
                position=structure.position,
                parameters={
                    "particle_count": 50,
                    "color": structure.primary_color or "#FFD700",
                    "radius": 5
                },
                associated_with=structure.id,
                association_type="structure"
            )
            self.effects.append(effect)

    def update_weather(
        self,
        weather_type: str,
        intensity: float = 0.5,
        parameters: Optional[Dict] = None,
        triggered_by: Optional[str] = None,
        cycle_number: int = 0
    ):
        """Update the weather state"""
        self.weather = WeatherState(
            weather_type=weather_type,
            intensity=intensity,
            parameters=parameters or {},
            triggered_by_doctrine_id=triggered_by,
            started_at_cycle=cycle_number
        )

        logger.info(f"Weather changed to {weather_type} at intensity {intensity}")

    def get_structures_in_radius(
        self,
        x: float,
        z: float,
        radius: float
    ) -> List[Structure]:
        """Get all structures within a radius"""
        result = []
        for structure in self.structures:
            if not structure.active:
                continue

            dx = structure.position.x - x
            dz = structure.position.z - z
            dist = math.sqrt(dx*dx + dz*dz)

            if dist <= radius:
                result.append(structure)

        return result

    def get_state(self) -> Dict:
        """Get full world state as dictionary"""
        return {
            "structures": [s.to_dict() for s in self.structures if s.active],
            "effects": [e.to_dict() for e in self.effects if e.active],
            "weather": self.weather.to_dict(),
            "terrain_modifications": self.terrain_modifications,
            "structure_count": len([s for s in self.structures if s.active]),
            "effect_count": len([e for e in self.effects if e.active])
        }

    def create_snapshot(self, cycle_number: int) -> Dict:
        """Create a full state snapshot for replay"""
        return {
            "cycle_number": cycle_number,
            "world_state": self.get_state(),
            "timestamp": datetime.utcnow().isoformat()
        }
