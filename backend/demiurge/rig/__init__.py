"""
Rig - Rust-inspired LLM Agent Framework for Python

Ported from https://github.com/0xPlaygrounds/rig

This module provides a powerful, ergonomic framework for building LLM-powered agents
with tools, RAG capabilities, and multi-turn conversations.

Key Components:
- Tool: Base class for defining agent tools
- ToolSet: Collection of tools for an agent
- RigAgent: High-level agent abstraction with tool support
- AgentBuilder: Builder pattern for configuring agents
- RigAgentWrapper: Wrapper for existing Demiurge agents
- Philosophical Tools: World manipulation, reasoning, social tools

Usage:
    from demiurge.rig import RigAgent, AgentBuilder, tool, wrap_agent

    # Create a tool
    @tool(name="greet", description="Say hello")
    async def greet(name: str) -> str:
        return f"Hello, {name}!"

    # Build an agent
    agent = (AgentBuilder(model)
        .preamble("You are a helpful assistant.")
        .tool(greet)
        .build())

    # Use the agent
    response = await agent.prompt("Say hi to Claude")

    # Or wrap an existing Demiurge agent
    from demiurge.agents.axioma import Axioma
    axioma = Axioma("axioma_001")
    rig_axioma = wrap_agent(axioma, api_key="...")
    response = await rig_axioma.generate_with_tools("Create a temple")
"""

from .tool import Tool, ToolDefinition, ToolResult, ToolError, ToolEmbedding, tool
from .toolset import ToolSet, ToolSetBuilder, ToolSetConfig
from .agent import RigAgent, AgentBuilder, ChatHistory
from .completion import (
    CompletionModel, CompletionRequest, CompletionResponse,
    AnthropicCompletionModel, OpenAICompletionModel,
    Message, MessageRole, ToolCall
)
from .context import (
    Context, ContextDocument, DynamicContext,
    FunctionContext, MemoryContext, CombinedContext
)
from .embedding import (
    EmbeddingModel, VectorStore, EmbeddingResult, SearchResult,
    InMemoryVectorStore, KeywordEmbeddingModel
)
from .agent_wrapper import RigAgentWrapper, wrap_agent
from .philosophical_tools import (
    CreateStructureTool,
    DoctrineSearchTool,
    DebateHistoryTool,
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
    get_all_philosophical_tools,
    get_rag_tools,
    get_archetype_tools,
)

__all__ = [
    # Tools
    "Tool",
    "ToolDefinition",
    "ToolResult",
    "ToolError",
    "ToolEmbedding",
    "tool",
    "ToolSet",
    "ToolSetBuilder",
    "ToolSetConfig",

    # Agent
    "RigAgent",
    "AgentBuilder",
    "ChatHistory",
    "RigAgentWrapper",
    "wrap_agent",

    # Completion
    "CompletionModel",
    "CompletionRequest",
    "CompletionResponse",
    "AnthropicCompletionModel",
    "OpenAICompletionModel",
    "Message",
    "MessageRole",
    "ToolCall",

    # Context
    "Context",
    "ContextDocument",
    "DynamicContext",
    "FunctionContext",
    "MemoryContext",
    "CombinedContext",

    # Embedding/RAG
    "EmbeddingModel",
    "VectorStore",
    "EmbeddingResult",
    "SearchResult",
    "InMemoryVectorStore",
    "KeywordEmbeddingModel",

    # Philosophical Tools
    "CreateStructureTool",
    "DoctrineSearchTool",
    "DebateHistoryTool",
    "create_particle_effect",
    "modify_terrain",
    "analyze_doctrine",
    "recall_memory",
    "propose_doctrine",
    "send_message",
    "express_emotion",
    "form_alliance",
    "observe_world",
    "observe_agent",
    "get_all_philosophical_tools",
    "get_rag_tools",
    "get_archetype_tools",
]
