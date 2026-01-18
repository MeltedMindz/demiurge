"""
ToolSet - Aggregation of multiple tools for agent use

Inspired by Rig's ToolSet which combines tools and optional RAG capabilities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging

from .tool import Tool, ToolDefinition, ToolResult, ToolEmbedding

logger = logging.getLogger("demiurge.rig.toolset")


@dataclass
class ToolSetConfig:
    """Configuration for a ToolSet"""
    # Maximum tools to include in prompt (for RAG mode)
    max_tools_in_prompt: int = 10
    # Whether to use RAG for tool selection
    use_rag: bool = False
    # Similarity threshold for RAG tool selection
    rag_threshold: float = 0.5


class ToolSet:
    """
    Collection of tools for agent use.

    Supports both static tools (always available) and
    RAG-enabled tools (selected based on query relevance).

    Inspired by Rig's ToolSet:
    ```rust
    pub struct ToolSet<S: Send + Sync, D: Send + Sync> {
        tools: HashMap<String, Box<dyn ToolDyn<S, D>>>,
        // ...
    }
    ```

    Usage:
        toolset = (ToolSetBuilder()
            .tool(calculator)
            .tool(search_tool)
            .dynamic_tool(code_interpreter, index)
            .build())

        # Get definitions for LLM
        definitions = await toolset.definitions("help me calculate")

        # Execute a tool
        result = await toolset.call("calculator", {"a": 1, "b": 2})
    """

    def __init__(
        self,
        tools: Dict[str, Tool] = None,
        dynamic_tools: Dict[str, ToolEmbedding] = None,
        config: ToolSetConfig = None
    ):
        self.tools = tools or {}
        self.dynamic_tools = dynamic_tools or {}
        self.config = config or ToolSetConfig()
        self._definitions_cache: Dict[str, ToolDefinition] = {}

    async def definitions(self, prompt: str = "") -> List[ToolDefinition]:
        """
        Get tool definitions for the LLM.

        If RAG is enabled, selects relevant tools based on the prompt.
        Otherwise, returns all static tool definitions.
        """
        definitions = []

        # Add all static tools
        for name, tool in self.tools.items():
            if name not in self._definitions_cache:
                self._definitions_cache[name] = await tool.definition(prompt)
            definitions.append(self._definitions_cache[name])

        # Add dynamic tools based on RAG (if enabled)
        if self.config.use_rag and self.dynamic_tools:
            relevant_tools = await self._select_relevant_tools(prompt)
            for name, tool in relevant_tools.items():
                if name not in self._definitions_cache:
                    self._definitions_cache[name] = await tool.definition(prompt)
                definitions.append(self._definitions_cache[name])

        return definitions

    async def _select_relevant_tools(
        self,
        prompt: str
    ) -> Dict[str, ToolEmbedding]:
        """Select relevant dynamic tools based on prompt similarity"""
        # Simple keyword matching for now
        # TODO: Implement proper vector similarity with embedding model
        relevant = {}
        prompt_lower = prompt.lower()

        for name, tool in self.dynamic_tools.items():
            for doc in tool.embedding_docs():
                if any(word in prompt_lower for word in doc.lower().split()):
                    relevant[name] = tool
                    break

        return relevant

    async def call(
        self,
        tool_name: str,
        args: Dict[str, Any]
    ) -> ToolResult:
        """Execute a tool by name with given arguments"""
        # Look in static tools first
        tool = self.tools.get(tool_name)

        # Then check dynamic tools
        if not tool:
            tool = self.dynamic_tools.get(tool_name)

        if not tool:
            logger.error(f"Tool not found: {tool_name}")
            return ToolResult(
                success=False,
                tool_name=tool_name,
                error=f"Tool '{tool_name}' not found"
            )

        return await tool.execute(args)

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name) or self.dynamic_tools.get(name)

    def list_tools(self) -> List[str]:
        """List all available tool names"""
        return list(self.tools.keys()) + list(self.dynamic_tools.keys())

    def to_anthropic_format(self, prompt: str = "") -> List[Dict[str, Any]]:
        """Get tool definitions in Anthropic format"""
        import asyncio

        async def get_defs():
            defs = await self.definitions(prompt)
            return [d.to_anthropic_format() for d in defs]

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, get_defs())
                    return future.result()
            return asyncio.run(get_defs())
        except RuntimeError:
            return asyncio.run(get_defs())


class ToolSetBuilder:
    """
    Builder for constructing ToolSets.

    Inspired by Rig's builder pattern for tool configuration.

    Usage:
        toolset = (ToolSetBuilder()
            .config(ToolSetConfig(use_rag=True))
            .tool(calculator)
            .tool(search)
            .dynamic_tool(code_tool)
            .build())
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._dynamic_tools: Dict[str, ToolEmbedding] = {}
        self._config = ToolSetConfig()

    def config(self, config: ToolSetConfig) -> "ToolSetBuilder":
        """Set the toolset configuration"""
        self._config = config
        return self

    def tool(self, tool: Tool) -> "ToolSetBuilder":
        """Add a static tool"""
        self._tools[tool.name] = tool
        return self

    def tools(self, tools: List[Tool]) -> "ToolSetBuilder":
        """Add multiple static tools"""
        for t in tools:
            self._tools[t.name] = t
        return self

    def dynamic_tool(self, tool: ToolEmbedding) -> "ToolSetBuilder":
        """Add a RAG-enabled dynamic tool"""
        self._dynamic_tools[tool.name] = tool
        return self

    def dynamic_tools(self, tools: List[ToolEmbedding]) -> "ToolSetBuilder":
        """Add multiple dynamic tools"""
        for t in tools:
            self._dynamic_tools[t.name] = t
        return self

    def build(self) -> ToolSet:
        """Build the ToolSet"""
        return ToolSet(
            tools=self._tools,
            dynamic_tools=self._dynamic_tools,
            config=self._config
        )
