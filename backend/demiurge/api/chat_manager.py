"""
Chat Manager for Agent-User and Agent-Agent Communication

Handles routing messages between users and agents, and manages
autonomous agent-to-agent conversations.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from ..agents.base_agent import BaseAgent
    from ..orchestration.claude_client import ClaudeClient

from .websocket import ws_manager, MessageType, WSMessage
from ..agents.autonomy import ActionType, AutonomousAction

logger = logging.getLogger("demiurge.chat")


@dataclass
class ChatUser:
    """Represents a connected user"""
    user_id: str
    username: str
    connected_at: datetime
    last_active: datetime


class ChatManager:
    """
    Manages all chat interactions in the Demiurge world.

    Responsibilities:
    - Route user messages to agents
    - Handle agent responses
    - Manage agent-to-agent conversations
    - Process autonomous agent actions
    - Track active users
    """

    def __init__(self):
        self.agents: Dict[str, 'BaseAgent'] = {}
        self.claude_client: Optional['ClaudeClient'] = None
        self.active_users: Dict[str, ChatUser] = {}
        self.active_conversations: Dict[str, Dict] = {}  # conversation_id -> metadata
        self._autonomy_task: Optional[asyncio.Task] = None
        self._autonomy_running = False

    def register_agents(self, agents: Dict[str, 'BaseAgent']):
        """Register agents that can receive messages"""
        self.agents = agents
        logger.info(f"Registered {len(agents)} agents for chat: {list(agents.keys())}")

    def set_claude_client(self, client: 'ClaudeClient'):
        """Set the Claude client for generating responses"""
        self.claude_client = client

    # ============== User Management ==============

    async def user_connected(self, user_id: str, username: str = None):
        """Handle user connection"""
        self.active_users[user_id] = ChatUser(
            user_id=user_id,
            username=username or f"User_{user_id[:8]}",
            connected_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )

        # Notify agents of new presence
        for agent in self.agents.values():
            agent.update_world_awareness(
                users=list(self.active_users.keys()),
                agents={a.id: a.to_dict() for a in self.agents.values()},
                events=[{"type": "user_joined", "user_id": user_id}]
            )

        # Broadcast user presence
        await ws_manager.broadcast_user_presence(user_id, "joined", username)
        logger.info(f"User {username or user_id} connected")

    async def user_disconnected(self, user_id: str):
        """Handle user disconnection"""
        user = self.active_users.pop(user_id, None)
        if user:
            await ws_manager.broadcast_user_presence(user_id, "left", user.username)
            logger.info(f"User {user.username} disconnected")

    # ============== User-Agent Chat ==============

    async def send_user_message(
        self,
        user_id: str,
        agent_id: str,
        message: str
    ) -> Optional[str]:
        """
        Send a message from a user to an agent.
        Returns the agent's response.
        """
        if agent_id not in self.agents:
            logger.warning(f"Unknown agent: {agent_id}")
            return None

        if not self.claude_client:
            logger.error("Claude client not initialized")
            return None

        agent = self.agents[agent_id]

        # Update user activity
        if user_id in self.active_users:
            self.active_users[user_id].last_active = datetime.utcnow()

        # Broadcast the user's message
        await ws_manager.broadcast(WSMessage(
            type=MessageType.CHAT_MESSAGE,
            data={
                "user_id": user_id,
                "agent_id": agent_id,
                "message": message
            }
        ))

        # Get agent's response
        try:
            response = await agent.receive_user_message(
                user_id=user_id,
                message=message,
                claude_client=self.claude_client
            )

            # Broadcast the response
            await ws_manager.broadcast_chat_response(
                agent_id=agent.id,
                agent_name=agent.name,
                user_id=user_id,
                message=response,
                emotional_state=agent.emotional_state.value if agent.emotional_state else None
            )

            logger.info(f"Chat: {user_id} -> {agent.name}: {message[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error generating agent response: {e}")
            return None

    # ============== Agent-Agent Communication ==============

    async def initiate_agent_conversation(
        self,
        initiator_id: str,
        target_id: str,
        topic: Optional[str] = None
    ) -> Optional[str]:
        """
        Have one agent initiate a conversation with another.
        Returns the conversation ID.
        """
        if initiator_id not in self.agents or target_id not in self.agents:
            return None

        if not self.claude_client:
            return None

        initiator = self.agents[initiator_id]
        target = self.agents[target_id]

        try:
            # Initiator starts conversation
            conv_id, opening = await initiator.initiate_conversation(
                target=target,
                topic=topic,
                claude_client=self.claude_client
            )

            self.active_conversations[conv_id] = {
                "participants": [initiator_id, target_id],
                "topic": topic,
                "started_at": datetime.utcnow().isoformat(),
                "message_count": 1
            }

            # Broadcast the opening
            await ws_manager.broadcast_agent_chat(
                from_agent=initiator.name,
                to_agent=target.name,
                message=opening,
                conversation_id=conv_id
            )

            # Target responds
            response = await target.receive_agent_message(
                from_agent=initiator,
                message=opening,
                claude_client=self.claude_client,
                conversation_id=conv_id
            )

            self.active_conversations[conv_id]["message_count"] += 1

            # Broadcast response
            await ws_manager.broadcast_agent_chat(
                from_agent=target.name,
                to_agent=initiator.name,
                message=response,
                conversation_id=conv_id
            )

            logger.info(f"Agent conversation started: {initiator.name} -> {target.name} on '{topic}'")
            return conv_id

        except Exception as e:
            logger.error(f"Error starting agent conversation: {e}")
            return None

    async def continue_agent_conversation(
        self,
        conversation_id: str,
        speaker_id: str,
        message: str
    ) -> Optional[str]:
        """Continue an existing agent conversation"""
        if conversation_id not in self.active_conversations:
            return None

        conv = self.active_conversations[conversation_id]
        participants = conv["participants"]

        if speaker_id not in participants:
            return None

        # Determine the listener
        listener_id = [p for p in participants if p != speaker_id][0]
        speaker = self.agents.get(speaker_id)
        listener = self.agents.get(listener_id)

        if not speaker or not listener or not self.claude_client:
            return None

        try:
            # Broadcast the message
            await ws_manager.broadcast_agent_chat(
                from_agent=speaker.name,
                to_agent=listener.name,
                message=message,
                conversation_id=conversation_id
            )

            # Get response
            response = await listener.receive_agent_message(
                from_agent=speaker,
                message=message,
                claude_client=self.claude_client,
                conversation_id=conversation_id
            )

            conv["message_count"] += 1

            # Broadcast response
            await ws_manager.broadcast_agent_chat(
                from_agent=listener.name,
                to_agent=speaker.name,
                message=response,
                conversation_id=conversation_id
            )

            return response

        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return None

    # ============== Autonomous Actions ==============

    async def start_autonomy_loop(self, check_interval: float = 5.0):
        """Start the autonomous agent action loop"""
        if self._autonomy_running:
            return

        self._autonomy_running = True
        self._autonomy_task = asyncio.create_task(
            self._autonomy_loop(check_interval)
        )
        logger.info("Started agent autonomy loop")

    async def stop_autonomy_loop(self):
        """Stop the autonomy loop"""
        self._autonomy_running = False
        if self._autonomy_task:
            self._autonomy_task.cancel()
            try:
                await self._autonomy_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped agent autonomy loop")

    async def _autonomy_loop(self, interval: float):
        """Main loop for checking autonomous agent actions"""
        while self._autonomy_running:
            try:
                await self._check_all_agents_for_actions()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in autonomy loop: {e}")
                await asyncio.sleep(interval)

    async def _check_all_agents_for_actions(self):
        """Check each agent for autonomous actions"""
        # Update all agents' awareness
        users = list(self.active_users.keys())
        agent_states = {a.id: a.to_dict() for a in self.agents.values()}

        for agent in self.agents.values():
            agent.update_world_awareness(users, agent_states, [])

        # Check each agent for actions
        for agent in self.agents.values():
            action = agent.check_autonomous_action()
            if action:
                await self._execute_autonomous_action(agent, action)

    async def _execute_autonomous_action(self, agent: 'BaseAgent', action: AutonomousAction):
        """Execute an autonomous action"""
        logger.info(f"Agent {agent.name} taking action: {action.action_type.value}")

        if action.action_type == ActionType.INITIATE_CHAT:
            # Find target
            if action.target and action.target in self.agents:
                await self.initiate_agent_conversation(
                    agent.id,
                    action.target,
                    action.metadata.get("topic")
                )
            elif action.target in self.active_users:
                # Agent initiates chat with user
                thought = f"*{agent.name} turns to address {self.active_users[action.target].username}*"
                await ws_manager.broadcast_agent_thought(agent.id, agent.name, thought)

        elif action.action_type == ActionType.SHARE_THOUGHT:
            # Agent shares a thought publicly
            if action.content:
                await ws_manager.broadcast_agent_thought(agent.id, agent.name, action.content)

        elif action.action_type == ActionType.MAKE_OBSERVATION:
            # Agent makes an observation
            if action.content:
                await ws_manager.broadcast_agent_thought(agent.id, agent.name, action.content)

        elif action.action_type == ActionType.EXPRESS_EMOTION:
            # Agent expresses emotion
            if action.content:
                await ws_manager.broadcast_agent_thought(agent.id, agent.name, action.content)

        # Broadcast the action for UI updates
        await ws_manager.broadcast_agent_action(
            agent_id=agent.id,
            agent_name=agent.name,
            action_type=action.action_type.value,
            target=action.target,
            content=action.content
        )

    # ============== State Access ==============

    def get_active_users(self) -> List[Dict]:
        """Get list of active users"""
        return [
            {
                "user_id": u.user_id,
                "username": u.username,
                "connected_at": u.connected_at.isoformat(),
                "last_active": u.last_active.isoformat()
            }
            for u in self.active_users.values()
        ]

    def get_active_conversations(self) -> List[Dict]:
        """Get list of active conversations"""
        return [
            {"conversation_id": cid, **data}
            for cid, data in self.active_conversations.items()
        ]

    def get_agent_interactions(self, agent_id: str, limit: int = 10) -> List[Dict]:
        """Get recent interactions for an agent"""
        if agent_id not in self.agents:
            return []
        return self.agents[agent_id].get_recent_interactions(limit)


# Global chat manager instance
chat_manager = ChatManager()
