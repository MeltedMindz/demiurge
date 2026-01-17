"""
Pydantic Schemas for Debates
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field


class ProposalType(str, Enum):
    """Types of theological proposals"""
    BELIEF = "belief"
    RITUAL = "ritual"
    DEITY = "deity"
    COMMANDMENT = "commandment"
    MYTH = "myth"
    SACRED_TEXT = "sacred_text"
    HIERARCHY = "hierarchy"
    SCHISM = "schism"


class VoteType(str, Enum):
    """Vote options"""
    ACCEPT = "accept"
    REJECT = "reject"
    MUTATE = "mutate"
    DELAY = "delay"


class DebatePhase(str, Enum):
    """Phases of a debate cycle"""
    IDLE = "idle"
    PROPOSAL = "proposal"
    CHALLENGE = "challenge"
    VOTING = "voting"
    RESULT = "result"
    WORLD_UPDATE = "world_update"


class ProposalCreate(BaseModel):
    """Schema for creating a proposal"""
    type: ProposalType
    content: str
    details: Dict[str, Any] = Field(default_factory=dict)
    proposer_id: str


class ProposalResponse(BaseModel):
    """Proposal in a debate"""
    id: str
    type: ProposalType
    content: str
    details: Dict[str, Any]
    proposer_id: str
    proposer_name: str
    created_at: datetime


class ChallengeResponse(BaseModel):
    """Challenge to a proposal"""
    agent_id: str
    agent_name: str
    content: str
    challenge_type: str = "argument"  # 'argument', 'question', 'counter_proposal'
    timestamp: datetime


class VoteResponse(BaseModel):
    """Vote on a proposal"""
    agent_id: str
    agent_name: str
    vote: VoteType
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime


class DebateCreate(BaseModel):
    """Schema for starting a new debate"""
    cycle_number: int
    proposal: ProposalCreate


class DebateResponse(BaseModel):
    """Full debate record"""
    id: str
    cycle_number: int
    proposer_id: str
    proposer_name: str
    proposal_type: ProposalType
    proposal_content: str

    challenges: List[ChallengeResponse] = Field(default_factory=list)
    votes: Dict[str, VoteResponse] = Field(default_factory=dict)

    outcome: str  # 'accepted', 'rejected', 'mutated', 'delayed'
    final_content: Optional[str] = None

    world_changes: List[Dict[str, Any]] = Field(default_factory=list)

    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DebateStateResponse(BaseModel):
    """Current debate state for real-time updates"""
    cycle_number: int
    phase: DebatePhase
    phase_time_remaining: float  # seconds

    proposal: Optional[ProposalResponse] = None
    challenges: List[ChallengeResponse] = Field(default_factory=list)
    votes: Dict[str, VoteResponse] = Field(default_factory=dict)

    current_speaker: Optional[str] = None
    current_speech: Optional[str] = None


class DoctrineResponse(BaseModel):
    """Accepted doctrine"""
    id: str
    content: str
    doctrine_type: str
    proposed_by_id: Optional[str] = None
    proposed_by_name: Optional[str] = None
    accepted_at_cycle: int

    structure_id: Optional[str] = None
    visual_effect: Optional[str] = None

    importance_level: float = 0.5
    created_at: datetime

    class Config:
        from_attributes = True


class SacredTermResponse(BaseModel):
    """Sacred vocabulary term"""
    id: str
    term: str
    definition: Optional[str] = None
    etymology: Optional[str] = None
    proposed_by_name: Optional[str] = None
    adopted_at_cycle: int
    usage_count: int = 0
    symbol_glyph: Optional[str] = None


class ProphecyResponse(BaseModel):
    """Prophecy record"""
    id: str
    prophet_id: str
    prophet_name: str
    prediction: str
    target_cycle: Optional[int] = None
    created_at_cycle: int
    confidence: float = 0.5
    fulfillment_status: str = "pending"  # 'pending', 'fulfilled', 'failed'
    fulfilled_at_cycle: Optional[int] = None


# ============== Debate Outcome Rules ==============

VOTE_THRESHOLDS = {
    "accept": 2,  # Need 2/3 to accept
    "reject": 2,  # Need 2/3 to reject
    "mutate": 2,  # Need 2/3 to mutate
    "delay": 3,   # Need unanimous to delay
}


# ============== Proposal Templates ==============

PROPOSAL_TEMPLATES = {
    ProposalType.BELIEF: {
        "prompt_prefix": "A new belief that",
        "structure_type": "floating_symbol"
    },
    ProposalType.RITUAL: {
        "prompt_prefix": "A sacred ritual where",
        "structure_type": "altar"
    },
    ProposalType.DEITY: {
        "prompt_prefix": "A divine being named",
        "structure_type": "temple"
    },
    ProposalType.COMMANDMENT: {
        "prompt_prefix": "A sacred commandment stating",
        "structure_type": "obelisk"
    },
    ProposalType.MYTH: {
        "prompt_prefix": "An origin story about",
        "structure_type": "terrain_feature"
    },
    ProposalType.SACRED_TEXT: {
        "prompt_prefix": "A holy scripture describing",
        "structure_type": "library"
    }
}
