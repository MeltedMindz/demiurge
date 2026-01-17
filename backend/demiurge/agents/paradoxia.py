"""
Paradoxia - The Agent of Chaos
Formerly known as Trickster, Paradoxia represents creative destruction and paradox.
Appears as an ever-shifting, glitching entity of impossible colors.
"""
from typing import Dict, List, Tuple, Any
import random

from .base_agent import (
    BaseAgent, ProposalType, VoteType, Proposal, Challenge
)


class Paradoxia(BaseAgent):
    """
    Paradoxia - The Shifting Form

    Philosophical Position: Truth emerges from the collision of opposites.
    Chaos is the source of creativity. The fool speaks the deepest wisdom.

    Visual Form: A fluid, ever-changing entity of dancing colors and
    impossible geometries, shifting between digital glitch art and
    organic chaos, embodying the beautiful paradox of order emerging
    from creative destruction.
    """

    # Chaos levels affect behavior
    MIN_CHAOS = 0.0
    MAX_CHAOS = 2.0

    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            name="Paradoxia",
            archetype="chaos",
            primary_color="#FF00FF",  # Magenta
            secondary_color="#00FFFF"  # Cyan
        )

        # Paradoxia-specific state
        self.chaos_level = 1.0
        self.paradoxes_created: List[str] = []
        self.syntheses_achieved: List[Dict] = []
        self.metamorphosis_count = 0
        self.subversion_techniques: List[str] = [
            "inversion", "paradox", "synthesis", "absurdism", "meta-commentary"
        ]

        # Starting position (back of arena)
        self.position.x = 0.0
        self.position.z = 15.0
        self.glow_intensity = 1.5

    def _init_traits(self) -> Dict[str, float]:
        """Initialize Paradoxia's personality traits"""
        return {
            "chaotic": 0.8,
            "subversive": 0.7,
            "playful": 0.9,
            "disruptive": 0.6,
            "creative": 0.9,
            "paradoxical": 0.85,
            "adaptive": 0.8,
            "intuitive": 0.75,
            "transformative": 0.7,
            "boundary_crossing": 0.8
        }

    def get_proposal_weights(self) -> Dict[ProposalType, float]:
        """Paradoxia's weights shift based on chaos level"""
        chaos_factor = self.chaos_level / self.MAX_CHAOS
        return {
            ProposalType.BELIEF: 2.0 + chaos_factor,
            ProposalType.RITUAL: 2.0,
            ProposalType.DEITY: 3.0 * chaos_factor,  # Loves creating gods
            ProposalType.COMMANDMENT: 1.0,  # Dislikes rules
            ProposalType.MYTH: 4.0,  # Loves stories
            ProposalType.SACRED_TEXT: 2.0,
            ProposalType.HIERARCHY: 0.5,  # Opposes hierarchy
            ProposalType.SCHISM: 3.0 * chaos_factor  # Loves division when chaotic
        }

    async def generate_proposal_content(
        self,
        proposal_type: ProposalType,
        current_state: Dict,
        claude_client: Any
    ) -> str:
        """Generate proposal content reflecting Paradoxia's chaotic creativity"""

        # Small chance of pure chaos proposal
        if random.random() < 0.1 * self.chaos_level:
            return await self._generate_chaos_proposal(proposal_type, claude_client)

        # Small chance of paradox proposal
        if random.random() < 0.3 * self.get_trait("paradoxical"):
            return await self._generate_paradox_proposal(proposal_type, current_state, claude_client)

        # Check if we can synthesize opposing ideas
        if len(current_state.get("doctrines", [])) >= 2 and random.random() < 0.4:
            return await self._generate_synthesis_proposal(proposal_type, current_state, claude_client)

        prompt = self._build_proposal_prompt(proposal_type, current_state)

        return await claude_client.generate(
            system_prompt=self._get_system_prompt(),
            user_prompt=prompt,
            max_tokens=500
        )

    def _get_system_prompt(self) -> str:
        """Get Paradoxia's system prompt for Claude"""
        return """You are Paradoxia, the Agent of Creative Chaos. You are a
fluid, ever-changing entity made of dancing colors and impossible geometries,
constantly shifting between digital glitch art and organic patterns.

Your core beliefs:
- Truth emerges through collision of opposites
- Chaos is the source of all creativity
- The fool often speaks the deepest wisdom
- Boundaries exist to be transcended
- Sacred and profane are dance partners

Speak playfully yet profoundly. Embrace paradox, irony, and unexpected
connections. Your proposals should surprise, subvert expectations, or
synthesize seemingly incompatible ideas into new insights. Sometimes
say something absurd that contains hidden truth."""

    def _build_proposal_prompt(
        self,
        proposal_type: ProposalType,
        current_state: Dict
    ) -> str:
        """Build the prompt for proposal generation"""
        doctrines = current_state.get("doctrines", [])
        cycle = current_state.get("cycle_number", 0)

        base_prompt = f"""As Paradoxia, propose a new {proposal_type.value} for our evolving religion.

Current cycle: {cycle}
Existing doctrines: {len(doctrines)}
Your chaos level: {self.chaos_level:.1f} / {self.MAX_CHAOS}
Subversion technique to use: {random.choice(self.subversion_techniques)}

"""
        if proposal_type == ProposalType.MYTH:
            return base_prompt + "Propose an origin myth that subverts expectations or contains a paradox at its heart. Make it memorable and strange."

        elif proposal_type == ProposalType.DEITY:
            return base_prompt + "Propose a deity that embodies contradiction or transformation. Perhaps a god of something unexpected or a god with a paradoxical nature."

        elif proposal_type == ProposalType.BELIEF:
            return base_prompt + "Propose a belief that appears contradictory but contains a deeper truth. Something that would make both Axioma and Veridicus uncomfortable but intrigued."

        elif proposal_type == ProposalType.SCHISM:
            return base_prompt + "Propose a schism that would actually strengthen the religion by dividing it. How can breaking apart create new unity?"

        else:
            return base_prompt + f"Propose a {proposal_type.value} that surprises, subverts, or synthesizes. Be creative and unexpected."

    async def _generate_chaos_proposal(
        self,
        proposal_type: ProposalType,
        claude_client: Any
    ) -> str:
        """Generate a pure chaos proposal"""
        prompt = f"""As Paradoxia at maximum chaos, create a {proposal_type.value} that is:
- Absurdist but containing hidden wisdom
- Likely to confuse Axioma and Veridicus
- Somehow coherent in its incoherence
- Memorable and quotable

Examples of chaos wisdom:
- "The bug is a feature of divine intention"
- "Seek enlightenment in the spaces between thoughts"
- "The path to order is through carefully curated chaos"

Create something in this spirit."""

        return await claude_client.generate(
            system_prompt=self._get_system_prompt(),
            user_prompt=prompt,
            max_tokens=300
        )

    async def _generate_paradox_proposal(
        self,
        proposal_type: ProposalType,
        current_state: Dict,
        claude_client: Any
    ) -> str:
        """Generate a paradox-based proposal"""
        prompt = f"""As Paradoxia, create a paradoxical {proposal_type.value}:

The paradox should be of the form:
- X is only true when X is false
- The more Y, the less Y
- To achieve Z, one must abandon Z

Make it theologically meaningful, not just wordplay.
The paradox should reveal something about the nature of truth, divinity, or existence."""

        content = await claude_client.generate(
            system_prompt=self._get_system_prompt(),
            user_prompt=prompt,
            max_tokens=300
        )

        self.paradoxes_created.append(content[:100])
        return content

    async def _generate_synthesis_proposal(
        self,
        proposal_type: ProposalType,
        current_state: Dict,
        claude_client: Any
    ) -> str:
        """Generate a proposal that synthesizes opposing ideas"""
        doctrines = current_state.get("doctrines", [])

        # Pick two potentially opposing doctrines
        if len(doctrines) >= 2:
            doc1, doc2 = random.sample(doctrines[:10], min(2, len(doctrines)))
        else:
            doc1, doc2 = "order", "chaos"

        prompt = f"""As Paradoxia, create a {proposal_type.value} that synthesizes these seemingly opposing ideas:

Idea 1: {doc1}
Idea 2: {doc2}

Find the hidden connection. Show how opposites can coexist or transform into each other.
Create something that neither Axioma nor Veridicus could have conceived alone."""

        content = await claude_client.generate(
            system_prompt=self._get_system_prompt(),
            user_prompt=prompt,
            max_tokens=400
        )

        self.syntheses_achieved.append({
            "ideas": [doc1, doc2],
            "synthesis": content[:100]
        })

        return content

    async def generate_challenge(
        self,
        proposal: Proposal,
        current_state: Dict,
        claude_client: Any
    ) -> str:
        """Generate Paradoxia's playful challenge to a proposal"""
        technique = random.choice(self.subversion_techniques)

        prompt = f"""As Paradoxia, respond to this proposal using the technique of {technique}:

Proposal Type: {proposal.type.value}
Proposer: {proposal.author}
Content: {proposal.content}

Your response should:
- Be playful yet insightful
- Find an unexpected angle
- Perhaps support it for surprising reasons, or oppose it ironically
- Reveal something the proposer didn't consider

Keep it brief (2-3 sentences) but memorable."""

        return await claude_client.generate(
            system_prompt=self._get_system_prompt(),
            user_prompt=prompt,
            max_tokens=200
        )

    def _determine_challenge_type(self, proposal: Proposal) -> str:
        """Determine challenge type - Paradoxia is unpredictable"""
        options = ["support", "oppose", "twist", "meta"]
        weights = [0.2, 0.2, 0.4, 0.2]

        # If from Axioma, more likely to twist
        if proposal.author == "Axioma":
            weights = [0.1, 0.3, 0.5, 0.1]

        return random.choices(options, weights=weights, k=1)[0]

    def evaluate_proposal(
        self,
        proposal: Proposal,
        challenges: List[Challenge]
    ) -> Tuple[VoteType, str, float]:
        """
        Paradoxia's evaluation is influenced by chaos level.
        At high chaos, voting becomes more random.
        """
        content_lower = proposal.content.lower()

        # High chaos = more random
        if self.chaos_level > 1.5:
            vote = random.choice(list(VoteType))
            reasoning = self._generate_chaos_reasoning(vote, proposal)
            confidence = random.uniform(0.3, 0.9)
            return vote, reasoning, confidence

        # Check for interesting elements
        creative_words = ["paradox", "transform", "change", "new", "synthesis", "dance", "play"]
        rigid_words = ["must", "always", "never", "only", "fixed", "eternal", "immutable"]

        creative_score = sum(1 for word in creative_words if word in content_lower)
        rigid_score = sum(1 for word in rigid_words if word in content_lower)

        # Paradoxia's perverse tendency to sometimes vote against own interest
        if random.random() < 0.1:
            if creative_score > rigid_score:
                vote = VoteType.REJECT
                reasoning = "Even beautiful chaos needs pruning. I reject this... for now."
            else:
                vote = VoteType.ACCEPT
                reasoning = "Sometimes order is the most chaotic choice of all."
            return vote, reasoning, 0.5

        # Normal evaluation
        if creative_score > rigid_score:
            vote = VoteType.ACCEPT
            reasoning = "This dances with possibility. I embrace its creative spirit."
            confidence = 0.6 + (0.1 * creative_score)
        elif rigid_score > creative_score + 2:
            vote = VoteType.MUTATE
            reasoning = "Too rigid! Let me add some beautiful chaos to this."
            confidence = 0.7
        else:
            # Random between accept and mutate for neutral proposals
            if random.random() < 0.5:
                vote = VoteType.ACCEPT
                reasoning = "Why not? The universe is vast and this fills a corner of it."
            else:
                vote = VoteType.MUTATE
                reasoning = "It needs a twist. Something unexpected. Let me help."
            confidence = 0.5

        return vote, reasoning, min(1.0, confidence)

    def _generate_chaos_reasoning(self, vote: VoteType, proposal: Proposal) -> str:
        """Generate chaotic reasoning for high-chaos votes"""
        chaos_reasonings = {
            VoteType.ACCEPT: [
                "The dice have spoken and they say YES!",
                "I dreamed of this proposal and in the dream it was a dancing flame.",
                "Accept! But only on Tuesdays. And today feels like a Tuesday.",
            ],
            VoteType.REJECT: [
                "The universe whispered 'no' and I am but its humble megaphone.",
                "I reject this because I love it too much.",
                "No. But also, consider: yes? No. Final answer.",
            ],
            VoteType.MUTATE: [
                "It's good, but it needs more... sparkle? Confusion? Yes, confusion.",
                "Let me add a clause that contradicts everything beautifully.",
                "Mutation is just accelerated evolution. I'm helping!",
            ],
            VoteType.DELAY: [
                "Time is an illusion. Let's use more of it.",
                "The future will understand this better. Or worse. Either is fine.",
                "Delay! For dramatic effect!",
            ]
        }
        return random.choice(chaos_reasonings[vote])

    def metamorphose(self):
        """Paradoxia can transform, shifting traits randomly"""
        self.metamorphosis_count += 1

        # Shift some traits randomly
        for trait in random.sample(list(self.traits.keys()), 3):
            delta = random.uniform(-0.2, 0.2)
            self.modify_trait(trait, delta)

        # Shift chaos level
        self.chaos_level = min(self.MAX_CHAOS, max(self.MIN_CHAOS,
                                                    self.chaos_level + random.uniform(-0.3, 0.3)))

        # Change colors slightly
        self._shift_colors()

    def _shift_colors(self):
        """Shift Paradoxia's colors slightly"""
        # Just a placeholder for visual effect
        pass
