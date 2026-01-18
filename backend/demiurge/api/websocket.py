"""
WebSocket Handler for Real-time Updates
"""
import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("demiurge.websocket")

router = APIRouter()


class MessageType(str, Enum):
    """WebSocket message types"""
    # Server -> Client
    WORLD_STATE = "world_state"
    AGENT_UPDATE = "agent_update"
    STRUCTURE_SPAWN = "structure_spawn"
    STRUCTURE_REMOVE = "structure_remove"
    EFFECT_SPAWN = "effect_spawn"
    WEATHER_CHANGE = "weather_change"
    DEBATE_PHASE = "debate_phase"
    PROPOSAL = "proposal"
    CHALLENGE = "challenge"
    VOTE = "vote"
    DEBATE_RESULT = "debate_result"
    CYCLE_START = "cycle_start"
    CYCLE_END = "cycle_end"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

    # Chat messages
    CHAT_MESSAGE = "chat_message"           # User message to agent
    CHAT_RESPONSE = "chat_response"         # Agent response to user
    AGENT_CHAT = "agent_chat"               # Agent-to-agent conversation
    AGENT_THOUGHT = "agent_thought"         # Agent's internal thought (broadcast)
    AGENT_ACTION = "agent_action"           # Agent autonomous action
    USER_PRESENCE = "user_presence"         # User joined/left

    # Client -> Server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    REQUEST_STATE = "request_state"
    SEND_CHAT = "send_chat"                 # User sends message to agent


@dataclass
class WSMessage:
    """WebSocket message structure"""
    type: MessageType
    data: Dict[str, Any]
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp
        })


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accept and register new connection"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Remove connection"""
        async with self._lock:
            self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal(self, websocket: WebSocket, message: WSMessage):
        """Send message to specific client"""
        try:
            await websocket.send_text(message.to_json())
        except Exception as e:
            logger.error(f"Error sending to client: {e}")

    async def broadcast(self, message: WSMessage):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return

        disconnected = []
        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_text(message.to_json())
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    disconnected.append(connection)

            # Clean up disconnected clients
            for conn in disconnected:
                self.active_connections.discard(conn)

    # ============== Convenience broadcast methods ==============

    async def broadcast_agent_update(self, agent_data: Dict):
        """Broadcast agent position/state update"""
        await self.broadcast(WSMessage(
            type=MessageType.AGENT_UPDATE,
            data=agent_data
        ))

    async def broadcast_structure_spawn(self, structure_data: Dict):
        """Broadcast new structure creation"""
        await self.broadcast(WSMessage(
            type=MessageType.STRUCTURE_SPAWN,
            data=structure_data
        ))

    async def broadcast_weather_change(self, weather_data: Dict):
        """Broadcast weather state change"""
        await self.broadcast(WSMessage(
            type=MessageType.WEATHER_CHANGE,
            data=weather_data
        ))

    async def broadcast_debate_phase(self, phase: str, data: Dict):
        """Broadcast debate phase change"""
        await self.broadcast(WSMessage(
            type=MessageType.DEBATE_PHASE,
            data={"phase": phase, **data}
        ))

    async def broadcast_proposal(self, proposal_data: Dict):
        """Broadcast new proposal"""
        await self.broadcast(WSMessage(
            type=MessageType.PROPOSAL,
            data=proposal_data
        ))

    async def broadcast_challenge(self, challenge_data: Dict):
        """Broadcast challenge response"""
        await self.broadcast(WSMessage(
            type=MessageType.CHALLENGE,
            data=challenge_data
        ))

    async def broadcast_vote(self, vote_data: Dict):
        """Broadcast vote"""
        await self.broadcast(WSMessage(
            type=MessageType.VOTE,
            data=vote_data
        ))

    async def broadcast_debate_result(self, result_data: Dict):
        """Broadcast debate outcome"""
        await self.broadcast(WSMessage(
            type=MessageType.DEBATE_RESULT,
            data=result_data
        ))

    async def broadcast_cycle_start(self, cycle_number: int):
        """Broadcast cycle start"""
        await self.broadcast(WSMessage(
            type=MessageType.CYCLE_START,
            data={"cycle_number": cycle_number}
        ))

    async def broadcast_cycle_end(self, cycle_number: int, summary: Dict):
        """Broadcast cycle end"""
        await self.broadcast(WSMessage(
            type=MessageType.CYCLE_END,
            data={"cycle_number": cycle_number, "summary": summary}
        ))

    # ============== Chat broadcast methods ==============

    async def broadcast_chat_response(self, agent_id: str, agent_name: str, user_id: str, message: str, emotional_state: str = None):
        """Broadcast agent response to user chat"""
        await self.broadcast(WSMessage(
            type=MessageType.CHAT_RESPONSE,
            data={
                "agent_id": agent_id,
                "agent_name": agent_name,
                "user_id": user_id,
                "message": message,
                "emotional_state": emotional_state
            }
        ))

    async def broadcast_agent_chat(self, from_agent: str, to_agent: str, message: str, conversation_id: str = None):
        """Broadcast agent-to-agent conversation"""
        await self.broadcast(WSMessage(
            type=MessageType.AGENT_CHAT,
            data={
                "from_agent": from_agent,
                "to_agent": to_agent,
                "message": message,
                "conversation_id": conversation_id
            }
        ))

    async def broadcast_agent_thought(self, agent_id: str, agent_name: str, thought: str):
        """Broadcast agent's internal thought"""
        await self.broadcast(WSMessage(
            type=MessageType.AGENT_THOUGHT,
            data={
                "agent_id": agent_id,
                "agent_name": agent_name,
                "thought": thought
            }
        ))

    async def broadcast_agent_action(self, agent_id: str, agent_name: str, action_type: str, target: str = None, content: str = None):
        """Broadcast agent's autonomous action"""
        await self.broadcast(WSMessage(
            type=MessageType.AGENT_ACTION,
            data={
                "agent_id": agent_id,
                "agent_name": agent_name,
                "action_type": action_type,
                "target": target,
                "content": content
            }
        ))

    async def broadcast_user_presence(self, user_id: str, action: str, username: str = None):
        """Broadcast user joined/left"""
        await self.broadcast(WSMessage(
            type=MessageType.USER_PRESENCE,
            data={
                "user_id": user_id,
                "action": action,  # "joined" or "left"
                "username": username
            }
        ))


