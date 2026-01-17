"""
Debate Orchestrator
Manages real-time debate cycles between agents
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from uuid import uuid4

from demiurge.config import settings
from demiurge.agents import Axioma, Veridicus, Paradoxia, BaseAgent
from demiurge.agents.base_agent import Proposal, Challenge, Vote, VoteType, ProposalType
from demiurge.api.websocket import ConnectionManager
from .claude_client import ClaudeClient

logger = logging.getLogger("demiurge.orchestrator")


class DebatePhase(str, Enum):
    """Phases of a debate cycle"""
    IDLE = "idle"
    PROPOSAL = "proposal"
    CHALLENGE = "challenge"
    VOTING = "voting"
    RESULT = "result"
    WORLD_UPDATE = "world_update"


class DebateOrchestrator:
    """
    Orchestrates real-time debates between AI agents.

    Each cycle:
    1. Select proposer (rotating)
    2. Generate proposal
    3. Other agents challenge
    4. All agents vote
    5. Process result and update world
    """

    def __init__(self, connection_manager: ConnectionManager):
        self.ws_manager = connection_manager
        self.claude_client = ClaudeClient()

        # Initialize agents
        self.agents: Dict[str, BaseAgent] = {
            "Axioma": Axioma(agent_id=str(uuid4())),
            "Veridicus": Veridicus(agent_id=str(uuid4())),
            "Paradoxia": Paradoxia(agent_id=str(uuid4()))
        }
        self.agent_order = ["Axioma", "Veridicus", "Paradoxia"]

        # State
        self.cycle_number = 0
        self.current_phase = DebatePhase.IDLE
        self.current_proposal: Optional[Proposal] = None
        self.current_challenges: List[Challenge] = []
        self.current_votes: Dict[str, Vote] = {}
        self.is_running = False

        # Timing (in seconds)
        self.cycle_duration = settings.cycle_duration_seconds
        self.proposal_duration = settings.proposal_phase_seconds
        self.challenge_duration = settings.challenge_phase_seconds
        self.voting_duration = settings.voting_phase_seconds
        self.result_duration = settings.result_phase_seconds

        # World state
        self.doctrines: List[Dict] = []
        self.structures: List[Dict] = []

    async def start(self):
        """Start the orchestrator loop"""
        self.is_running = True
        logger.info("Debate orchestrator starting...")

        while self.is_running:
            try:
                await self.run_cycle()
            except Exception as e:
                logger.error(f"Error in debate cycle: {e}")
                await asyncio.sleep(5)

    async def stop(self):
        """Stop the orchestrator"""
        self.is_running = False
        logger.info("Debate orchestrator stopped")

    async def run_cycle(self):
        """Run a complete debate cycle"""
        self.cycle_number += 1
        logger.info(f"Starting cycle {self.cycle_number}")

        # Broadcast cycle start
        await self.ws_manager.broadcast_cycle_start(self.cycle_number)

        # Reset state
        self.current_challenges = []
        self.current_votes = {}

        # Get current state for agents
        current_state = self._get_current_state()

        # Phase 1: Proposal
        await self._run_proposal_phase(current_state)

        # Phase 2: Challenges
        await self._run_challenge_phase(current_state)

        # Phase 3: Voting
        await self._run_voting_phase()

        # Phase 4: Result
        outcome = await self._run_result_phase()

        # Phase 5: World Update (if accepted)
        if outcome == "accepted":
            await self._run_world_update_phase()

        # Broadcast cycle end
        await self.ws_manager.broadcast_cycle_end(
            self.cycle_number,
            self._get_cycle_summary()
        )

        # Wait for next cycle
        await asyncio.sleep(2)

    async def _run_proposal_phase(self, current_state: Dict):
        """Run the proposal generation phase"""
        self.current_phase = DebatePhase.PROPOSAL
        await self.ws_manager.broadcast_debate_phase("proposal", {
            "duration": self.proposal_duration
        })

        # Select proposer (rotating)
        proposer_name = self.agent_order[self.cycle_number % len(self.agent_order)]
        proposer = self.agents[proposer_name]

        logger.info(f"Proposer: {proposer_name}")

        # Move proposer to center
        proposer.move_to(0, 0, -5)
        proposer.set_animation("proposing")
        await self.ws_manager.broadcast_agent_update(proposer.to_dict())

        # Generate proposal
        self.current_proposal = await proposer.create_proposal(
            current_state,
            self.claude_client,
            self.cycle_number
        )

        # Broadcast proposal
        await self.ws_manager.broadcast_proposal({
            "id": self.current_proposal.id,
            "type": self.current_proposal.type.value,
            "content": self.current_proposal.content,
            "proposer": proposer_name,
            "proposer_id": proposer.id
        })

        await asyncio.sleep(self.proposal_duration)

    async def _run_challenge_phase(self, current_state: Dict):
        """Run the challenge phase"""
        self.current_phase = DebatePhase.CHALLENGE
        await self.ws_manager.broadcast_debate_phase("challenge", {
            "duration": self.challenge_duration
        })

        # Get challengers (all agents except proposer)
        proposer_name = self.current_proposal.author
        challengers = [
            (name, agent) for name, agent in self.agents.items()
            if name != proposer_name
        ]

        # Generate challenges in parallel
        challenge_tasks = []
        for name, agent in challengers:
            task = agent.challenge(
                self.current_proposal,
                current_state,
                self.claude_client
            )
            challenge_tasks.append((name, task))

        # Wait for all challenges
        for name, task in challenge_tasks:
            try:
                challenge = await task
                self.current_challenges.append(challenge)

                # Move challenger forward
                agent = self.agents[name]
                if name == "Axioma":
                    agent.move_to(-8, 0, -3)
                elif name == "Veridicus":
                    agent.move_to(8, 0, -3)
                else:
                    agent.move_to(0, 0, 8)

                agent.set_animation("challenging")
                await self.ws_manager.broadcast_agent_update(agent.to_dict())

                # Broadcast challenge
                await self.ws_manager.broadcast_challenge({
                    "agent_id": challenge.agent_id,
                    "agent_name": challenge.agent_name,
                    "content": challenge.content,
                    "type": challenge.challenge_type
                })

                await asyncio.sleep(self.challenge_duration / len(challengers))

            except Exception as e:
                logger.error(f"Error generating challenge from {name}: {e}")

    async def _run_voting_phase(self):
        """Run the voting phase"""
        self.current_phase = DebatePhase.VOTING
        await self.ws_manager.broadcast_debate_phase("voting", {
            "duration": self.voting_duration
        })

        # All agents vote
        for name, agent in self.agents.items():
            vote = agent.vote(self.current_proposal, self.current_challenges)
            self.current_votes[name] = vote

            # Animate voting
            agent.set_animation("voting")
            await self.ws_manager.broadcast_agent_update(agent.to_dict())

            # Broadcast vote
            await self.ws_manager.broadcast_vote({
                "agent_id": vote.agent_id,
                "agent_name": vote.agent_name,
                "vote": vote.vote.value,
                "reasoning": vote.reasoning,
                "confidence": vote.confidence
            })

            await asyncio.sleep(self.voting_duration / len(self.agents))

    async def _run_result_phase(self) -> str:
        """Process and announce results"""
        self.current_phase = DebatePhase.RESULT
        await self.ws_manager.broadcast_debate_phase("result", {
            "duration": self.result_duration
        })

        # Count votes
        vote_counts = {
            VoteType.ACCEPT: 0,
            VoteType.REJECT: 0,
            VoteType.MUTATE: 0,
            VoteType.DELAY: 0
        }

        for vote in self.current_votes.values():
            vote_counts[vote.vote] += 1

        # Determine outcome
        if vote_counts[VoteType.ACCEPT] >= 2:
            outcome = "accepted"
        elif vote_counts[VoteType.REJECT] >= 2:
            outcome = "rejected"
        elif vote_counts[VoteType.MUTATE] >= 2:
            outcome = "mutated"
        else:
            outcome = "delayed"

        # Update agent stats and relationships
        proposer = self.agents[self.current_proposal.author]
        proposer.record_proposal_outcome(self.current_proposal, outcome == "accepted")

        # Update relationships based on voting agreement
        for name1, vote1 in self.current_votes.items():
            for name2, vote2 in self.current_votes.items():
                if name1 != name2:
                    agreed = vote1.vote == vote2.vote
                    self.agents[name1].update_relationship(name2, "vote_agreement", agreed)

        # Broadcast result
        await self.ws_manager.broadcast_debate_result({
            "outcome": outcome,
            "vote_counts": {k.value: v for k, v in vote_counts.items()},
            "proposal_id": self.current_proposal.id,
            "proposer": self.current_proposal.author
        })

        # If accepted, add to doctrines
        if outcome == "accepted":
            self.doctrines.append({
                "id": str(uuid4()),
                "content": self.current_proposal.content,
                "type": self.current_proposal.type.value,
                "proposed_by": self.current_proposal.author,
                "accepted_at_cycle": self.cycle_number
            })

        await asyncio.sleep(self.result_duration)
        return outcome

    async def _run_world_update_phase(self):
        """Update world based on accepted proposal"""
        self.current_phase = DebatePhase.WORLD_UPDATE

        # Determine world change based on proposal type
        world_change = self._generate_world_change(self.current_proposal)

        if world_change:
            self.structures.append(world_change)

            # Broadcast structure spawn
            await self.ws_manager.broadcast_structure_spawn(world_change)

        # Move agents back to home positions
        for name, agent in self.agents.items():
            if name == "Axioma":
                agent.move_to(-15, 0, 0)
            elif name == "Veridicus":
                agent.move_to(15, 0, 0)
            else:
                agent.move_to(0, 0, 15)

            agent.set_animation("idle")
            await self.ws_manager.broadcast_agent_update(agent.to_dict())

    def _generate_world_change(self, proposal: Proposal) -> Optional[Dict]:
        """Generate a world structure based on proposal type"""
        import random
        import math

        # Determine structure type
        type_mapping = {
            ProposalType.BELIEF: "floating_symbol",
            ProposalType.RITUAL: "altar",
            ProposalType.DEITY: "temple",
            ProposalType.COMMANDMENT: "obelisk",
            ProposalType.MYTH: "terrain_feature",
            ProposalType.SACRED_TEXT: "library",
            ProposalType.HIERARCHY: "monument",
            ProposalType.SCHISM: "rift"
        }

        structure_type = type_mapping.get(proposal.type, "monument")

        # Find position (spiral outward from center)
        angle = len(self.structures) * 0.618 * 2 * math.pi  # Golden ratio spiral
        distance = 10 + len(self.structures) * 2
        x = math.cos(angle) * distance
        z = math.sin(angle) * distance

        # Get proposer's colors
        proposer = self.agents.get(proposal.author)
        color = proposer.primary_color if proposer else "#FFFFFF"

        return {
            "id": str(uuid4()),
            "structure_type": structure_type,
            "name": f"Monument of Cycle {self.cycle_number}",
            "position": {"x": x, "y": 0, "z": z},
            "rotation_y": random.uniform(0, 360),
            "scale": 1.0,
            "material_preset": "crystal" if proposal.author == "Axioma" else (
                "stone" if proposal.author == "Veridicus" else "ethereal"
            ),
            "primary_color": color,
            "glow_enabled": True,
            "created_by": proposal.author,
            "created_at_cycle": self.cycle_number,
            "associated_doctrine_id": proposal.id
        }

    def _get_current_state(self) -> Dict:
        """Get current state for agent context"""
        return {
            "cycle_number": self.cycle_number,
            "doctrines": [d["content"] for d in self.doctrines[-20:]],  # Last 20
            "structures": len(self.structures),
            "agents": {
                name: {
                    "influence": agent.influence_score,
                    "proposals_accepted": agent.proposals_accepted
                }
                for name, agent in self.agents.items()
            }
        }

    def _get_cycle_summary(self) -> Dict:
        """Get summary of current cycle"""
        return {
            "cycle_number": self.cycle_number,
            "proposal_type": self.current_proposal.type.value if self.current_proposal else None,
            "proposer": self.current_proposal.author if self.current_proposal else None,
            "outcome": "completed",
            "doctrines_count": len(self.doctrines),
            "structures_count": len(self.structures)
        }
