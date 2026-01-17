"""
Pydantic Schemas for World State
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

from .agent_schemas import AgentResponse, Position3D


class StructureCreate(BaseModel):
    """Schema for creating a structure"""
    structure_type: str  # 'temple', 'monument', 'altar', 'obelisk', 'library'
    name: Optional[str] = None
    position: Position3D
    rotation_y: float = 0.0
    scale: float = 1.0
    model_path: Optional[str] = None
    material_preset: str = "stone"  # 'crystal', 'stone', 'ethereal', 'glitch'
    primary_color: Optional[str] = None
    glow_enabled: bool = False
    created_by: Optional[str] = None  # Agent ID
    associated_doctrine_id: Optional[str] = None


class StructureResponse(BaseModel):
    """Structure in the world"""
    id: str
    structure_type: str
    name: Optional[str] = None

    # Transform
    position: Position3D
    rotation_y: float = 0.0
    scale: float = 1.0

    # Appearance
    model_path: Optional[str] = None
    material_preset: str = "stone"
    primary_color: Optional[str] = None
    glow_enabled: bool = False

    # Metadata
    created_by: Optional[str] = None
    created_at_cycle: int
    associated_doctrine_id: Optional[str] = None
    integrity: float = 1.0
    active: bool = True

    created_at: datetime

    class Config:
        from_attributes = True


class TerrainModification(BaseModel):
    """Terrain modification zone"""
    id: str
    modification_type: str  # 'elevation', 'texture', 'effect_zone'
    center_x: float
    center_z: float
    radius: float
    parameters: Dict[str, Any]  # Type-specific params
    caused_by_doctrine_id: Optional[str] = None
    created_at_cycle: int
    active: bool = True


class WorldEffect(BaseModel):
    """Visual effect in the world"""
    id: str
    effect_type: str  # 'floating_symbol', 'light_beam', 'particle_field'
    position: Position3D
    parameters: Dict[str, Any]
    associated_with: Optional[str] = None
    association_type: Optional[str] = None
    intensity: float = 1.0
    active: bool = True


class WeatherResponse(BaseModel):
    """Current weather state"""
    type: str  # 'clear', 'mystical_fog', 'divine_light', 'chaos_storm'
    intensity: float = Field(ge=0.0, le=1.0, default=0.5)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    triggered_by_doctrine_id: Optional[str] = None
    started_at_cycle: Optional[int] = None


class WorldStateResponse(BaseModel):
    """Complete world state snapshot"""
    cycle_number: int
    agents: List[AgentResponse]
    structures: List[StructureResponse]
    terrain_modifications: List[TerrainModification] = Field(default_factory=list)
    effects: List[WorldEffect]
    weather: WeatherResponse


class CycleSnapshot(BaseModel):
    """Full cycle state for replay"""
    id: str
    cycle_number: int
    agent_states: Dict[str, Any]
    structures: List[StructureResponse]
    effects: List[WorldEffect]
    weather: WeatherResponse
    debate_summary: Optional[Dict[str, Any]] = None
    created_at: datetime


# ============== Structure Templates ==============

STRUCTURE_TEMPLATES = {
    "belief": {
        "types": ["floating_symbol", "light_beam"],
        "material": "ethereal"
    },
    "ritual": {
        "types": ["altar", "ceremonial_circle"],
        "material": "stone"
    },
    "deity": {
        "types": ["temple", "shrine"],
        "material": "crystal"
    },
    "commandment": {
        "types": ["obelisk", "tablet"],
        "material": "stone"
    },
    "myth": {
        "types": ["terrain_feature"],
        "material": "natural"
    },
    "sacred_text": {
        "types": ["library", "archive"],
        "material": "crystal"
    }
}


# ============== Weather Effects ==============

WEATHER_TYPES = {
    "clear": {
        "description": "Clear skies, gentle ambient light",
        "fog_density": 0.0,
        "light_intensity": 1.0
    },
    "mystical_fog": {
        "description": "Ethereal fog rolling through the world",
        "fog_density": 0.5,
        "fog_color": "#9966CC"
    },
    "divine_light": {
        "description": "Golden rays streaming from above",
        "light_intensity": 1.5,
        "light_color": "#FFD700"
    },
    "chaos_storm": {
        "description": "Reality-warping glitch effects",
        "glitch_intensity": 0.7,
        "color_shift": True
    },
    "order_symmetry": {
        "description": "Perfectly symmetrical cloud formations",
        "cloud_pattern": "symmetric"
    }
}
