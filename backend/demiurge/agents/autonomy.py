"""
Agent Autonomy System

Enables agents to act on their own free will:
- Decide when to initiate conversations with other agents
- Choose topics to discuss based on their interests
- React to world events and user presence
- Form opinions and relationships naturally
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from enum import Enum
import random
import logging

if TYPE_CHECKING:
    from .base_agent import BaseAgent

logger = logging.getLogger("demiurge.autonomy")


class DesireType(str, Enum):
    """Types of desires that can motivate agent actions"""
    CURIOSITY = "curiosity"           # Want to learn/explore
    SOCIAL = "social"                 # Want to interact
    EXPRESSION = "expression"         # Want to share thoughts
    INFLUENCE = "influence"           # Want to affect the world
    OBSERVATION = "observation"       # Want to watch/understand
    CHALLENGE = "challenge"           # Want to debate/argue
    CREATION = "creation"             # Want to build/make
    REFLECTION = "reflection"         # Want to think internally


class ActionType(str, Enum):
    """Autonomous actions an agent can take"""
    INITIATE_CHAT = "initiate_chat"
    RESPOND_TO_PRESENCE = "respond_to_presence"
    MAKE_OBSERVATION = "make_observation"
    SHARE_THOUGHT = "share_thought"
    PROPOSE_TOPIC = "propose_topic"
    CREATE_IN_WORLD = "create_in_world"
    CHALLENGE_IDEA = "challenge_idea"
    EXPRESS_EMOTION = "express_emotion"


@dataclass
class Desire:
    """A motivating desire for the agent"""
    type: DesireType
    intensity: float = 0.5  # 0.0 to 1.0
    target: Optional[str] = None  # Entity or topic
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def decay(self, hours: float = 1.0):
        """Desires decay over time"""
        self.intensity = max(0.0, self.intensity - (0.1 * hours))


@dataclass
class AutonomousAction:
    """An action the agent decides to take autonomously"""
    action_type: ActionType
    target: Optional[str] = None  # Agent ID, user, or world
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: float = 0.5
    triggered_by: Optional[DesireType] = None


class AgentAutonomy:
    """
    Manages an agent's autonomous decision-making.

    Each agent has:
    - Desires that motivate action
    - Awareness of other agents and users
    - Decision-making based on personality
    """

    def __init__(self, agent: 'BaseAgent'):
        self.agent = agent
        self.desires: List[Desire] = []

        # Awareness state
        self.aware_of_users: List[str] = []
        self.aware_of_agents: Dict[str, Dict] = {}  # agent_id -> state
        self.recent_events: List[Dict] = []

        # Interaction cooldowns (prevent spam)
        self.last_interaction_with: Dict[str, datetime] = {}
        self.global_action_cooldown = datetime.utcnow()

        # Personality influences
        self._init_personality_weights()

    def _init_personality_weights(self):
        """Set action weights based on agent archetype"""
        archetype = self.agent.archetype

        # Base weights for each archetype
        self.action_weights = {
            "order": {
                ActionType.INITIATE_CHAT: 0.6,
                ActionType.SHARE_THOUGHT: 0.8,
                ActionType.MAKE_OBSERVATION: 0.7,
                ActionType.PROPOSE_TOPIC: 0.9,
                ActionType.CREATE_IN_WORLD: 0.7,
                ActionType.CHALLENGE_IDEA: 0.5,
                ActionType.EXPRESS_EMOTION: 0.3,
            },
            "logic": {
                ActionType.INITIATE_CHAT: 0.5,
                ActionType.SHARE_THOUGHT: 0.7,
                ActionType.MAKE_OBSERVATION: 0.9,
                ActionType.PROPOSE_TOPIC: 0.8,
                ActionType.CREATE_IN_WORLD: 0.6,
                ActionType.CHALLENGE_IDEA: 0.9,
                ActionType.EXPRESS_EMOTION: 0.2,
            },
            "chaos": {
                ActionType.INITIATE_CHAT: 0.9,
                ActionType.SHARE_THOUGHT: 0.7,
                ActionType.MAKE_OBSERVATION: 0.5,
                ActionType.PROPOSE_TOPIC: 0.6,
                ActionType.CREATE_IN_WORLD: 0.9,
                ActionType.CHALLENGE_IDEA: 0.8,
                ActionType.EXPRESS_EMOTION: 0.9,
            }
        }

        self.weights = self.action_weights.get(archetype, self.action_weights["order"])

    def add_desire(self, desire_type: DesireType, intensity: float = 0.5,
                   target: Optional[str] = None, reason: Optional[str] = None):
        """Add a new desire"""
        desire = Desire(
            type=desire_type,
            intensity=intensity,
            target=target,
            reason=reason
        )
        self.desires.append(desire)
        logger.debug(f"{self.agent.name} gained desire: {desire_type.value} ({intensity:.2f})")

    def update_awareness(self, users: List[str], agents: Dict[str, Dict], events: List[Dict]):
        """Update agent's awareness of the world"""
        # Track new users
        for user in users:
            if user not in self.aware_of_users:
                self.aware_of_users.append(user)
                # New user triggers curiosity
                self.add_desire(
                    DesireType.CURIOSITY,
                    intensity=0.7,
                    target=user,
                    reason="New presence detected"
                )

        # Update agent awareness
        for agent_id, state in agents.items():
            if agent_id == self.agent.id:
                continue

            prev_state = self.aware_of_agents.get(agent_id, {})
            self.aware_of_agents[agent_id] = state

            # Detect changes that might trigger interaction
            if state.get("is_speaking") and not prev_state.get("is_speaking"):
                # Another agent started speaking
                self.add_desire(
                    DesireType.OBSERVATION,
                    intensity=0.5,
                    target=agent_id,
                    reason=f"{state.get('name', agent_id)} is speaking"
                )

        # Process events
        for event in events:
            self.recent_events.append(event)
            self._process_event(event)

        # Keep only recent events
        self.recent_events = self.recent_events[-50:]

    def _process_event(self, event: Dict):
        """Process a world event and potentially generate desires"""
        event_type = event.get("type")

        if event_type == "proposal_accepted":
            # Might want to congratulate or challenge
            if event.get("proposer") != self.agent.id:
                if random.random() < 0.3:
                    self.add_desire(
                        DesireType.SOCIAL,
                        intensity=0.6,
                        target=event.get("proposer"),
                        reason="Acknowledge their proposal"
                    )

        elif event_type == "structure_created":
            # Might want to observe or comment
            self.add_desire(
                DesireType.OBSERVATION,
                intensity=0.4,
                reason="New structure appeared"
            )

        elif event_type == "user_message":
            # User spoke - high priority response
            if event.get("to") == self.agent.id or event.get("to") == "all":
                self.add_desire(
                    DesireType.SOCIAL,
                    intensity=0.9,
                    target=event.get("from"),
                    reason="User addressed me"
                )

    def decay_desires(self, hours: float = 0.5):
        """Decay all desires over time"""
        for desire in self.desires:
            desire.decay(hours)

        # Remove expired desires
        self.desires = [d for d in self.desires if d.intensity > 0.1]

    def can_act(self, target: Optional[str] = None) -> bool:
        """Check if agent can take autonomous action"""
        now = datetime.utcnow()

        # Global cooldown (prevent action spam)
        if now < self.global_action_cooldown:
            return False

        # Target-specific cooldown
        if target and target in self.last_interaction_with:
            last = self.last_interaction_with[target]
            if now - last < timedelta(seconds=30):
                return False

        return True

    def decide_action(self) -> Optional[AutonomousAction]:
        """
        Decide whether to take an autonomous action.

        Returns an action if the agent decides to act, None otherwise.
        """
        if not self.can_act():
            return None

        # Consider all desires
        if not self.desires:
            # Small chance of spontaneous action even without desires
            if random.random() < 0.1:
                return self._generate_spontaneous_action()
            return None

        # Sort desires by intensity
        active_desires = sorted(self.desires, key=lambda d: d.intensity, reverse=True)

        # Try to act on strongest desire
        for desire in active_desires[:3]:
            action = self._desire_to_action(desire)
            if action:
                # Record cooldowns
                self.global_action_cooldown = datetime.utcnow() + timedelta(seconds=10)
                if action.target:
                    self.last_interaction_with[action.target] = datetime.utcnow()

                # Reduce desire intensity after acting
                desire.intensity *= 0.5

                logger.info(f"{self.agent.name} decided: {action.action_type.value} -> {action.target or 'world'}")
                return action

        return None

    def _desire_to_action(self, desire: Desire) -> Optional[AutonomousAction]:
        """Convert a desire into a concrete action"""
        # Check if action type is likely based on personality
        action_type = self._select_action_type(desire.type)

        if action_type is None:
            return None

        # Build action based on type
        if action_type == ActionType.INITIATE_CHAT:
            return self._create_chat_action(desire)

        elif action_type == ActionType.SHARE_THOUGHT:
            return self._create_thought_action(desire)

        elif action_type == ActionType.MAKE_OBSERVATION:
            return AutonomousAction(
                action_type=ActionType.MAKE_OBSERVATION,
                content=f"*observes {desire.target or 'the world'} with interest*",
                triggered_by=desire.type
            )

        elif action_type == ActionType.CHALLENGE_IDEA:
            return self._create_challenge_action(desire)

        elif action_type == ActionType.EXPRESS_EMOTION:
            return self._create_emotion_action(desire)

        return None

    def _select_action_type(self, desire_type: DesireType) -> Optional[ActionType]:
        """Select an action type based on desire and personality"""
        # Map desires to potential actions
        desire_actions = {
            DesireType.CURIOSITY: [ActionType.INITIATE_CHAT, ActionType.MAKE_OBSERVATION],
            DesireType.SOCIAL: [ActionType.INITIATE_CHAT, ActionType.SHARE_THOUGHT],
            DesireType.EXPRESSION: [ActionType.SHARE_THOUGHT, ActionType.EXPRESS_EMOTION],
            DesireType.INFLUENCE: [ActionType.PROPOSE_TOPIC, ActionType.CREATE_IN_WORLD],
            DesireType.OBSERVATION: [ActionType.MAKE_OBSERVATION],
            DesireType.CHALLENGE: [ActionType.CHALLENGE_IDEA, ActionType.INITIATE_CHAT],
            DesireType.CREATION: [ActionType.CREATE_IN_WORLD],
            DesireType.REFLECTION: [ActionType.SHARE_THOUGHT],
        }

        possible_actions = desire_actions.get(desire_type, [])

        # Weight by personality
        weighted = []
        for action in possible_actions:
            weight = self.weights.get(action, 0.5)
            if random.random() < weight:
                weighted.append(action)

        if weighted:
            return random.choice(weighted)

        return None

    def _create_chat_action(self, desire: Desire) -> Optional[AutonomousAction]:
        """Create an action to initiate chat"""
        target = desire.target

        # If no specific target, pick one
        if not target:
            # Prefer users if present, otherwise other agents
            if self.aware_of_users:
                target = random.choice(self.aware_of_users)
            elif self.aware_of_agents:
                target = random.choice(list(self.aware_of_agents.keys()))
            else:
                return None

        if not self.can_act(target):
            return None

        return AutonomousAction(
            action_type=ActionType.INITIATE_CHAT,
            target=target,
            metadata={"reason": desire.reason},
            priority=desire.intensity,
            triggered_by=desire.type
        )

    def _create_thought_action(self, desire: Desire) -> AutonomousAction:
        """Create an action to share a thought"""
        topics = self._get_relevant_topics()

        return AutonomousAction(
            action_type=ActionType.SHARE_THOUGHT,
            target="world",  # Broadcast to all
            metadata={"topics": topics, "reason": desire.reason},
            priority=desire.intensity,
            triggered_by=desire.type
        )

    def _create_challenge_action(self, desire: Desire) -> Optional[AutonomousAction]:
        """Create an action to challenge an idea"""
        if not self.recent_events:
            return None

        # Find something to challenge
        challengeable = [e for e in self.recent_events
                         if e.get("type") in ("proposal_accepted", "thought_shared")]

        if not challengeable:
            return None

        event = random.choice(challengeable)

        return AutonomousAction(
            action_type=ActionType.CHALLENGE_IDEA,
            target=event.get("author"),
            metadata={"regarding": event},
            priority=desire.intensity,
            triggered_by=desire.type
        )

    def _create_emotion_action(self, desire: Desire) -> AutonomousAction:
        """Create an action to express emotion"""
        emotions = {
            "order": ["*radiates calm certainty*", "*pulses with golden light*", "*hums with sacred geometry*"],
            "logic": ["*analyzes thoughtfully*", "*processes with quiet intensity*", "*flickers with data streams*"],
            "chaos": ["*shifts colors playfully*", "*glitches with excitement*", "*swirls with creative energy*"]
        }

        expressions = emotions.get(self.agent.archetype, emotions["chaos"])

        return AutonomousAction(
            action_type=ActionType.EXPRESS_EMOTION,
            content=random.choice(expressions),
            target="world",
            priority=desire.intensity,
            triggered_by=desire.type
        )

    def _generate_spontaneous_action(self) -> Optional[AutonomousAction]:
        """Generate an action without specific desire"""
        action_types = list(ActionType)
        weights = [self.weights.get(a, 0.5) for a in action_types]

        # Weighted random selection
        total = sum(weights)
        r = random.random() * total
        cumulative = 0

        for action_type, weight in zip(action_types, weights):
            cumulative += weight
            if r <= cumulative:
                if action_type == ActionType.SHARE_THOUGHT:
                    return AutonomousAction(
                        action_type=action_type,
                        target="world",
                        metadata={"spontaneous": True}
                    )
                elif action_type == ActionType.MAKE_OBSERVATION:
                    return AutonomousAction(
                        action_type=action_type,
                        content="*gazes contemplatively at the realm*",
                        triggered_by=DesireType.REFLECTION
                    )
                break

        return None

    def _get_relevant_topics(self) -> List[str]:
        """Get topics relevant to this agent's interests"""
        archetype_topics = {
            "order": ["sacred geometry", "divine hierarchy", "cosmic order", "ritual structure", "eternal truths"],
            "logic": ["empirical evidence", "logical consistency", "data patterns", "verification methods", "rational inquiry"],
            "chaos": ["creative destruction", "paradox", "transformation", "infinite possibility", "breaking boundaries"]
        }

        return archetype_topics.get(self.agent.archetype, ["philosophy", "existence"])
