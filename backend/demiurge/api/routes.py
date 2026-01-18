"""
REST API Routes for Demiurge
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from demiurge.schemas.agent_schemas import AgentResponse, AgentCreate
from demiurge.schemas.world_schemas import (
    WorldStateResponse,
    StructureResponse,
    WeatherResponse
)
from demiurge.schemas.debate_schemas import DebateResponse, DoctrineResponse
from .chat_manager import chat_manager

router = APIRouter()


# ============== Chat Models ==============

class ChatMessageRequest(BaseModel):
    user_id: str
    agent_id: str
    message: str


class ChatMessageResponse(BaseModel):
    agent_id: str
    agent_name: str
    message: str
    emotional_state: Optional[str] = None


class UserPresenceRequest(BaseModel):
    user_id: str
    username: Optional[str] = None


class AgentConversationRequest(BaseModel):
    initiator_id: str
    target_id: str
    topic: Optional[str] = None


# ============== World State ==============

@router.get("/world", response_model=WorldStateResponse)
async def get_world_state():
    """Get current world state including all structures, effects, and weather"""
    # TODO: Implement with database
    return {
        "cycle_number": 0,
        "agents": [],
        "structures": [],
        "effects": [],
        "weather": {
            "type": "clear",
            "intensity": 0.5
        }
    }


@router.get("/world/structures", response_model=List[StructureResponse])
async def get_structures(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0)
):
    """Get all world structures with pagination"""
    # TODO: Implement
    return []


@router.get("/world/weather", response_model=WeatherResponse)
async def get_weather():
    """Get current weather state"""
    return {
        "type": "clear",
        "intensity": 0.5,
        "parameters": {}
    }


# ============== Agents ==============

@router.get("/agents", response_model=List[AgentResponse])
async def get_agents():
    """Get all agents with their current state"""
    # TODO: Implement with database
    return [
        {
            "id": "axioma-uuid",
            "name": "Axioma",
            "archetype": "order",
            "position": {"x": -10, "y": 0, "z": 0},
            "rotation_y": 0,
            "current_animation": "idle",
            "primary_color": "#FFD700",
            "secondary_color": "#FFFFFF",
            "glow_intensity": 1.0,
            "influence_score": 100
        },
        {
            "id": "veridicus-uuid",
            "name": "Veridicus",
            "archetype": "logic",
            "position": {"x": 10, "y": 0, "z": 0},
            "rotation_y": 0,
            "current_animation": "idle",
            "primary_color": "#4169E1",
            "secondary_color": "#C0C0C0",
            "glow_intensity": 1.0,
            "influence_score": 100
        },
        {
            "id": "paradoxia-uuid",
            "name": "Paradoxia",
            "archetype": "chaos",
            "position": {"x": 0, "y": 0, "z": 10},
            "rotation_y": 0,
            "current_animation": "idle",
            "primary_color": "#FF00FF",
            "secondary_color": "#00FFFF",
            "glow_intensity": 1.5,
            "influence_score": 100
        }
    ]


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get specific agent details"""
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/agents/{agent_id}/beliefs")
async def get_agent_beliefs(agent_id: str):
    """Get agent's current beliefs"""
    # TODO: Implement
    return []


@router.get("/agents/{agent_id}/relationships")
async def get_agent_relationships(agent_id: str):
    """Get agent's relationships with other agents"""
    # TODO: Implement
    return []


@router.get("/agents/{agent_id}/journals")
async def get_agent_journals(agent_id: str, limit: int = 10):
    """Get agent's journal entries"""
    # TODO: Implement
    return []


# ============== Debates ==============

@router.get("/debates", response_model=List[DebateResponse])
async def get_debates(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Get debate history with pagination"""
    # TODO: Implement
    return []


@router.get("/debates/current")
async def get_current_debate():
    """Get current active debate state"""
    # TODO: Implement
    return {
        "cycle_number": 0,
        "phase": "idle",
        "phase_time_remaining": 0,
        "proposal": None,
        "challenges": [],
        "votes": {}
    }


@router.get("/debates/{cycle_number}", response_model=DebateResponse)
async def get_debate(cycle_number: int):
    """Get specific debate by cycle number"""
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Debate not found")


# ============== Doctrines ==============

@router.get("/doctrines", response_model=List[DoctrineResponse])
async def get_doctrines(
    doctrine_type: Optional[str] = None,
    limit: int = Query(50, le=200)
):
    """Get accepted doctrines"""
    # TODO: Implement
    return []


@router.get("/doctrines/{doctrine_id}", response_model=DoctrineResponse)
async def get_doctrine(doctrine_id: str):
    """Get specific doctrine"""
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Doctrine not found")


# ============== Sacred Terms ==============

@router.get("/sacred-terms")
async def get_sacred_terms():
    """Get evolved sacred vocabulary"""
    # TODO: Implement
    return []


# ============== Prophecies ==============

@router.get("/prophecies")
async def get_prophecies(
    status: Optional[str] = None  # pending, fulfilled, failed
):
    """Get prophecies with optional status filter"""
    # TODO: Implement
    return []


# ============== Cycle Snapshots ==============

@router.get("/snapshots/{cycle_number}")
async def get_cycle_snapshot(cycle_number: int):
    """Get full world state snapshot for a specific cycle"""
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Snapshot not found")


@router.get("/snapshots/latest")
async def get_latest_snapshot():
    """Get the most recent cycle snapshot"""
    # TODO: Implement
    return None


# ============== Chat ==============

@router.post("/chat/message", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest):
    """Send a message from a user to an agent"""
    response = await chat_manager.send_user_message(
        user_id=request.user_id,
        agent_id=request.agent_id,
        message=request.message
    )

    if response is None:
        raise HTTPException(status_code=500, detail="Failed to get agent response")

    agent = chat_manager.agents.get(request.agent_id)
    return ChatMessageResponse(
        agent_id=request.agent_id,
        agent_name=agent.name if agent else request.agent_id,
        message=response,
        emotional_state=agent.emotional_state.value if agent and agent.emotional_state else None
    )


@router.post("/chat/user/connect")
async def user_connect(request: UserPresenceRequest):
    """Register a user as present in the world"""
    await chat_manager.user_connected(request.user_id, request.username)
    return {"status": "connected", "user_id": request.user_id}


@router.post("/chat/user/disconnect")
async def user_disconnect(request: UserPresenceRequest):
    """Register a user as leaving the world"""
    await chat_manager.user_disconnected(request.user_id)
    return {"status": "disconnected", "user_id": request.user_id}


@router.get("/chat/users")
async def get_active_users():
    """Get list of active users"""
    return chat_manager.get_active_users()


@router.post("/chat/agent-conversation")
async def start_agent_conversation(request: AgentConversationRequest):
    """Trigger a conversation between two agents"""
    conv_id = await chat_manager.initiate_agent_conversation(
        initiator_id=request.initiator_id,
        target_id=request.target_id,
        topic=request.topic
    )

    if conv_id is None:
        raise HTTPException(status_code=500, detail="Failed to start conversation")

    return {"conversation_id": conv_id}


@router.get("/chat/conversations")
async def get_conversations():
    """Get list of active conversations"""
    return chat_manager.get_active_conversations()


@router.get("/chat/interactions/{agent_id}")
async def get_agent_interactions(agent_id: str, limit: int = Query(10, le=50)):
    """Get recent interactions for an agent"""
    return chat_manager.get_agent_interactions(agent_id, limit)
