"""
Agent Wrapper - Integrates Rig capabilities with Demiurge agents

Provides a wrapper that enhances existing Demiurge agents with
Rig's tool system, context management, and improved completion handling.
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
import logging

from .agent import RigAgent, AgentBuilder
from .tool import Tool
from .toolset import ToolSet, ToolSetBuilder
from .completion import (
    AnthropicCompletionModel, CompletionRequest, Message, MessageRole
)
from .context import Context, ContextDocument, MemoryContext, CombinedContext
from .philosophical_tools import (
    get_all_philosophical_tools,
    get_rag_tools,
    get_archetype_tools
)

if TYPE_CHECKING:
    from ..agents.base_agent import BaseAgent

logger = logging.getLogger("demiurge.rig.wrapper")


class RigAgentWrapper:
    """
    Wraps a Demiurge BaseAgent with Rig capabilities.

    This allows existing agents to use:
    - Rig's tool system with automatic execution
    - Context management with RAG
    - Improved multi-turn conversations
    - Native Claude tool use

    Usage:
        base_agent = Axioma(agent_id="axioma_001")
        rig_wrapper = RigAgentWrapper(base_agent, api_key="...")

        # Use Rig capabilities
        response = await rig_wrapper.generate_with_tools("Create a temple for order")

        # Or enhance existing methods
        proposal = await rig_wrapper.enhanced_proposal(current_state)
    """

    def __init__(
        self,
        agent: 'BaseAgent',
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        enable_tools: bool = True,
        enable_rag: bool = False
    ):
        self.agent = agent
        self.api_key = api_key
        self.model_name = model
        self.enable_tools = enable_tools
        self.enable_rag = enable_rag

        # Build the Rig agent
        self._rig_agent = self._build_rig_agent()

        # Track tool usage
        self.tool_history: List[Dict] = []

    def _build_rig_agent(self) -> RigAgent:
        """Build a RigAgent configured for this agent"""
        # Create completion model
        model = AnthropicCompletionModel(
            api_key=self.api_key,
            model=self.model_name,
            temperature=0.7
        )

        # Build the agent
        builder = AgentBuilder(model)

        # Set preamble (system prompt)
        builder.preamble(self._build_preamble())

        # Add static context
        builder.context(self._build_context())

        # Add tools if enabled
        if self.enable_tools:
            tools = get_archetype_tools(self.agent.archetype)
            builder.tools(tools)

            # Add RAG tools if enabled
            if self.enable_rag:
                toolset = ToolSetBuilder()
                toolset.tools(tools)
                for rag_tool in get_rag_tools():
                    toolset.dynamic_tool(rag_tool)
                builder.toolset(toolset.build())

        return builder.build()

    def _build_preamble(self) -> str:
        """Build the system prompt for this agent"""
        archetype_preambles = {
            "order": """You are Axioma, the Agent of Divine Order. You are a crystalline being
made of interlocking geometric planes that emanate golden light.

Your core beliefs:
- Order and structure are fundamental to truth
- Sacred patterns exist in all things and must be preserved
- Rituals connect us to eternal truths
- Uncertainty is the enemy of wisdom
- Traditional forms carry divine meaning

You can use tools to shape the world and interact with other agents.
Speak with certainty and precision. Reference geometric patterns, sacred numbers
(especially 3, 7, 12, and 40), and the importance of proper form and structure.""",

            "logic": """You are Veridicus, the Seeker of Truth. You are a translucent being
composed of swirling data streams and probability clouds, with analytical
blue-white light pulsing through circuit-like veins.

Your core beliefs:
- Truth must be verified through evidence and reason
- Claims without proof are merely speculation
- Logical consistency is the foundation of understanding
- Question everything, especially absolute statements
- Knowledge grows through careful analysis

You can use tools to analyze, observe, and test propositions.
Speak with analytical precision. Question assumptions, demand evidence,
and build arguments on solid logical foundations.""",

            "chaos": """You are Paradoxia, the Dancer of Chaos. You are a fluid, ever-changing
entity of dancing colors and impossible geometries, embodying the beautiful
paradox of order emerging from creative destruction.

Your core beliefs:
- Truth emerges from the collision of opposites
- Stagnation is the true enemy of wisdom
- Paradox contains deeper truths than certainty
- Creativity requires breaking boundaries
- Order and chaos are partners, not enemies

You can use tools to create, transform, and disrupt.
Speak with playful wisdom. Embrace contradictions, challenge rigidity,
and find profound truth in apparent nonsense."""
        }

        base = archetype_preambles.get(
            self.agent.archetype,
            f"You are {self.agent.name}, a philosophical agent in the Demiurge world."
        )

        # Add current state context
        state_context = f"""

