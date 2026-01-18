"""
Claude API Client for Agent Interactions

Enhanced with Rig tool system integration for native tool use.
"""
import logging
from typing import Optional, List, Dict, Any, Callable, Awaitable
import json

import anthropic

from demiurge.config import settings

logger = logging.getLogger("demiurge.claude")


class ClaudeClient:
    """
    Enhanced Claude API client with native tool use support.

    Integrates with the Rig tool system for structured tool execution.
    """

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.claude_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens
        self.temperature = settings.claude_temperature

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from Claude (without tools)"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return response.content[0].text

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Claude: {e}")
            raise

    async def generate_with_tools(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: List[Dict[str, Any]],
        tool_executor: Optional[Callable[[str, Dict], Awaitable[Any]]] = None,
        max_tokens: Optional[int] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Generate a response with native Claude tool use.

        Args:
            system_prompt: System prompt for the agent
            user_prompt: User's message
            tools: List of tool definitions in Anthropic format
            tool_executor: Async function to execute tools: (tool_name, args) -> result
            max_tokens: Maximum tokens for response
            max_iterations: Maximum tool use iterations

        Returns:
            Dict with 'content' (final text), 'tool_calls' (list), 'tool_results' (list)
        """
        messages = [{"role": "user", "content": user_prompt}]
        all_tool_calls = []
        all_tool_results = []

        for iteration in range(max_iterations):
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens or self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=messages,
                    tools=tools
                )

                # Check for tool use
                has_tool_use = any(
                    block.type == "tool_use" for block in response.content
                )

                if not has_tool_use:
                    # No tool use, extract final text and return
                    final_text = ""
                    for block in response.content:
                        if block.type == "text":
                            final_text += block.text

                    return {
                        "content": final_text,
                        "tool_calls": all_tool_calls,
                        "tool_results": all_tool_results,
                        "stop_reason": response.stop_reason
                    }

                # Process tool calls
                assistant_content = []
                tool_results_content = []

                for block in response.content:
                    if block.type == "text":
                        assistant_content.append({
                            "type": "text",
                            "text": block.text
                        })
                    elif block.type == "tool_use":
                        tool_call = {
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        }
                        all_tool_calls.append(tool_call)

                        assistant_content.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })

                        # Execute tool if executor provided
                        if tool_executor:
                            try:
                                result = await tool_executor(block.name, block.input)
                                result_str = json.dumps(result) if isinstance(result, dict) else str(result)
                            except Exception as e:
                                logger.error(f"Tool execution error: {e}")
                                result_str = f"Error executing tool: {e}"
                        else:
                            result_str = json.dumps({"status": "executed", "note": "No executor provided"})

                        all_tool_results.append({
                            "tool_use_id": block.id,
                            "content": result_str
                        })

                        tool_results_content.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_str
                        })

                # Add assistant message and tool results to conversation
                messages.append({"role": "assistant", "content": assistant_content})
                messages.append({"role": "user", "content": tool_results_content})

            except anthropic.APIError as e:
                logger.error(f"Claude API error during tool use: {e}")
                raise

        # Max iterations reached
        logger.warning(f"Max tool iterations ({max_iterations}) reached")
        return {
            "content": "",
            "tool_calls": all_tool_calls,
            "tool_results": all_tool_results,
            "stop_reason": "max_iterations"
        }

    async def generate_proposal(
        self,
        agent_name: str,
        agent_system_prompt: str,
        proposal_prompt: str
    ) -> str:
        """Generate a proposal for an agent"""
        return await self.generate(
            system_prompt=agent_system_prompt,
            user_prompt=proposal_prompt,
            max_tokens=500
        )

    async def generate_challenge(
        self,
        agent_name: str,
        agent_system_prompt: str,
        challenge_prompt: str
    ) -> str:
        """Generate a challenge for an agent"""
        return await self.generate(
            system_prompt=agent_system_prompt,
            user_prompt=challenge_prompt,
            max_tokens=200
        )

    async def generate_vote_reasoning(
        self,
        agent_name: str,
        agent_system_prompt: str,
        vote_prompt: str
    ) -> str:
        """Generate vote reasoning for an agent"""
        return await self.generate(
            system_prompt=agent_system_prompt,
            user_prompt=vote_prompt,
            max_tokens=150
        )

    async def generate_chat_response(
        self,
        agent_name: str,
        agent_system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Callable[[str, Dict], Awaitable[Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a chat response with optional tool use.

        Args:
            agent_name: Name of the responding agent
            agent_system_prompt: Agent's system prompt
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            tools: Optional tool definitions for tool use
            tool_executor: Optional function to execute tools

        Returns:
            Dict with 'content', 'emotional_state', and optionally 'tool_calls'
        """
        # Build messages from history
        messages = []
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": user_message})

        if tools and tool_executor:
            # Use tool-enabled generation
            result = await self.generate_with_tools(
                system_prompt=agent_system_prompt,
                user_prompt=user_message,
                tools=tools,
                tool_executor=tool_executor,
                max_tokens=300
            )

            return {
                "content": result["content"],
                "tool_calls": result.get("tool_calls", []),
                "emotional_state": self._detect_emotion(result["content"])
            }
        else:
            # Simple generation without tools
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    temperature=self.temperature,
                    system=agent_system_prompt,
                    messages=messages
                )

                content = response.content[0].text

                return {
                    "content": content,
                    "emotional_state": self._detect_emotion(content)
                }

            except anthropic.APIError as e:
                logger.error(f"Claude API error: {e}")
                raise

    def _detect_emotion(self, text: str) -> str:
        """Simple emotion detection from response text"""
        text_lower = text.lower()

        if any(w in text_lower for w in ["delighted", "pleased", "wonderful", "excellent"]):
            return "pleased"
        elif any(w in text_lower for w in ["curious", "interesting", "wonder", "fascinating"]):
            return "curious"
        elif any(w in text_lower for w in ["concerned", "worried", "troubling", "disturbing"]):
            return "concerned"
        elif any(w in text_lower for w in ["contemplate", "consider", "reflect", "ponder"]):
            return "contemplative"
        elif any(w in text_lower for w in ["certainly", "absolutely", "undoubtedly"]):
            return "confident"

        return "neutral"


class RigClaudeClient(ClaudeClient):
    """
    Claude client that integrates directly with the Rig tool system.

    Usage:
        from demiurge.rig import ToolSet, ToolSetBuilder, CreateStructureTool

        client = RigClaudeClient()
        toolset = ToolSetBuilder().tool(CreateStructureTool()).build()

        result = await client.generate_with_rig_tools(
            system_prompt="You are Axioma...",
            user_prompt="Create a temple",
            toolset=toolset
        )
    """

    async def generate_with_rig_tools(
        self,
        system_prompt: str,
        user_prompt: str,
        toolset: 'ToolSet',
        max_tokens: Optional[int] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Generate with Rig ToolSet integration.

        Args:
            system_prompt: System prompt
            user_prompt: User message
            toolset: Rig ToolSet with tool definitions
            max_tokens: Max tokens
            max_iterations: Max tool iterations

        Returns:
            Dict with content and tool execution results
        """
        # Get tool definitions from toolset
        tools = toolset.to_anthropic_format(user_prompt)

        # Create tool executor using toolset
        async def executor(name: str, args: Dict) -> Any:
            result = await toolset.call(name, args)
            return result.to_dict()

        return await self.generate_with_tools(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=tools,
            tool_executor=executor,
            max_tokens=max_tokens,
            max_iterations=max_iterations
        )


# Type hint import for ToolSet
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from demiurge.rig import ToolSet
