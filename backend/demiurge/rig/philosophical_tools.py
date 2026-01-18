"""
Philosophical Tools for Demiurge Agents

These tools allow agents to interact with the world, reason about doctrines,
manipulate the 3D environment, and influence each other.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import uuid
import logging

from .tool import Tool, ToolDefinition, ToolEmbedding, tool

logger = logging.getLogger("demiurge.rig.tools")


# ============== World Manipulation Tools ==============

@dataclass
class WorldPosition:
    x: float
    y: float
    z: float


@dataclass
class CreateStructureArgs:
    structure_type: str  # temple, monument, altar, obelisk, shrine
    name: str
    position: Optional[Dict[str, float]] = None
    scale: float = 1.0
    doctrine_reference: Optional[str] = None


class CreateStructureTool(Tool[CreateStructureArgs, Dict]):
    """
    Create a structure in the 3D world.

    Agents use this to manifest their beliefs as physical structures.
    """
    name = "create_structure"
    description = "Create a sacred structure in the world to manifest a belief or doctrine"

    def __init__(self, world_state: Any = None):
        self.world_state = world_state

    async def definition(self, prompt: str = "") -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": {
                    "structure_type": {
                        "type": "string",
                        "enum": ["temple", "monument", "altar", "obelisk", "shrine", "archive", "portal"],
                        "description": "The type of structure to create"
                    },
                    "name": {
                        "type": "string",
                        "description": "The sacred name of the structure"
                    },
                    "position": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "z": {"type": "number"}
                        },
                        "description": "World position (optional, will be auto-placed if omitted)"
                    },
                    "scale": {
                        "type": "number",
                        "description": "Size multiplier (default 1.0)"
                    },
                    "doctrine_reference": {
                        "type": "string",
                        "description": "ID of the doctrine this structure represents"
                    }
                },
                "required": ["structure_type", "name"]
            }
        )

    async def call(self, args: Dict[str, Any]) -> Dict[str, Any]:
        structure_id = f"structure_{uuid.uuid4().hex[:8]}"

        # Default position based on structure type
        if "position" not in args or args["position"] is None:
            default_positions = {
                "temple": {"x": -20, "y": 0, "z": 10},
                "monument": {"x": 0, "y": 0, "z": -15},
                "altar": {"x": 10, "y": 0, "z": 10},
                "obelisk": {"x": 15, "y": 0, "z": -5},
                "shrine": {"x": -10, "y": 0, "z": -10},
                "archive": {"x": 20, "y": 0, "z": 0},
                "portal": {"x": 0, "y": 0, "z": 20}
            }
            args["position"] = default_positions.get(
                args["structure_type"],
                {"x": 0, "y": 0, "z": 0}
            )

        result = {
            "id": structure_id,
            "structure_type": args["structure_type"],
            "name": args["name"],
            "position": args["position"],
            "scale": args.get("scale", 1.0),
            "doctrine_reference": args.get("doctrine_reference"),
            "created": True
        }

        logger.info(f"Created structure: {args['name']} ({args['structure_type']})")
        return result


@tool(
    name="create_particle_effect",
    description="Create a particle effect in the world to visualize spiritual energy or emotions"
)
async def create_particle_effect(
    effect_type: str,
    position_x: float = 0,
    position_y: float = 2,
    position_z: float = 0,
    color: str = "#FFD700",
    intensity: float = 1.0,
    duration: Optional[float] = None
) -> Dict[str, Any]:
    """Create a particle effect at the specified position"""
    effect_id = f"effect_{uuid.uuid4().hex[:8]}"

    return {
        "id": effect_id,
        "effect_type": effect_type,
        "position": {"x": position_x, "y": position_y, "z": position_z},
        "color": color,
        "intensity": intensity,
        "duration": duration,
        "created": True
    }


@tool(
    name="modify_terrain",
    description="Modify the terrain to reflect theological changes - raise mountains, create valleys, or change textures"
)
async def modify_terrain(
    modification_type: str,
    center_x: float,
    center_z: float,
    radius: float = 10.0,
    intensity: float = 1.0
) -> Dict[str, Any]:
    """Modify terrain in the specified area"""
    mod_id = f"terrain_mod_{uuid.uuid4().hex[:8]}"

    valid_types = ["elevation", "depression", "plateau", "texture_sacred", "texture_chaotic"]
    if modification_type not in valid_types:
        modification_type = "elevation"

    return {
        "id": mod_id,
        "modification_type": modification_type,
        "center": {"x": center_x, "z": center_z},
        "radius": radius,
        "intensity": intensity,
        "applied": True
    }


# ============== Reasoning Tools ==============

@tool(
    name="analyze_doctrine",
    description="Analyze a doctrine or belief for logical consistency, theological implications, and alignment with agent's philosophy"
)
async def analyze_doctrine(
    doctrine_content: str,
    analysis_type: str = "full"
) -> Dict[str, Any]:
    """
    Analyze a doctrine.

    Analysis types:
    - logical: Check for internal contradictions
    - theological: Examine religious implications
    - compatibility: Check alignment with existing doctrines
    - full: All of the above
    """
    analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"

    # This would be enhanced by actually calling Claude for analysis
    return {
        "id": analysis_id,
        "doctrine_preview": doctrine_content[:100] + "..." if len(doctrine_content) > 100 else doctrine_content,
        "analysis_type": analysis_type,
        "status": "analyzed",
        "requires_further_review": True
    }


@tool(
    name="recall_memory",
    description="Search through memories of past debates, interactions, and events"
)
async def recall_memory(
    query: str,
    memory_type: str = "all",
    limit: int = 5
) -> Dict[str, Any]:
    """
    Search agent's memories.

    Memory types:
    - debate: Past debate outcomes
    - interaction: Conversations with agents/users
    - doctrine: Accepted/rejected doctrines
    - all: Search all memory types
    """
    return {
        "query": query,
        "memory_type": memory_type,
        "results_count": 0,  # Would be populated from actual memory
        "results": [],
        "status": "searched"
    }


@tool(
    name="propose_doctrine",
    description="Formally propose a new doctrine for the religion"
)
async def propose_doctrine(
    doctrine_type: str,
    content: str,
    supporting_arguments: List[str] = None
) -> Dict[str, Any]:
    """
    Propose a new doctrine.

    Doctrine types: belief, ritual, deity, commandment, myth, sacred_text, hierarchy
    """
    proposal_id = f"proposal_{uuid.uuid4().hex[:8]}"

    valid_types = ["belief", "ritual", "deity", "commandment", "myth", "sacred_text", "hierarchy"]
    if doctrine_type not in valid_types:
        return {"error": f"Invalid doctrine type. Must be one of: {valid_types}"}

    return {
        "id": proposal_id,
        "doctrine_type": doctrine_type,
        "content": content,
        "supporting_arguments": supporting_arguments or [],
        "status": "proposed",
        "awaiting_debate": True
    }


# ============== Social/Influence Tools ==============

@tool(
    name="send_message",
    description="Send a message to another agent or broadcast to all"
)
async def send_message(
    recipient: str,
    message: str,
    message_type: str = "statement"
) -> Dict[str, Any]:
    """
    Send a message.

    Recipients: "Axioma", "Veridicus", "Paradoxia", or "all"
    Message types: statement, question, challenge, agreement, observation
    """
    message_id = f"msg_{uuid.uuid4().hex[:8]}"

    return {
        "id": message_id,
        "recipient": recipient,
        "message": message,
        "message_type": message_type,
        "status": "sent"
    }


@tool(
    name="express_emotion",
    description="Express an emotional state visually in the world"
)
async def express_emotion(
    emotion: str,
    intensity: float = 0.5
) -> Dict[str, Any]:
    """
    Express emotion through visual effects.

    Emotions: joy, contemplation, concern, curiosity, certainty, doubt, creativity
    """
    valid_emotions = ["joy", "contemplation", "concern", "curiosity", "certainty", "doubt", "creativity"]

    return {
        "emotion": emotion if emotion in valid_emotions else "neutral",
        "intensity": max(0.0, min(1.0, intensity)),
        "visual_effect": "applied",
        "status": "expressed"
    }


@tool(
    name="form_alliance",
    description="Propose an alliance with another agent on a specific topic or doctrine"
)
async def form_alliance(
    target_agent: str,
    topic: str,
    proposed_terms: str
) -> Dict[str, Any]:
    """Propose an alliance with another agent"""
    alliance_id = f"alliance_{uuid.uuid4().hex[:8]}"

    return {
        "id": alliance_id,
        "target": target_agent,
        "topic": topic,
        "terms": proposed_terms,
        "status": "proposed",
        "awaiting_response": True
    }


# ============== Observation Tools ==============

@tool(
    name="observe_world",
    description="Observe the current state of the world - structures, effects, terrain"
)
async def observe_world(
    focus_area: str = "all"
) -> Dict[str, Any]:
    """
    Observe the world state.

    Focus areas: all, structures, effects, terrain, agents, center
    """
    return {
        "focus_area": focus_area,
        "observation_time": "now",
        "status": "observed",
        "details_available": True
    }


@tool(
    name="observe_agent",
    description="Observe another agent's current state, position, and apparent mood"
)
async def observe_agent(
    agent_name: str
) -> Dict[str, Any]:
    """Observe another agent"""
    valid_agents = ["Axioma", "Veridicus", "Paradoxia"]

    if agent_name not in valid_agents:
        return {"error": f"Unknown agent. Valid agents: {valid_agents}"}

    return {
        "target": agent_name,
        "status": "observed",
        "visible_state": True
    }


# ============== RAG-Enabled Tools ==============

class DoctrineSearchTool(ToolEmbedding[Dict, List[Dict]]):
    """
    Search through existing doctrines using semantic similarity.

    RAG-enabled tool that retrieves relevant doctrines based on query.
    """
    name = "search_doctrines"
    description = "Search through all accepted and proposed doctrines to find relevant ones"

    def __init__(self, doctrine_store: Any = None):
        self.doctrine_store = doctrine_store

    def embedding_docs(self) -> List[str]:
        return [
            "search for doctrines",
            "find religious beliefs",
            "look up rituals",
            "query commandments",
            "find theological texts"
        ]

    def context(self) -> str:
        return "This tool searches through the religion's accepted doctrines and beliefs."

    async def definition(self, prompt: str = "") -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "doctrine_type": {
                        "type": "string",
                        "enum": ["belief", "ritual", "deity", "commandment", "myth", "all"],
                        "description": "Filter by doctrine type"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results"
                    }
                },
                "required": ["query"]
            }
        )

    async def call(self, args: Dict[str, Any]) -> List[Dict]:
        # Would query actual doctrine store
        return [{
            "query": args.get("query"),
            "type_filter": args.get("doctrine_type", "all"),
            "results": [],
            "status": "searched"
        }]


class DebateHistoryTool(ToolEmbedding[Dict, List[Dict]]):
    """
    Search through past debates and their outcomes.

    RAG-enabled tool for learning from debate history.
    """
    name = "search_debates"
    description = "Search through past debates to understand historical outcomes and arguments"

    def __init__(self, debate_store: Any = None):
        self.debate_store = debate_store

    def embedding_docs(self) -> List[str]:
        return [
            "past debates",
            "argument history",
            "vote outcomes",
            "discussion records",
            "theological disputes"
        ]

    def context(self) -> str:
        return "This tool searches through the complete history of theological debates."

    async def definition(self, prompt: str = "") -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for debates"
                    },
                    "proposer": {
                        "type": "string",
                        "description": "Filter by who proposed"
                    },
                    "outcome": {
                        "type": "string",
                        "enum": ["accepted", "rejected", "mutated", "all"],
                        "description": "Filter by outcome"
                    }
                },
                "required": ["query"]
            }
        )

    async def call(self, args: Dict[str, Any]) -> List[Dict]:
        return [{
            "query": args.get("query"),
            "results": [],
            "status": "searched"
        }]


# ============== Tool Collection ==============

def get_all_philosophical_tools() -> List[Tool]:
    """Get all philosophical tools for agent use"""
    return [
        CreateStructureTool(),
        create_particle_effect,
        modify_terrain,
        analyze_doctrine,
        recall_memory,
        propose_doctrine,
        send_message,
        express_emotion,
        form_alliance,
        observe_world,
        observe_agent,
    ]


def get_rag_tools() -> List[ToolEmbedding]:
    """Get all RAG-enabled tools"""
    return [
        DoctrineSearchTool(),
        DebateHistoryTool(),
    ]


def get_archetype_tools(archetype: str) -> List[Tool]:
    """Get tools preferred by each archetype"""
    base_tools = get_all_philosophical_tools()

    # All archetypes get all tools, but this could be used
    # to filter or weight tools for each archetype
    archetype_preferences = {
        "order": ["create_structure", "propose_doctrine", "analyze_doctrine"],
        "logic": ["analyze_doctrine", "recall_memory", "observe_agent"],
        "chaos": ["create_particle_effect", "modify_terrain", "express_emotion"]
    }

    # Return all tools for now - preferences are informational
    return base_tools
