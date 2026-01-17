"""
Pydantic Schemas for Agents
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field


class Position3D(BaseModel):
    """3D position in world space"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class PersonalityTrait(BaseModel):
    """Dynamic personality trait"""
    name: str
    strength: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AgentBelief(BaseModel):
    """Individual agent belief"""
    id: Optional[UUID] = None
    content: str
    belief_type: str  # 'doctrine', 'ritual', 'principle'
    confidence: float = Field(ge=0.0, le=1.0)
    importance: float = Field(ge=0.0, le=1.0)
    source: Optional[str] = None
    times_challenged: int = 0
    times_defended: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_reinforced: datetime = Field(default_factory=datetime.utcnow)


class AgentRelationship(BaseModel):
    """Relationship between agents"""
    target_agent_id: UUID
    target_agent_name: str
    trust_score: float = Field(ge=-1.0, le=1.0, default=0.0)
    agreement_rate: float = Field(ge=0.0, le=1.0, default=0.5)
    total_interactions: int = 0
    successful_alliances: int = 0
    conflicts: int = 0
    shared_beliefs: List[str] = Field(default_factory=list)


class AgentStats(BaseModel):
    """Agent performance statistics"""
    proposals_made: int = 0
    proposals_accepted: int = 0
    challenges_made: int = 0
    challenges_successful: int = 0
    votes_cast: int = 0
    influence_score: int = 100


class AgentCreate(BaseModel):
    """Schema for creating a new agent"""
    name: str
    archetype: str  # 'order', 'logic', 'chaos'
    primary_color: str = "#FFFFFF"
    secondary_color: str = "#000000"
    avatar_model_path: Optional[str] = None


class AgentResponse(BaseModel):
    """Full agent response schema"""
    id: str
    name: str
    archetype: str

    # 3D State
    position: Position3D
    rotation_y: float = 0.0
    current_animation: str = "idle"

    # Visual
    primary_color: str
    secondary_color: str
    glow_intensity: float = 1.0
    avatar_model_path: Optional[str] = None

    # Stats
    influence_score: int = 100
    proposals_made: int = 0
    proposals_accepted: int = 0

    class Config:
        from_attributes = True


class AgentDetailResponse(AgentResponse):
    """Detailed agent response with beliefs and relationships"""
    traits: Dict[str, PersonalityTrait] = Field(default_factory=dict)
    beliefs: List[AgentBelief] = Field(default_factory=list)
    relationships: List[AgentRelationship] = Field(default_factory=list)
    stats: AgentStats = Field(default_factory=AgentStats)
    created_at: datetime
    updated_at: datetime


class AgentPositionUpdate(BaseModel):
    """Update for agent position (WebSocket)"""
    agent_id: str
    position: Position3D
    rotation_y: float
    animation: Optional[str] = None


class AgentSpeech(BaseModel):
    """Agent speech bubble content"""
    agent_id: str
    agent_name: str
    content: str
    speech_type: str = "normal"  # 'proposal', 'challenge', 'vote', 'normal'
    duration_ms: int = 5000


class JournalEntry(BaseModel):
    """Agent journal entry"""
    id: Optional[UUID] = None
    agent_id: UUID
    cycle_number: int
    entry: str
    mood: Optional[str] = None
    make_visible: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
