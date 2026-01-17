"""
SQLAlchemy Database Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, Text, ForeignKey,
    DateTime, JSON, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base


# ============== Agent Models ==============

class Agent(Base):
    """Agent identity and state"""
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    archetype: Mapped[str] = mapped_column(String(50), nullable=False)  # 'order', 'logic', 'chaos'

    # 3D World State
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    position_z: Mapped[float] = mapped_column(Float, default=0.0)
    rotation_y: Mapped[float] = mapped_column(Float, default=0.0)
    current_animation: Mapped[str] = mapped_column(String(50), default="idle")

    # Visual appearance
    avatar_model_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(7), default="#FFFFFF")
    secondary_color: Mapped[str] = mapped_column(String(7), default="#000000")
    glow_intensity: Mapped[float] = mapped_column(Float, default=1.0)

    # Stats
    influence_score: Mapped[int] = mapped_column(Integer, default=100)
    proposals_made: Mapped[int] = mapped_column(Integer, default=0)
    proposals_accepted: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    personality = relationship("AgentPersonality", back_populates="agent", uselist=False)
    beliefs = relationship("AgentBelief", back_populates="agent")
    journals = relationship("AgentJournal", back_populates="agent")


class AgentPersonality(Base):
    """Dynamic personality traits"""
    __tablename__ = "agent_personality"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    agent_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"))

    traits: Mapped[Dict] = mapped_column(JSON, nullable=False)  # {"certainty": 0.9, "order": 0.8, ...}
    trait_history: Mapped[List] = mapped_column(JSON, default=list)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent = relationship("Agent", back_populates="personality")


class AgentBelief(Base):
    """Individual agent belief"""
    __tablename__ = "agent_beliefs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    agent_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"))

    content: Mapped[str] = mapped_column(Text, nullable=False)
    belief_type: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    importance: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    times_challenged: Mapped[int] = mapped_column(Integer, default=0)
    times_defended: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_reinforced: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="beliefs")

    __table_args__ = (
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_confidence_range'),
        CheckConstraint('importance >= 0 AND importance <= 1', name='check_importance_range'),
    )


class AgentRelationship(Base):
    """Relationship between agents"""
    __tablename__ = "agent_relationships"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    agent_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"))
    target_agent_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"))

    trust_score: Mapped[float] = mapped_column(Float, default=0.0)
    agreement_rate: Mapped[float] = mapped_column(Float, default=0.5)
    total_interactions: Mapped[int] = mapped_column(Integer, default=0)
    successful_alliances: Mapped[int] = mapped_column(Integer, default=0)
    conflicts: Mapped[int] = mapped_column(Integer, default=0)
    shared_beliefs: Mapped[List] = mapped_column(JSON, default=list)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('agent_id', 'target_agent_id', name='unique_relationship'),
        CheckConstraint('trust_score >= -1 AND trust_score <= 1', name='check_trust_range'),
    )


class AgentJournal(Base):
    """Agent private journal entries"""
    __tablename__ = "agent_journals"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    agent_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"))
    cycle_number: Mapped[int] = mapped_column(Integer, nullable=False)

    entry: Mapped[str] = mapped_column(Text, nullable=False)
    mood: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    make_visible: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="journals")

    __table_args__ = (
        UniqueConstraint('agent_id', 'cycle_number', name='unique_journal_per_cycle'),
    )


# ============== Debate Models ==============

class Debate(Base):
    """Debate history"""
    __tablename__ = "debates"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    cycle_number: Mapped[int] = mapped_column(Integer, nullable=False)

    proposer_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"))
    proposal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    proposal_content: Mapped[str] = mapped_column(Text, nullable=False)

    challenges: Mapped[List] = mapped_column(JSON, default=list)
    votes: Mapped[Dict] = mapped_column(JSON, nullable=False)

    outcome: Mapped[str] = mapped_column(String(20), nullable=False)
    final_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    world_changes: Mapped[List] = mapped_column(JSON, default=list)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_debates_cycle', 'cycle_number'),
    )


class Doctrine(Base):
    """Accepted doctrines"""
    __tablename__ = "doctrines"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    doctrine_type: Mapped[str] = mapped_column(String(50), nullable=False)

    proposed_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=True)
    accepted_at_cycle: Mapped[int] = mapped_column(Integer, nullable=False)

    structure_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("world_structures.id"), nullable=True)
    visual_effect: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    importance_level: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ============== World Models ==============

class WorldStructure(Base):
    """3D World structures"""
    __tablename__ = "world_structures"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    structure_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 3D Transform
    position_x: Mapped[float] = mapped_column(Float, nullable=False)
    position_y: Mapped[float] = mapped_column(Float, nullable=False)
    position_z: Mapped[float] = mapped_column(Float, nullable=False)
    rotation_y: Mapped[float] = mapped_column(Float, default=0.0)
    scale: Mapped[float] = mapped_column(Float, default=1.0)

    # Appearance
    model_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    material_preset: Mapped[str] = mapped_column(String(50), default="stone")
    primary_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    glow_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadata
    created_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=True)
    created_at_cycle: Mapped[int] = mapped_column(Integer, nullable=False)
    associated_doctrine: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), nullable=True)

    # State
    integrity: Mapped[float] = mapped_column(Float, default=1.0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_structures_position', 'position_x', 'position_z'),
    )


class TerrainModification(Base):
    """Terrain modifications"""
    __tablename__ = "terrain_modifications"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    modification_type: Mapped[str] = mapped_column(String(50), nullable=False)

    center_x: Mapped[float] = mapped_column(Float, nullable=False)
    center_z: Mapped[float] = mapped_column(Float, nullable=False)
    radius: Mapped[float] = mapped_column(Float, nullable=False)

    parameters: Mapped[Dict] = mapped_column(JSON, nullable=False)

    caused_by_doctrine: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("doctrines.id"), nullable=True)
    created_at_cycle: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WorldEffect(Base):
    """Visual effects in the world"""
    __tablename__ = "world_effects"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    effect_type: Mapped[str] = mapped_column(String(50), nullable=False)

    position_x: Mapped[float] = mapped_column(Float, nullable=False)
    position_y: Mapped[float] = mapped_column(Float, nullable=False)
    position_z: Mapped[float] = mapped_column(Float, nullable=False)

    parameters: Mapped[Dict] = mapped_column(JSON, nullable=False)

    associated_with: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), nullable=True)
    association_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    intensity: Mapped[float] = mapped_column(Float, default=1.0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_effects_active', 'active'),
    )


class WorldWeather(Base):
    """Weather state"""
    __tablename__ = "world_weather"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    weather_type: Mapped[str] = mapped_column(String(50), nullable=False)
    intensity: Mapped[float] = mapped_column(Float, default=0.5)
    parameters: Mapped[Dict] = mapped_column(JSON, default=dict)

    triggered_by_doctrine: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("doctrines.id"), nullable=True)
    started_at_cycle: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_cycles: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ============== Cultural Models ==============

class SacredTerm(Base):
    """Sacred vocabulary"""
    __tablename__ = "sacred_terms"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    term: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    etymology: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    proposed_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=True)
    adopted_at_cycle: Mapped[int] = mapped_column(Integer, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    symbol_glyph: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    effect_when_spoken: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prophecy(Base):
    """Prophecies"""
    __tablename__ = "prophecies"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    prophet_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"))
    prediction: Mapped[str] = mapped_column(Text, nullable=False)

    target_cycle: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at_cycle: Mapped[int] = mapped_column(Integer, nullable=False)

    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    fulfillment_status: Mapped[str] = mapped_column(String(20), default="pending")
    fulfilled_at_cycle: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    fulfillment_effect: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SacredImage(Base):
    """Generated sacred images"""
    __tablename__ = "sacred_images"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    sacred_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)

    displayed_in_structure: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("world_structures.id"), nullable=True)
    position_in_structure: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    generated_at_cycle: Mapped[int] = mapped_column(Integer, nullable=False)
    generated_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=True)
    associated_doctrine: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("doctrines.id"), nullable=True)

    metadata: Mapped[Dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CycleSnapshot(Base):
    """Full cycle state for replay"""
    __tablename__ = "cycle_snapshots"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    cycle_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    agent_states: Mapped[Dict] = mapped_column(JSON, nullable=False)
    world_structures: Mapped[List] = mapped_column(JSON, nullable=False)
    active_effects: Mapped[List] = mapped_column(JSON, nullable=False)
    weather_state: Mapped[Dict] = mapped_column(JSON, nullable=False)

    debate_summary: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