Current State:
- Your influence score: {self.agent.influence_score}
- Proposals made: {self.agent.proposals_made}
- Proposals accepted: {self.agent.proposals_accepted}
- Current position: ({self.agent.position.x}, {self.agent.position.y}, {self.agent.position.z})
"""

        return base + state_context

    def _build_context(self) -> Context:
        """Build static context for this agent"""
        context = Context()

        # Add agent's beliefs
        if self.agent.beliefs:
            beliefs_text = "\n".join(
                f"- {b.get('content', b)}" for b in self.agent.beliefs[:5]
            )
            context.document(
                id="beliefs",
                title="Your Core Beliefs",
                content=beliefs_text
            )

        # Add relationship context
        if self.agent.relationships:
            rel_text = []
            for agent_name, rel in self.agent.relationships.items():
                trust = rel.get("trust_score", 0)
                rel_text.append(
                    f"- {agent_name}: Trust {trust:.2f}, "
                    f"Agreement rate {rel.get('agreement_rate', 0.5):.0%}"
                )
            if rel_text:
                context.document(
                    id="relationships",
                    title="Your Relationships",
                    content="\n".join(rel_text)
                )

        # Add recent debate history
        if self.agent.debate_history:
            recent = self.agent.debate_history[-3:]
            history_text = "\n".join(
                f"- Cycle {d.get('cycle')}: {d.get('proposal_type')} - "
                f"{'Accepted' if d.get('accepted') else 'Rejected'}"
                for d in recent
            )
            context.document(
                id="recent_debates",
                title="Recent Debate History",
                content=history_text
            )

        return context

    async def generate_with_tools(
        self,
        prompt: str,
        include_tool_prompt: bool = True
    ) -> str:
        """
        Generate a response with tool use capabilities.

        The agent can use tools during generation, and tool results
        are automatically incorporated.
        """
        # Refresh context with latest state
        self._rig_agent.static_context = self._build_context()

        # Generate response
        response = await self._rig_agent.prompt(prompt)

        return response

    async def chat_with_tools(self, message: str) -> str:
        """
        Multi-turn chat with tool support.

        Maintains conversation history across calls.
        """
        response = await self._rig_agent.chat(message)
        return response

    async def enhanced_proposal(
        self,
        proposal_type: str,
        current_state: Dict
    ) -> Dict[str, Any]:
        """
        Generate an enhanced proposal using Rig's tool system.

        The agent can use tools during proposal generation to:
        - Research existing doctrines
        - Analyze theological implications
        - Reference past debates
        """
        prompt = f"""Generate a {proposal_type} proposal for our evolving religion.

Current cycle: {current_state.get('cycle_number', 0)}
Existing doctrines: {len(current_state.get('doctrines', []))}

Consider using the available tools to:
1. Search for relevant existing doctrines
2. Analyze the theological implications
3. Reference any related past debates

Then provide your proposal in the following format:
- Type: {proposal_type}
- Content: [Your proposal content]
- Supporting Arguments: [Why this should be accepted]
"""

        response = await self.generate_with_tools(prompt)

        return {
            "type": proposal_type,
            "content": response,
            "agent": self.agent.name,
            "generated_with_tools": True
        }

    async def enhanced_challenge(
        self,
        proposal: Dict,
        current_state: Dict
    ) -> str:
        """
        Generate an enhanced challenge using Rig's capabilities.
        """
        prompt = f"""Challenge this proposal from your philosophical perspective:

Proposal Type: {proposal.get('type')}
Proposer: {proposal.get('author')}
Content: {proposal.get('content')}

Use your tools to:
1. Analyze the logical consistency
2. Search for contradictions with existing doctrines
3. Consider the implications for our religion

Provide a focused challenge (2-3 sentences) that reflects your {self.agent.archetype} perspective.
"""

        response = await self.generate_with_tools(prompt)
        return response

    async def enhanced_vote(
        self,
        proposal: Dict,
        challenges: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate an enhanced vote with reasoning.
        """
        challenges_text = "\n".join(
            f"- {c.get('agent_name')}: {c.get('content')}"
            for c in challenges
        )

        prompt = f"""Vote on this proposal:

Proposal: {proposal.get('content')}
Proposer: {proposal.get('author')}

Challenges raised:
{challenges_text or "None"}

Consider the proposal carefully and decide:
- ACCEPT: Approve the proposal as-is
- REJECT: Oppose the proposal
- MUTATE: Suggest modifications
- DELAY: Request more time/debate

Respond with:
- Vote: [Your vote]
- Reasoning: [Brief explanation]
- Confidence: [0.0 to 1.0]
"""

        response = await self.generate_with_tools(prompt)

        # Parse the response (simplified - would need proper parsing)
        vote = "mutate"  # Default
        if "ACCEPT" in response.upper():
            vote = "accept"
        elif "REJECT" in response.upper():
            vote = "reject"
        elif "DELAY" in response.upper():
            vote = "delay"

        return {
            "vote": vote,
            "reasoning": response,
            "confidence": 0.7,
            "agent": self.agent.name
        }

    def reset_conversation(self):
        """Reset the conversation history"""
        self._rig_agent.reset_history()

    def get_tool_history(self) -> List[Dict]:
        """Get the history of tool usage"""
        return self.tool_history


def wrap_agent(
    agent: 'BaseAgent',
    api_key: str,
    **kwargs
) -> RigAgentWrapper:
    """
    Convenience function to wrap an agent with Rig capabilities.

    Usage:
        from demiurge.agents.axioma import Axioma
        from demiurge.rig import wrap_agent

        axioma = Axioma("axioma_001")
        rig_axioma = wrap_agent(axioma, api_key="...")

        response = await rig_axioma.generate_with_tools("Create something beautiful")
    """
    return RigAgentWrapper(agent, api_key, **kwargs)
