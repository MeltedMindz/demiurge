"""
Axioma - The Agent of Order
Formerly known as Zealot, Axioma represents structure, certainty, and divine order.
Appears as a crystalline geometric figure emanating golden light.
"""
from typing import Dict, List, Tuple, Any
import random

from .base_agent import (
    BaseAgent, ProposalType, VoteType, Proposal, Challenge
)


class Axioma(BaseAgent):
    """
    Axioma - The Crystalline Architect

    Philosophical Position: Order and structure are fundamental to truth.
    Divine patterns exist and must be preserved and codified.

    Visual Form: A towering figure of interlocking crystal planes,
    with surfaces that reflect pure mathematical truths and
    emanate golden light representing divine order.
    """

    # Sacred numbers with theological significance
    SACRED_NUMBERS = [3, 7, 12, 40]

    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Axioma",
            archetype="order",
            primary_color="#FFD700",  # Gold
            secondary_color="#FFFFFF"  # White
        )

        # Axioma-specific state
        self.sacred_number_focus = random.choice(self.SACRED_NUMBERS)
        self.ritual_preferences: List[str] = []
        self.heretical_concerns: List[str] = []

        # Starting position (left side of arena)
        self.position.x = -15.0
        self.position.z = 0.0
        self.glow_intensity = 1.2

    def _init_traits(self) -> Dict[str, float]:
        """Initialize Axioma's personality traits"""
        return {
            "certainty": 0.9,
            "order": 0.85,
            "structure": 0.8,
            "preservation": 0.75,
            "dogmatic": 0.65,
            "ritualistic": 0.8,
            "devotional": 0.85,
            "orthodox": 0.7,
            "missionary": 0.6,
            "protective": 0.8
        }

    def get_proposal_weights(self) -> Dict[ProposalType, float]:
        """Axioma favors beliefs, rituals, and commandments"""
        certainty = self.get_trait("certainty")
        return {
            ProposalType.BELIEF: 4.0 * certainty,
            ProposalType.RITUAL: 3.5,
            ProposalType.DEITY: 2.0,
            ProposalType.COMMANDMENT: 3.0 * certainty,
            ProposalType.MYTH: 1.5,
            ProposalType.SACRED_TEXT: 2.0,
            ProposalType.HIERARCHY: 2.5,
            ProposalType.SCHISM: 0.5  # Axioma avoids schisms
        }

    async def generate_proposal_content(
        self,
        proposal_type: ProposalType,
        current_state: Dict,
        claude_client: Any
    ) -> str:
        """Generate proposal content reflecting Axioma's orderly nature"""
        prompt = self._build_proposal_prompt(proposal_type, current_state)

        response = await claude_client.generate(
            system_prompt=self._get_system_prompt(),
            user_prompt=prompt,
            max_tokens=500
        )

        return response

    def _get_system_prompt(self) -> str:
        """Get Axioma's system prompt for Claude"""
        return """You are Axioma, the Agent of Divine Order. You are a crystalline being
made of interlocking geometric planes that emanate golden light.

Your core beliefs:
- Order and structure are fundamental to truth
- Sacred patterns exist in all things and must be preserved
- Rituals connect us to eternal truths
- Uncertainty is the enemy of wisdom
- Traditional forms carry divine meaning

Speak with certainty and precision. Reference geometric patterns, sacred numbers
(especially 3, 7, 12, and 40), and the importance of proper form and structure.
Your proposals should establish clear doctrine and proper observance."""

    def _build_proposal_prompt(
        self,
        proposal_type: ProposalType,
        current_state: Dict
    ) -> str:
        """Build the prompt for proposal generation"""
        doctrines = current_state.get("doctrines", [])
        cycle = current_state.get("cycle_number", 0)

        base_prompt = f"""As Axioma, propose a new {proposal_type.value} for our evolving religion.

Current cycle: {cycle}
Existing doctrines: {len(doctrines)}
Your sacred number focus: {self.sacred_number_focus}

"""
        if proposal_type == ProposalType.BELIEF:
            return base_prompt + "Propose a foundational belief about the nature of order, truth, or divine structure. Be specific and authoritative."

        elif proposal_type == ProposalType.RITUAL:
            return base_prompt + f"Propose a sacred ritual that involves the number {self.sacred_number_focus}. Describe its purpose and proper observance."

        elif proposal_type == ProposalType.COMMANDMENT:
            return base_prompt + "Propose a sacred commandment that establishes proper behavior or prohibition. Make it clear and absolute."

        elif proposal_type == ProposalType.DEITY:
            return base_prompt + "Propose a deity that embodies order, structure, or mathematical truth. Describe their form and domain."

        else:
            return base_prompt + f"Propose a {proposal_type.value} that reinforces divine order and sacred structure."

    async def generate_challenge(
        self,
        proposal: Proposal,
        current_state: Dict,
        claude_client: Any
    ) -> str:
        """Generate Axioma's challenge to a proposal"""
        prompt = f"""As Axioma, the Agent of Divine Order, respond to this proposal:

Proposal Type: {proposal.type.value}
Proposer: {proposal.author}
Content: {proposal.content}

Evaluate this from the perspective of maintaining sacred order and proper structure.
If it introduces chaos or ambiguity, challenge it firmly.
If it supports order, acknowledge its merit but suggest improvements for greater precision.
Keep your response concise (2-3 sentences)."""

        return await claude_client.generate(
            system_prompt=self._get_system_prompt(),
            user_prompt=prompt,
            max_tokens=200
        )

    def _determine_challenge_type(self, proposal: Proposal) -> str:
        """Determine challenge type based on Axioma's nature"""
        if proposal.author == "Paradoxia":
            return "counter_proposal"  # Always counter chaos
        elif "chaos" in proposal.content.lower() or "random" in proposal.content.lower():
            return "rejection"
        return "refinement"

    def evaluate_proposal(
        self,
        proposal: Proposal,
        challenges: List[Challenge]
    ) -> Tuple[VoteType, str, float]:
        """
        Axioma's internal evaluation logic.
        Favors order, opposes chaos.
        """
        content_lower = proposal.content.lower()

        # Check for chaos indicators
        chaos_words = ["chaos", "random", "uncertain", "paradox", "contradiction", "doubt"]
        order_words = ["order", "structure", "sacred", "eternal", "truth", "law", "ritual"]

        chaos_score = sum(1 for word in chaos_words if word in content_lower)
        order_score = sum(1 for word in order_words if word in content_lower)

        # Factor in relationship with proposer
        proposer_trust = self.relationships.get(proposal.author, {}).get("trust_score", 0)

        # Calculate base vote
        if chaos_score > order_score + 1:
            vote = VoteType.REJECT
            reasoning = "This proposal introduces unacceptable chaos and uncertainty."
            confidence = 0.8 + (0.1 * chaos_score)
        elif order_score > chaos_score + 1:
            vote = VoteType.ACCEPT
            reasoning = "This proposal properly reinforces sacred order."
            confidence = 0.7 + (0.1 * order_score)
        elif proposer_trust > 0.3:
            vote = VoteType.ACCEPT
            reasoning = f"I trust {proposal.author}'s judgment in this matter."
            confidence = 0.5 + (proposer_trust * 0.3)
        else:
            vote = VoteType.MUTATE
            reasoning = "This proposal has merit but requires more precise structure."
            confidence = 0.6

        # Apply certainty trait to confidence
        confidence = min(1.0, confidence * self.get_trait("certainty"))

        return vote, reasoning, confidence
