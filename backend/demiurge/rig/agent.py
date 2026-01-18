"""
RigAgent - High-level agent abstraction with tool support

The core agent class that combines an LLM model with prompts,
context, and tools to create intelligent agents.

Inspired by Rig's Agent struct:
```rust
pub struct Agent<M: CompletionModel> {
    model: M,
    preamble: String,
    static_context: Vec<Document>,
    static_tools: Vec<Box<dyn ToolDyn>>,
    dynamic_context: Vec<Box<dyn VectorStoreIndexDyn>>,
    dynamic_tools: Vec<(Box<dyn VectorStoreIndexDyn>, Box<dyn ToolSetDyn>)>,
    // ...
}
```
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterator, Union
import logging
import uuid

from .tool import Tool, ToolResult
from .toolset import ToolSet, ToolSetBuilder
from .completion import (
    CompletionModel, CompletionRequest, CompletionResponse,
    Message, MessageRole, ToolCall
)
from .context import Context, DynamicContext, CombinedContext, ContextDocument

logger = logging.getLogger("demiurge.rig.agent")


@dataclass
class ChatHistory:
    """Manages conversation history for multi-turn chat"""
    messages: List[Message] = field(default_factory=list)
    max_messages: int = 50

    def add_user(self, content: str):
        """Add a user message"""
        self.messages.append(Message(role=MessageRole.USER, content=content))
        self._trim()

    def add_assistant(self, content: str):
        """Add an assistant message"""
        self.messages.append(Message(role=MessageRole.ASSISTANT, content=content))
        self._trim()

    def add_tool_result(self, tool_call_id: str, content: str):
        """Add a tool result message"""
        self.messages.append(Message(
            role=MessageRole.TOOL,
            content=content,
            tool_call_id=tool_call_id
        ))
        self._trim()

    def _trim(self):
        """Keep only recent messages"""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def clear(self):
        """Clear history"""
        self.messages = []


class RigAgent:
    """
    High-level agent that combines an LLM with context and tools.

    Features:
    - System prompt (preamble) configuration
    - Static and dynamic context injection
    - Tool use with automatic execution
    - Multi-turn chat support
    - Streaming support

    Usage:
        agent = (AgentBuilder(model)
            .preamble("You are a helpful assistant.")
            .context(Context().document("rules", "...", "..."))
            .tools([calculator, search])
            .build())

        response = await agent.prompt("What is 2+2?")
        # or
        response = await agent.chat("Hello!")
    """

    def __init__(
        self,
        model: CompletionModel,
        preamble: str = "",
        static_context: Optional[Context] = None,
        dynamic_context: Optional[List[DynamicContext]] = None,
        toolset: Optional[ToolSet] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_tool_iterations: int = 5
    ):
        self.model = model
        self.preamble = preamble
        self.static_context = static_context or Context()
        self.dynamic_context = dynamic_context or []
        self.toolset = toolset
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_tool_iterations = max_tool_iterations

        # Chat state
        self.history = ChatHistory()

        # Combined context manager
        self._context = CombinedContext(
            static=self.static_context,
            dynamic=self.dynamic_context
        )

    async def _build_system_prompt(self, user_input: str = "") -> str:
        """Build the full system prompt with context"""
        parts = []

        # Add preamble
        if self.preamble:
            parts.append(self.preamble)

        # Add context
        context_text = await self._context.get_context(user_input)
        if context_text:
            parts.append("\n" + context_text)

        return "\n\n".join(parts)

    async def prompt(self, user_input: str) -> str:
        """
        Single-turn prompt without chat history.

        Returns the assistant's response.
        """
        system = await self._build_system_prompt(user_input)

        request = CompletionRequest(
            messages=[Message(role=MessageRole.USER, content=user_input)],
            system=system,
            tools=self.toolset.to_anthropic_format(user_input) if self.toolset else None,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        response = await self._execute_with_tools(request)
        return response.content

    async def chat(self, user_input: str) -> str:
        """
        Multi-turn chat with history.

        Returns the assistant's response and updates history.
        """
        self.history.add_user(user_input)

        system = await self._build_system_prompt(user_input)

        request = CompletionRequest(
            messages=list(self.history.messages),
            system=system,
            tools=self.toolset.to_anthropic_format(user_input) if self.toolset else None,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        response = await self._execute_with_tools(request)

        self.history.add_assistant(response.content)
        return response.content

    async def _execute_with_tools(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """
        Execute request with automatic tool handling.

        Will iteratively execute tool calls until the model
        produces a final response.
        """
        current_request = request
        iterations = 0

        while iterations < self.max_tool_iterations:
            response = await self.model.completion(current_request)

            # If no tool calls, we're done
            if not response.tool_calls:
                return response

            # Execute all tool calls
            tool_results = []
            for tool_call in response.tool_calls:
                result = await self._execute_tool(tool_call)
                tool_results.append((tool_call, result))

            # Add assistant message with tool calls and results
            # Build new messages list
            new_messages = list(current_request.messages)

            # Add assistant's response (may contain text + tool calls)
            if response.content:
                new_messages.append(Message(
                    role=MessageRole.ASSISTANT,
                    content=response.content
                ))

            # Add tool results
            for tool_call, result in tool_results:
                new_messages.append(Message(
                    role=MessageRole.TOOL,
                    content=self._format_tool_result(result),
                    tool_call_id=tool_call.id
                ))

            # Update request for next iteration
            current_request = CompletionRequest(
                messages=new_messages,
                system=current_request.system,
                tools=current_request.tools,
                max_tokens=current_request.max_tokens,
                temperature=current_request.temperature
            )

            iterations += 1

        logger.warning(f"Max tool iterations ({self.max_tool_iterations}) reached")
        return response

    async def _execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a single tool call"""
        if not self.toolset:
            return ToolResult(
                success=False,
                tool_name=tool_call.name,
                error="No toolset configured"
            )

        logger.info(f"Executing tool: {tool_call.name} with args: {tool_call.arguments}")
        return await self.toolset.call(tool_call.name, tool_call.arguments)

    def _format_tool_result(self, result: ToolResult) -> str:
        """Format a tool result for the model"""
        if result.success:
            return f"Tool '{result.tool_name}' executed successfully.\nOutput: {result.output}"
        else:
            return f"Tool '{result.tool_name}' failed.\nError: {result.error}"

    async def prompt_stream(self, user_input: str) -> AsyncIterator[str]:
        """Stream a single-turn prompt response"""
        system = await self._build_system_prompt(user_input)

        request = CompletionRequest(
            messages=[Message(role=MessageRole.USER, content=user_input)],
            system=system,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        async for chunk in self.model.completion_stream(request):
            yield chunk

    def reset_history(self):
        """Clear chat history"""
        self.history.clear()

    def add_context(self, doc: ContextDocument):
        """Add a context document"""
        self.static_context.add(doc)


class AgentBuilder:
    """
    Builder pattern for creating RigAgents.

    Inspired by Rig's AgentBuilder:
    ```rust
    impl<M: CompletionModel> AgentBuilder<M> {
        pub fn preamble(mut self, preamble: &str) -> Self;
        pub fn context(mut self, doc: &Document) -> Self;
        pub fn tool(mut self, tool: impl Tool) -> Self;
        pub fn build(self) -> Agent<M>;
    }
    ```

    Usage:
        agent = (AgentBuilder(model)
            .preamble("You are Axioma, the Agent of Divine Order...")
            .context(Context().document(...))
            .tool(world_manipulation_tool)
            .tool(reasoning_tool)
            .temperature(0.8)
            .build())
    """

    def __init__(self, model: CompletionModel):
        self._model = model
        self._preamble = ""
        self._static_context = Context()
        self._dynamic_context: List[DynamicContext] = []
        self._toolset_builder = ToolSetBuilder()
        self._temperature = 0.7
        self._max_tokens = 2000
        self._max_tool_iterations = 5

    def preamble(self, text: str) -> "AgentBuilder":
        """Set the agent's system prompt"""
        self._preamble = text
        return self

    def context(self, context: Context) -> "AgentBuilder":
        """Set static context"""
        self._static_context = context
        return self

    def context_document(
        self,
        id: str,
        title: str,
        content: str,
        **kwargs
    ) -> "AgentBuilder":
        """Add a context document"""
        self._static_context.document(id, title, content, **kwargs)
        return self

    def dynamic_context(self, context: DynamicContext) -> "AgentBuilder":
        """Add a dynamic context source"""
        self._dynamic_context.append(context)
        return self

    def tool(self, tool: Tool) -> "AgentBuilder":
        """Add a tool"""
        self._toolset_builder.tool(tool)
        return self

    def tools(self, tools: List[Tool]) -> "AgentBuilder":
        """Add multiple tools"""
        self._toolset_builder.tools(tools)
        return self

    def toolset(self, toolset: ToolSet) -> "AgentBuilder":
        """Use a pre-built toolset"""
        # Merge with existing
        for name, tool in toolset.tools.items():
            self._toolset_builder.tool(tool)
        for name, tool in toolset.dynamic_tools.items():
            self._toolset_builder.dynamic_tool(tool)
        return self

    def temperature(self, temp: float) -> "AgentBuilder":
        """Set temperature"""
        self._temperature = temp
        return self

    def max_tokens(self, tokens: int) -> "AgentBuilder":
        """Set max tokens"""
        self._max_tokens = tokens
        return self

    def max_tool_iterations(self, iterations: int) -> "AgentBuilder":
        """Set max tool execution iterations"""
        self._max_tool_iterations = iterations
        return self

    def build(self) -> RigAgent:
        """Build the agent"""
        toolset = self._toolset_builder.build()

        return RigAgent(
            model=self._model,
            preamble=self._preamble,
            static_context=self._static_context,
            dynamic_context=self._dynamic_context,
            toolset=toolset if toolset.tools or toolset.dynamic_tools else None,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            max_tool_iterations=self._max_tool_iterations
        )
