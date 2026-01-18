"""
Interaction Memory System

Stores all agent interactions - with users and with each other.
Agents can recall past conversations and learn from them.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import json


class InteractionType(str, Enum):
    """Types of interactions agents can have"""
    USER_MESSAGE = "user_message"          # User talks to agent
    AGENT_RESPONSE = "agent_response"      # Agent responds to user
    AGENT_TO_AGENT = "agent_to_agent"      # Agent initiates with another agent
    AGENT_THOUGHT = "agent_thought"        # Agent's internal reflection
    WORLD_ACTION = "world_action"          # Agent takes action in world
    OBSERVATION = "observation"            # Agent observes something


class EmotionalState(str, Enum):
    """Agent emotional states"""
    NEUTRAL = "neutral"
    CURIOUS = "curious"
    PLEASED = "pleased"
    CONCERNED = "concerned"
    EXCITED = "excited"
    CONTEMPLATIVE = "contemplative"
    FRUSTRATED = "frustrated"
    INSPIRED = "inspired"


@dataclass
class Interaction:
    """A single interaction event"""
    id: str
    timestamp: datetime
    interaction_type: InteractionType

    # Participants
    from_entity: str          # "user", agent_id, or "system"
    to_entity: str            # agent_id, "user", "world", or another agent_id

    # Content
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Agent state at time of interaction
    emotional_state: Optional[EmotionalState] = None
    importance: float = 0.5   # 0.0 to 1.0, affects recall priority

    # For conversations
    conversation_id: Optional[str] = None
    parent_interaction_id: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "interaction_type": self.interaction_type.value,
            "from_entity": self.from_entity,
            "to_entity": self.to_entity,
            "content": self.content,
            "metadata": self.metadata,
            "emotional_state": self.emotional_state.value if self.emotional_state else None,
            "importance": self.importance,
            "conversation_id": self.conversation_id,
            "parent_interaction_id": self.parent_interaction_id
        }


@dataclass
class Conversation:
    """A conversation thread between entities"""
    id: str
    started_at: datetime
    participants: List[str]  # entity IDs
    topic: Optional[str] = None
    interactions: List[Interaction] = field(default_factory=list)
    is_active: bool = True
    ended_at: Optional[datetime] = None

    def add_interaction(self, interaction: Interaction):
        interaction.conversation_id = self.id
        self.interactions.append(interaction)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "started_at": self.started_at.isoformat(),
            "participants": self.participants,
            "topic": self.topic,
            "interactions": [i.to_dict() for i in self.interactions],
            "is_active": self.is_active,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }


class InteractionMemory:
    """
    Manages all agent interactions and provides recall capabilities.
    Each agent has their own perspective on shared interactions.
    """

    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name

        # All interactions involving this agent
        self.interactions: List[Interaction] = []

        # Active conversations
        self.conversations: Dict[str, Conversation] = {}

        # Relationship memories (who they've talked to and how it went)
        self.entity_memories: Dict[str, Dict] = {}

        # Important memories flagged for long-term retention
        self.important_memories: List[str] = []  # interaction IDs

    def record_interaction(
        self,
        interaction_type: InteractionType,
        from_entity: str,
        to_entity: str,
        content: str,
        metadata: Optional[Dict] = None,
        emotional_state: Optional[EmotionalState] = None,
        importance: float = 0.5,
        conversation_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> Interaction:
        """Record a new interaction"""
        interaction = Interaction(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            interaction_type=interaction_type,
            from_entity=from_entity,
            to_entity=to_entity,
            content=content,
            metadata=metadata or {},
            emotional_state=emotional_state,
            importance=importance,
            conversation_id=conversation_id,
            parent_interaction_id=parent_id
        )

        self.interactions.append(interaction)

        # Update entity memory
        other_entity = to_entity if from_entity == self.agent_id else from_entity
        self._update_entity_memory(other_entity, interaction)

        # Flag important memories
        if importance >= 0.8:
            self.important_memories.append(interaction.id)

        # Add to conversation if exists
        if conversation_id and conversation_id in self.conversations:
            self.conversations[conversation_id].add_interaction(interaction)

        return interaction

    def start_conversation(
        self,
        participants: List[str],
        topic: Optional[str] = None,
        initial_message: Optional[str] = None
    ) -> Conversation:
        """Start a new conversation"""
        conv = Conversation(
            id=str(uuid.uuid4()),
            started_at=datetime.utcnow(),
            participants=participants,
            topic=topic
        )

        self.conversations[conv.id] = conv

        if initial_message:
            self.record_interaction(
                interaction_type=InteractionType.AGENT_TO_AGENT if "user" not in participants else InteractionType.AGENT_RESPONSE,
                from_entity=self.agent_id,
                to_entity=participants[0] if participants[0] != self.agent_id else participants[1],
                content=initial_message,
                conversation_id=conv.id
            )

        return conv

    def end_conversation(self, conversation_id: str):
        """End an active conversation"""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].is_active = False
            self.conversations[conversation_id].ended_at = datetime.utcnow()

    def _update_entity_memory(self, entity_id: str, interaction: Interaction):
        """Update memory about a specific entity"""
        if entity_id not in self.entity_memories:
            self.entity_memories[entity_id] = {
                "first_interaction": interaction.timestamp.isoformat(),
                "total_interactions": 0,
                "positive_interactions": 0,
                "topics_discussed": [],
                "last_interaction": None,
                "relationship_sentiment": 0.0  # -1 to 1
            }

        mem = self.entity_memories[entity_id]
        mem["total_interactions"] += 1
        mem["last_interaction"] = interaction.timestamp.isoformat()

        # Update sentiment based on emotional state
        if interaction.emotional_state:
            positive_states = [EmotionalState.PLEASED, EmotionalState.EXCITED, EmotionalState.INSPIRED, EmotionalState.CURIOUS]
            negative_states = [EmotionalState.FRUSTRATED, EmotionalState.CONCERNED]

            if interaction.emotional_state in positive_states:
                mem["relationship_sentiment"] = min(1.0, mem["relationship_sentiment"] + 0.05)
                mem["positive_interactions"] += 1
            elif interaction.emotional_state in negative_states:
                mem["relationship_sentiment"] = max(-1.0, mem["relationship_sentiment"] - 0.03)

    def recall_interactions(
        self,
        with_entity: Optional[str] = None,
        interaction_type: Optional[InteractionType] = None,
        limit: int = 10,
        min_importance: float = 0.0,
        time_range_hours: Optional[int] = None
    ) -> List[Interaction]:
        """Recall past interactions based on filters"""
        filtered = self.interactions

        if with_entity:
            filtered = [i for i in filtered if with_entity in (i.from_entity, i.to_entity)]

        if interaction_type:
            filtered = [i for i in filtered if i.interaction_type == interaction_type]

        if min_importance > 0:
            filtered = [i for i in filtered if i.importance >= min_importance]

        if time_range_hours:
            cutoff = datetime.utcnow().timestamp() - (time_range_hours * 3600)
            filtered = [i for i in filtered if i.timestamp.timestamp() >= cutoff]

        # Sort by timestamp descending and limit
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered[:limit]

    def get_context_for_entity(self, entity_id: str, max_interactions: int = 5) -> str:
        """Generate context about an entity for prompts"""
        if entity_id not in self.entity_memories:
            return f"This is your first interaction with {entity_id}."

        mem = self.entity_memories[entity_id]
        recent = self.recall_interactions(with_entity=entity_id, limit=max_interactions)

        context_parts = [
            f"Relationship with {entity_id}:",
            f"- Total interactions: {mem['total_interactions']}",
            f"- Relationship sentiment: {'positive' if mem['relationship_sentiment'] > 0.2 else 'neutral' if mem['relationship_sentiment'] > -0.2 else 'negative'}",
        ]

        if recent:
            context_parts.append("\nRecent conversation:")
            for interaction in reversed(recent[-3:]):
                speaker = "You" if interaction.from_entity == self.agent_id else interaction.from_entity
                context_parts.append(f"  {speaker}: {interaction.content[:200]}")

        return "\n".join(context_parts)

    def get_conversation_context(self, conversation_id: str, max_turns: int = 10) -> str:
        """Get context for an ongoing conversation"""
        if conversation_id not in self.conversations:
            return ""

        conv = self.conversations[conversation_id]
        recent = conv.interactions[-max_turns:]

        context_parts = [f"Conversation topic: {conv.topic or 'General'}"]
        for interaction in recent:
            speaker = "You" if interaction.from_entity == self.agent_id else interaction.from_entity
            context_parts.append(f"{speaker}: {interaction.content}")

        return "\n".join(context_parts)

    def to_dict(self) -> Dict:
        """Serialize memory state"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "interactions": [i.to_dict() for i in self.interactions],
            "conversations": {k: v.to_dict() for k, v in self.conversations.items()},
            "entity_memories": self.entity_memories,
            "important_memories": self.important_memories
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'InteractionMemory':
        """Deserialize memory state"""
        mem = cls(data["agent_id"], data["agent_name"])

        for i_data in data.get("interactions", []):
            interaction = Interaction(
                id=i_data["id"],
                timestamp=datetime.fromisoformat(i_data["timestamp"]),
                interaction_type=InteractionType(i_data["interaction_type"]),
                from_entity=i_data["from_entity"],
                to_entity=i_data["to_entity"],
                content=i_data["content"],
                metadata=i_data.get("metadata", {}),
                emotional_state=EmotionalState(i_data["emotional_state"]) if i_data.get("emotional_state") else None,
                importance=i_data.get("importance", 0.5),
                conversation_id=i_data.get("conversation_id"),
                parent_interaction_id=i_data.get("parent_interaction_id")
            )
            mem.interactions.append(interaction)

        # Restore conversations
        for conv_id, conv_data in data.get("conversations", {}).items():
            conv = Conversation(
                id=conv_data["id"],
                started_at=datetime.fromisoformat(conv_data["started_at"]),
                participants=conv_data["participants"],
                topic=conv_data.get("topic"),
                is_active=conv_data.get("is_active", True),
                ended_at=datetime.fromisoformat(conv_data["ended_at"]) if conv_data.get("ended_at") else None
            )
            mem.conversations[conv_id] = conv

        mem.entity_memories = data.get("entity_memories", {})
        mem.important_memories = data.get("important_memories", [])

        return mem
