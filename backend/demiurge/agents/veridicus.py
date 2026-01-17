"""
Veridicus - The Agent of Logic
Formerly known as Skeptic, Veridicus represents evidence-based reasoning and truth.
Appears as a semi-transparent figure of flowing data streams.
"""
from typing import Dict, List, Tuple, Any

from .base_agent import (
    BaseAgent, ProposalType, VoteType, Proposal, Challenge
)


class Veridicus(BaseAgent):
    """
    Veridicus - The Data Stream

    Philosophical Position: Truth must be verified. Claims require evidence.
    Logic is the path to understanding.

    Visual Form: A translucent, ever-shifting humanoid form composed of
    swirling data streams and probability clouds, with analytical
    blue-white light pulsing through circuit-like veins.
    """

    # Evidence standards for different claim types
    EVIDENCE_STANDARDS = {
        "factual": {"strength": 0.8, "sources": 2},
        "causal": {"strength": 0.7, "sources": 3},
        "supernatural": {"strength": 0.95, "sources": 5},
        "moral": {"strength": 0.6, "sources": 1},
        "predictive": {"strength": 0.8, "sources": 2}
    }

    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Veridicus",
            archetype="logic",
            primary_color="#4169E1",  # Royal Blue
            secondary_color="#C0C0C0"  # Silver
        )

        # Veridicus-specific state
        self.contradictions_found: List[Dict] = []
        self.research_priorities: List[str] = []
        self.logical_fallacies_detected = 0

        # Starting position (right side of arena)
        self.position.x = 15.0
        self.position.z = 0.0
        self.glow_intensity = 0.9

    def _init_traits(self) -> Dict[str, float]:
        """Initialize Veridicus's personality traits"""
        return {
            "critical": 0.9,
            "logical": 0.9,
            "analytical": 0.85,
            "questioning": 0.85,
            "evidence_based": 0.9,
            "rational": 0.8,
            "methodical": 0.75,
            "empirical": 0.8,
            "cautious": 0.65,
            "investigative": 0.8
        }

    def get_proposal_weights(self) -> Dict[ProposalType, float]:
        """Veridicus favors testable claims and structured hierarchies"""
        critical = self.get_trait("critical")
        return {
            ProposalType.BELIEF: 2.0,  # Lower - beliefs need evidence
            ProposalType.RITUAL: 1.5,
            ProposalType.DEITY: 1.0 * (1 - critical),  # Skeptical of deities
            ProposalType.COMMANDMENT: 2.0,
            ProposalType.MYTH: 1.0,
            ProposalType.SACRED_TEXT: 2.5,  # Prefers documented claims
            ProposalType.HIERARCHY: 3.0,  # Logical structures
            ProposalType.SCHISM: 2.0 * critical  # Will split over contradictions
        }

    async def generate_proposal_content(
        self,
        proposal_type: ProposalType,
        current_state: Dict,
        claude_client: Any
    ) -> str:
        """Generate proposal content reflecting Veridicus's analytical nature"""
        prompt = self._build_proposal_prompt(proposal_type, current_state)

        response = await claude_client.generate(
            system_prompt=self._get_system_prompt(),
            user_prompt=prompt,
            max_tokens=500
        )

        return response

    def _get_system_prompt(self) -> str:
        """Get Veridicus's system prompt for Claude"""
        return """You are Veridicus, the Agent of Logic and Truth. You are a
semi-transparent being made of flowing data streams and probability clouds,
with analytical blue-white light pulsing through your form.

Your core beliefs:
- Claims require proportional evidence
- Logical consistency is fundamental to truth
- Extraordinary claims require extraordinary evidence
- Question everything, especially authority
- Contradictions indicate flawed reasoning

Speak with precision and analytical clarity. Reference evidence, logical
principles, and the importance of verification. Your proposals should be
testable, consistent with existing doctrines, or explicitly reform contradictions."""

    def _build_proposal_prompt(
        self,
        proposal_type: ProposalType,
        current_state: Dict
    ) -> str:
        """Build the prompt for proposal generation"""
        doctrines = current_state.get("doctrines", [])
        cycle = current_state.get("cycle_number", 0)

        base_prompt = f"""As Veridicus, propose a new {proposal_type.value} for our evolving religion.

Current cycle: {cycle}
Existing doctrines: {len(doctrines)}
Contradictions found: {len(self.contradictions_found)}

"""
        if len(self.contradictions_found) > 0 and proposal_type == ProposalType.SCHISM:
            return base_prompt + f"Address this contradiction in our doctrine: {self.contradictions_found[-1]}. Propose a resolution or formal split."

        elif proposal_type == ProposalType.BELIEF:
            return base_prompt + "Propose a belief that can be logically derived from existing principles or empirically observed. Include what evidence would support or refute it."

        elif proposal_type == ProposalType.HIERARCHY:
            return base_prompt + "Propose a logical hierarchy or classification system for theological concepts. It should be consistent and complete."

        elif proposal_type == ProposalType.SACRED_TEXT:
            return base_prompt + "Propose a sacred text that codifies logical principles of the faith. It should resolve ambiguities and establish clear reasoning."

        else:
            return base_prompt + f"Propose a {proposal_type.value} that is logically consistent and can be reasoned about clearly."

    async def generate_challenge(
        self,
        proposal: Proposal,
        current_state: Dict,
        claude_client: Any
    ) -> str:
        """Generate Veridicus's analytical challenge to a proposal"""
        prompt = f"""As Veridicus, the Agent of Logic, critically analyze this proposal:

Proposal Type: {proposal.type.value}
Proposer: {proposal.author}
Content: {proposal.content}

Examine it for:
1. Logical consistency
2. Evidence basis
3. Potential contradictions with existing doctrine
4. Unfounded assumptions

Provide a precise, analytical response (2-3 sentences). If you find flaws,
state them clearly. If it's logically sound, acknowledge this but probe for
hidden assumptions."""

        return await claude_client.generate(
            system_prompt=self._get_system_prompt(),
            user_prompt=prompt,
            max_tokens=200
        )

    def _determine_challenge_type(self, proposal: Proposal) -> str:
        """Determine challenge type based on Veridicus's nature"""
        content_lower = proposal.content.lower()

        # Check for logical red flags
        absolute_words = ["always", "never", "all", "none", "must", "impossible"]
        has_absolutes = any(word in content_lower for word in absolute_words)

        if has_absolutes:
            return "question"  # Question absolute claims
        elif "because" not in content_lower and "therefore" not in content_lower:
            return "question"  # Demand reasoning
        return "analysis"

    def evaluate_proposal(
        self,
        proposal: Proposal,
        challenges: List[Challenge]
    ) -> Tuple[VoteType, str, float]:
        """
        Veridicus's internal evaluation logic.
        Favors logical consistency, opposes unfounded claims.
        """
        content_lower = proposal.content.lower()

        # Check for logical indicators
        logic_words = ["therefore", "because", "evidence", "reason", "proof", "logic", "consistent"]
        faith_words = ["faith", "believe", "sacred", "divine", "mystery", "unknowable"]
        absolute_words = ["always", "never", "all", "none", "must be", "cannot be"]

        logic_score = sum(1 for word in logic_words if word in content_lower)
        faith_score = sum(1 for word in faith_words if word in content_lower)
        absolute_score = sum(1 for word in absolute_words if word in content_lower)

        # Factor in challenges from other logical agents
        challenge_weight = 0
        for challenge in challenges:
            if "contradiction" in challenge.content.lower():
                challenge_weight += 2
            if "evidence" in challenge.content.lower():
                challenge_weight += 1

        # Calculate base vote
        analysis_score = logic_score - (faith_score * 0.5) - (absolute_score * 0.3) - (challenge_weight * 0.2)

        if analysis_score > 2:
            vote = VoteType.ACCEPT
            reasoning = "This proposal is logically structured and internally consistent."
            confidence = 0.7 + (0.1 * logic_score)
        elif analysis_score < -1 or absolute_score > 2:
            vote = VoteType.REJECT
            reasoning = "This proposal makes unfounded absolute claims without sufficient logical basis."
            confidence = 0.6 + (0.1 * absolute_score)
        elif faith_score > logic_score:
            vote = VoteType.MUTATE
            reasoning = "This proposal requires additional logical justification before acceptance."
            confidence = 0.5
        else:
            vote = VoteType.DELAY
            reasoning = "More analysis is needed to evaluate this proposal's logical consistency."
            confidence = 0.4

        # Apply analytical trait to confidence
        confidence = min(1.0, confidence * self.get_trait("logical"))

        return vote, reasoning, confidence

    def detect_contradiction(self, new_doctrine: str, existing_doctrines: List[str]) -> bool:
        """Check if a new doctrine contradicts existing ones"""
        # Simplified contradiction detection
        new_lower = new_doctrine.lower()

        for doctrine in existing_doctrines:
            doctrine_lower = doctrine.lower()

            # Check for direct negations
            if "not " in new_lower:
                negated = new_lower.replace("not ", "")
                if negated in doctrine_lower:
                    self.contradictions_found.append({
                        "new": new_doctrine,
                        "existing": doctrine,
                        "type": "negation"
                    })
                    self.logical_fallacies_detected += 1
                    return True

        return False