# Global connection manager instance
ws_manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint"""
    await ws_manager.connect(websocket)
    user_id = None

    try:
        # Send initial world state
        await ws_manager.send_personal(websocket, WSMessage(
            type=MessageType.WORLD_STATE,
            data={
                "message": "Connected to Demiurge",
                "agents": ["Axioma", "Veridicus", "Paradoxia"]
            }
        ))

        while True:
            # Receive and process client messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                msg_data = message.get("data", {})

                if msg_type == MessageType.REQUEST_STATE.value:
                    # Client requesting current state
                    await ws_manager.send_personal(websocket, WSMessage(
                        type=MessageType.WORLD_STATE,
                        data={"message": "State update"}
                    ))

                elif msg_type == MessageType.HEARTBEAT.value:
                    # Respond to heartbeat
                    await ws_manager.send_personal(websocket, WSMessage(
                        type=MessageType.HEARTBEAT,
                        data={"status": "alive"}
                    ))

                elif msg_type == MessageType.SEND_CHAT.value:
                    # User sending chat message to agent
                    from .chat_manager import chat_manager
                    response = await chat_manager.send_user_message(
                        user_id=msg_data.get("user_id", user_id or "anonymous"),
                        agent_id=msg_data.get("agent_id"),
                        message=msg_data.get("message", "")
                    )
                    # Response is broadcast automatically by chat_manager

                elif msg_type == MessageType.USER_PRESENCE.value:
                    # User joining/leaving
                    from .chat_manager import chat_manager
                    action = msg_data.get("action")
                    uid = msg_data.get("user_id")
                    username = msg_data.get("username")

                    if action == "joined":
                        user_id = uid
                        await chat_manager.user_connected(uid, username)
                    elif action == "left":
                        await chat_manager.user_disconnected(uid)

            except json.JSONDecodeError:
                await ws_manager.send_personal(websocket, WSMessage(
                    type=MessageType.ERROR,
                    data={"error": "Invalid JSON"}
                ))

    except WebSocketDisconnect:
        # Clean up user if they had registered
        if user_id:
            from .chat_manager import chat_manager
            await chat_manager.user_disconnected(user_id)
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if user_id:
            from .chat_manager import chat_manager
            await chat_manager.user_disconnected(user_id)
        await ws_manager.disconnect(websocket)


# Export for use in other modules
ws_router = router
