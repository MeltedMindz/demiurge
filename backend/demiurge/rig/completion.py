"""
Completion Model abstraction for LLM providers

Provides a unified interface for different LLM providers,
inspired by Rig's CompletionModel trait.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterator
from enum import Enum
import logging

logger = logging.getLogger("demiurge.rig.completion")


class MessageRole(str, Enum):
    """Message roles in a conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """A message in a conversation"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    """A tool call request from the model"""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class CompletionRequest:
    """Request for a completion"""
    messages: List[Message]
    system: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None  # "auto", "required", or specific tool name
    max_tokens: int = 2000
    temperature: float = 0.7
    stop_sequences: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResponse:
    """Response from a completion request"""
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    stop_reason: Optional[str] = None
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Optional[Any] = None


class CompletionModel(ABC):
    """
    Abstract base for completion models.

    Inspired by Rig's CompletionModel trait:
    ```rust
    pub trait CompletionModel: Clone + Send + Sync {
        type Response: Send;
        fn completion(
            &self,
            request: CompletionRequest<R>
        ) -> impl Future<Output = Result<CompletionResponse<Self::Response>>>;
    }
    ```
    """

    @abstractmethod
    async def completion(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """Generate a completion for the given request"""
        pass

    @abstractmethod
    async def completion_stream(
        self,
        request: CompletionRequest
    ) -> AsyncIterator[str]:
        """Stream completion tokens"""
        pass


class AnthropicCompletionModel(CompletionModel):
    """Anthropic Claude completion model"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.default_max_tokens = max_tokens
        self.default_temperature = temperature

    async def completion(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """Generate completion using Claude"""
        # Convert messages to Anthropic format
        messages = []
        for msg in request.messages:
            if msg.role == MessageRole.SYSTEM:
                continue  # System is separate
            elif msg.role == MessageRole.TOOL:
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg.tool_call_id,
                            "content": msg.content
                        }
                    ]
                })
            else:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })

        # Build request kwargs
        kwargs = {
            "model": self.model,
            "max_tokens": request.max_tokens or self.default_max_tokens,
            "temperature": request.temperature or self.default_temperature,
            "messages": messages
        }

        if request.system:
            kwargs["system"] = request.system

        if request.tools:
            kwargs["tools"] = request.tools
            if request.tool_choice:
                if request.tool_choice == "required":
                    kwargs["tool_choice"] = {"type": "any"}
                elif request.tool_choice == "auto":
                    kwargs["tool_choice"] = {"type": "auto"}
                else:
                    kwargs["tool_choice"] = {
                        "type": "tool",
                        "name": request.tool_choice
                    }

        try:
            response = await self.client.messages.create(**kwargs)

            # Extract content and tool calls
            content = ""
            tool_calls = []

            for block in response.content:
                if block.type == "text":
                    content += block.text
                elif block.type == "tool_use":
                    tool_calls.append(ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input
                    ))

            return CompletionResponse(
                content=content,
                tool_calls=tool_calls,
                stop_reason=response.stop_reason,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Anthropic completion error: {e}")
            raise

    async def completion_stream(
        self,
        request: CompletionRequest
    ) -> AsyncIterator[str]:
        """Stream completion tokens from Claude"""
        messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in request.messages
            if msg.role != MessageRole.SYSTEM
        ]

        kwargs = {
            "model": self.model,
            "max_tokens": request.max_tokens or self.default_max_tokens,
            "temperature": request.temperature or self.default_temperature,
            "messages": messages
        }

        if request.system:
            kwargs["system"] = request.system

        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text


class OpenAICompletionModel(CompletionModel):
    """OpenAI GPT completion model"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ):
        import openai
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self.default_max_tokens = max_tokens
        self.default_temperature = temperature

    async def completion(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """Generate completion using OpenAI"""
        # Convert messages to OpenAI format
        messages = []
        if request.system:
            messages.append({"role": "system", "content": request.system})

        for msg in request.messages:
            if msg.role == MessageRole.SYSTEM:
                messages.append({"role": "system", "content": msg.content})
            elif msg.role == MessageRole.TOOL:
                messages.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "content": msg.content
                })
            else:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })

        kwargs = {
            "model": self.model,
            "max_tokens": request.max_tokens or self.default_max_tokens,
            "temperature": request.temperature or self.default_temperature,
            "messages": messages
        }

        if request.tools:
            kwargs["tools"] = request.tools
            if request.tool_choice:
                kwargs["tool_choice"] = request.tool_choice

        try:
            response = await self.client.chat.completions.create(**kwargs)

            choice = response.choices[0]
            content = choice.message.content or ""
            tool_calls = []

            if choice.message.tool_calls:
                import json
                for tc in choice.message.tool_calls:
                    tool_calls.append(ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments)
                    ))

            return CompletionResponse(
                content=content,
                tool_calls=tool_calls,
                stop_reason=choice.finish_reason,
                usage={
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                },
                raw_response=response
            )

        except Exception as e:
            logger.error(f"OpenAI completion error: {e}")
            raise

    async def completion_stream(
        self,
        request: CompletionRequest
    ) -> AsyncIterator[str]:
        """Stream completion tokens from OpenAI"""
        messages = []
        if request.system:
            messages.append({"role": "system", "content": request.system})

        for msg in request.messages:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })

        stream = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=request.max_tokens or self.default_max_tokens,
            temperature=request.temperature or self.default_temperature,
            messages=messages,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
