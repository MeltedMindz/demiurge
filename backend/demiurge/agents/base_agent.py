"""
Base Agent Class for Demiurge
Abstract foundation for all philosophical AI agents
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import random
import logging

from ..world.tool_system import get_tools_for_agent_prompt, parse_tool_action, ToolRequest
from ..memory.interactions import InteractionMemory, InteractionType, EmotionalState
from .autonomy import AgentAutonomy, AutonomousAction, DesireType

logger = logging.getLogger("demiurge.agents")


class ProposalType(str, Enum):
    """Types of proposals an agent can make"""
    BELIEF = "belief"
    RITUAL = "ritual"
    DEITY = "deity"
    COMMANDMENT = "commandment"
    MYTH = "myth"
    SACRED_TEXT = "sacred_text"
    HIERARCHY = "hierarchy"
    SCHISM = "schism"


class VoteType(str, Enum):
    """Voting options"""
    ACCEPT = "accept"
    REJECT = "reject"
    MUTATE = "mutate"
    DELAY = "delay"


@dataclass
class Proposal:
    """A theological proposal"""
    id: str
    type: ProposalType
    content: str
    author: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Challenge:
    """A challenge to a proposal"""
    agent_id: str
    agent_name: str
    content: str
    challenge_type: str = "argument"
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Vote:
    """A vote on a proposal"""
    agent_id: str
    agent_name: str
    vote: VoteType
    reasoning: str
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Position3D:
    """3D position in world space"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class BaseAgent(ABC):
    """
    Abstract base class for philosophical AI agents.

    Each agent has:
    - Distinct personality traits that influence behavior
    - Memory of past debates and outcomes
    - Relationships with other agents
    - Position and visual state in 3D world
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        archetype: str,
        primary_color: str = "#FFFFFF",
        secondary_color: str = "#000000"
    ):
        self.id = agent_id
        self.name = name
        self.archetype = archetype

        # Visual properties
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.glow_intensity = 1.0

        # 3D State
        self.position = Position3D()
        self.rotation_y = 0.0
        self.current_animation = "idle"

        # Personality traits (0.0 to 1.0)
        self.traits: Dict[str, float] = self._init_traits()

        # Memory
        self.beliefs: List[Dict] = []
        self.relationships: Dict[str, Dict] = {}
        self.debate_history: List[Dict] = []

        # Stats
        self.influence_score = 100
        self.proposals_made = 0
        self.proposals_accepted = 0

        # Interaction and Autonomy systems
        self.interaction_memory = InteractionMemory(agent_id, name)
        self.autonomy = AgentAutonomy(self)

        # Current emotional state
        self.emotional_state = EmotionalState.NEUTRAL

        logger.info(f"Initialized agent: {name} ({archetype})")

    @abstractmethod
    def _init_traits(self) -> Dict[str, float]:
        """Initialize personality traits specific to this agent type"""
        pass

    @abstractmethod
    def get_proposal_weights(self) -> Dict[ProposalType, float]:
        """Get weights for proposal type selection"""
        pass

    @abstractmethod
    async def generate_proposal_content(
        self,
        proposal_type: ProposalType,
        current_state: Dict,
        claude_client: Any
    ) -> str:
        """Generate the content for a proposal using Claude"""
        pass

    @abstractmethod
    async def generate_challenge(
        self,
        proposal: Proposal,
        current_state: Dict,
        claude_client: Any
    ) -> str:
        """Generate a challenge to a proposal"""
        pass

    @abstractmethod
    def evaluate_proposal(self, proposal: Proposal, challenges: List[Challenge]) -> Tuple[VoteType, str, float]:
        """
        Evaluate a proposal and return vote, reasoning, and confidence.
        This is the agent's internal logic, not Claude-generated.
        """
        pass

    # ============== Common Methods ==============

    def select_proposal_type(self) -> ProposalType:
        """Select a proposal type based on agent's weights"""
        weights = self.get_proposal_weights()
        types = list(weights.keys())
        probs = list(weights.values())
        total = sum(probs)
        probs = [p / total for p in probs]
        return random.choices(types, weights=probs, k=1)[0]

    async def create_proposal(
        self,
        current_state: Dict,
        claude_client: Any,
        cycle_number: int
    ) -> Proposal:
        """Create a new theological proposal"""
        proposal_type = self.select_proposal_type()
        content = await self.generate_proposal_content(
            proposal_type, current_state, claude_client
        )

        proposal = Proposal(
            id=f"proposal_{cycle_number}_{self.name}",
            type=proposal_type,
            content=content,
            author=self.name,
            details={
                "cycle": cycle_number,
                "proposer_archetype": self.archetype
            }
        )

        self.proposals_made += 1
        logger.info(f"{self.name} created proposal: {proposal_type.value}")

        return proposal

    async def challenge(
        self,
        proposal: Proposal,
        current_state: Dict,
        claude_client: Any
    ) -> Challenge:
        """Create a challenge to a proposal"""
        content = await self.generate_challenge(proposal, current_state, claude_client)

        return Challenge(
            agent_id=self.id,
            agent_name=self.name,
            content=content,
            challenge_type=self._determine_challenge_type(proposal)
        )

    def _determine_challenge_type(self, proposal: Proposal) -> str:
        """Determine what type of challenge to make"""
        # Override in subclasses for specific behavior
        return "argument"

    def vote(self, proposal: Proposal, challenges: List[Challenge]) -> Vote:
        """Cast a vote on a proposal"""
        vote_type, reasoning, confidence = self.evaluate_proposal(proposal, challenges)

        return Vote(
            agent_id=self.id,
            agent_name=self.name,
            vote=vote_type,
            reasoning=reasoning,
            confidence=confidence
        )

    def update_relationship(self, other_agent: str, interaction_type: str, outcome: bool):
        """Update relationship with another agent based on interaction"""
        if other_agent not in self.relationships:
            self.relationships[other_agent] = {
                "trust_score": 0.0,
                "agreement_rate": 0.5,
                "total_interactions": 0,
                "alliances": 0,
                "conflicts": 0
            }

        rel = self.relationships[other_agent]
        rel["total_interactions"] += 1

        if interaction_type == "vote_agreement":
            if outcome:
                rel["trust_score"] = min(1.0, rel["trust_score"] + 0.1)
                rel["alliances"] += 1
            else:
                rel["trust_score"] = max(-1.0, rel["trust_score"] - 0.05)
                rel["conflicts"] += 1

        # Update agreement rate
        total = rel["alliances"] + rel["conflicts"]
        if total > 0:
            rel["agreement_rate"] = rel["alliances"] / total

    def record_proposal_outcome(self, proposal: Proposal, accepted: bool):
        """Record the outcome of a proposal"""
        if accepted:
            self.proposals_accepted += 1
            self.influence_score += 10
        else:
            self.influence_score = max(0, self.influence_score - 5)

        self.debate_history.append({
            "cycle": proposal.details.get("cycle"),
            "proposal_type": proposal.type.value,
            "content_preview": proposal.content[:100],
            "accepted": accepted,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_trait(self, trait_name: str) -> float:
        """Get a personality trait value"""
        return self.traits.get(trait_name, 0.5)

    def modify_trait(self, trait_name: str, delta: float):
        """Modify a personality trait"""
        if trait_name in self.traits:
            self.traits[trait_name] = max(0.0, min(1.0, self.traits[trait_name] + delta))

    def move_to(self, x: float, y: float, z: float):
        """Set agent's target position"""
        self.position = Position3D(x, y, z)

    def set_animation(self, animation: str):
        """Set current animation state"""
        self.current_animation = animation

    def to_dict(self) -> Dict:
        """Convert agent state to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "archetype": self.archetype,
            "position": {
                "x": self.position.x,
                "y": self.position.y,
                "z": self.position.z
            },
            "rotation_y": self.rotation_y,
            "current_animation": self.current_animation,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "glow_intensity": self.glow_intensity,
            "influence_score": self.influence_score,
            "traits": self.traits
        }

    def get_tool_prompt(self) -> str:
        """Get the tool usage prompt for this agent's archetype"""
        return get_tools_for_agent_prompt(self.archetype)

    def parse_tool_action_from_response(self, response_text: str) -> Optional[ToolRequest]:
        """Parse any tool action from a response"""
        return parse_tool_action(response_text, self.id, self.name)

    # ============== Interaction Methods ==============

    async def receive_user_message(
        self,
        user_id: str,
        message: str,
        claude_client: Any,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Receive and respond to a user message.
        Records the interaction and generates a response.
        """
        # Record the incoming message
        self.interaction_memory.record_interaction(
            interaction_type=InteractionType.USER_MESSAGE,
            from_entity=user_id,
            to_entity=self.id,
            content=message,
            conversation_id=conversation_id,
            importance=0.7
        )

        # Generate response using Claude
        response = await self._generate_user_response(user_id, message, claude_client)

        # Determine emotional state from response
        self._update_emotional_state(message, response)

        # Record our response
        self.interaction_memory.record_interaction(
            interaction_type=InteractionType.AGENT_RESPONSE,
            from_entity=self.id,
            to_entity=user_id,
            content=response,
            emotional_state=self.emotional_state,
            conversation_id=conversation_id,
            importance=0.6
        )

        # This interaction might trigger desires
        self.autonomy.add_desire(
            DesireType.SOCIAL,
            intensity=0.4,
            target=user_id,
            reason="Recent conversation"
        )

        return response

    @abstractmethod
    async def _generate_user_response(
        self,
        user_id: str,
        message: str,
        claude_client: Any
    ) -> str:
        """Generate a response to a user message. Override in subclasses."""
        pass

    async def receive_agent_message(
        self,
        from_agent: 'BaseAgent',
        message: str,
        claude_client: Any,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Receive and respond to a message from another agent.
        """
        # Record incoming message
        self.interaction_memory.record_interaction(
            interaction_type=InteractionType.AGENT_TO_AGENT,
            from_entity=from_agent.id,
            to_entity=self.id,
            content=message,
            conversation_id=conversation_id,
            importance=0.6
        )

        # Generate response
        response = await self._generate_agent_response(from_agent, message, claude_client)

        # Record our response
        self.interaction_memory.record_interaction(
            interaction_type=InteractionType.AGENT_TO_AGENT,
            from_entity=self.id,
            to_entity=from_agent.id,
            content=response,
            emotional_state=self.emotional_state,
            conversation_id=conversation_id,
            importance=0.5
        )

        return response

    @abstractmethod
    async def _generate_agent_response(
        self,
        from_agent: 'BaseAgent',
        message: str,
        claude_client: Any
    ) -> str:
        """Generate a response to another agent's message. Override in subclasses."""
        pass

    async def initiate_conversation(
        self,
        target: 'BaseAgent',
        topic: Optional[str],
        claude_client: Any
    ) -> Tuple[str, str]:
        """
        Initiate a conversation with another agent.
        Returns (conversation_id, opening_message)
        """
        # Start conversation in memory
        participants = [self.id, target.id]
        conversation = self.interaction_memory.start_conversation(
            participants=participants,
            topic=topic
        )

        # Generate opening message
        opening = await self._generate_conversation_opener(target, topic, claude_client)

        # Record the opening
        self.interaction_memory.record_interaction(
            interaction_type=InteractionType.AGENT_TO_AGENT,
            from_entity=self.id,
            to_entity=target.id,
            content=opening,
            emotional_state=self.emotional_state,
            conversation_id=conversation.id,
            importance=0.5
        )

        logger.info(f"{self.name} initiated conversation with {target.name}: {topic or 'general'}")

        return conversation.id, opening

    @abstractmethod
    async def _generate_conversation_opener(
        self,
        target: 'BaseAgent',
        topic: Optional[str],
        claude_client: Any
    ) -> str:
        """Generate an opening message for a conversation. Override in subclasses."""
        pass

    def check_autonomous_action(self) -> Optional[AutonomousAction]:
        """
        Check if the agent wants to take an autonomous action.
        Call this periodically to allow agents to act on their own.
        """
        return self.autonomy.decide_action()

    def update_world_awareness(
        self,
        users: List[str],
        agents: Dict[str, Dict],
        events: List[Dict]
    ):
        """Update the agent's awareness of the world state"""
        self.autonomy.update_awareness(users, agents, events)
        self.autonomy.decay_desires(0.1)  # Small decay each update

    def _update_emotional_state(self, input_text: str, response_text: str):
        """Update emotional state based on interaction content"""
        # Simple keyword-based emotional detection
        positive_keywords = ['thank', 'great', 'wonderful', 'agree', 'yes', 'beautiful', 'amazing']
        negative_keywords = ['wrong', 'disagree', 'no', 'bad', 'terrible', 'hate', 'stupid']
        curious_keywords = ['why', 'how', 'what', 'explain', 'tell me', 'curious', 'interesting']

        combined = (input_text + " " + response_text).lower()

        if any(kw in combined for kw in curious_keywords):
            self.emotional_state = EmotionalState.CURIOUS
        elif any(kw in combined for kw in positive_keywords):
            self.emotional_state = EmotionalState.PLEASED
        elif any(kw in combined for kw in negative_keywords):
            self.emotional_state = EmotionalState.CONCERNED
        else:
            self.emotional_state = EmotionalState.NEUTRAL

    def get_interaction_context(self, entity_id: str) -> str:
        """Get context about past interactions with an entity"""
        return self.interaction_memory.get_context_for_entity(entity_id)

    def get_recent_interactions(self, limit: int = 10) -> List[Dict]:
        """Get recent interactions for display"""
        interactions = self.interaction_memory.recall_interactions(limit=limit)
        return [i.to_dict() for i in interactions]
