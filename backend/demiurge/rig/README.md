# Rig - Python LLM Agent Framework

> Inspired by [0xPlaygrounds/rig](https://github.com/0xPlaygrounds/rig), the Rust LLM framework

This module provides a powerful, ergonomic framework for building LLM-powered agents with tools, RAG capabilities, and multi-turn conversations.

## Overview

The Rig module ports the core concepts from the Rust Rig library to Python, specifically designed for the Demiurge philosophical AI agents. It provides:

- **Tool System**: Define tools that agents can use to interact with the world
- **Agent Builder**: Fluent API for constructing agents with prompts, context, and tools
- **RAG Support**: Vector stores and dynamic context retrieval
- **Native Tool Use**: Integration with Claude's native tool use capabilities

## Quick Start

### Creating a Simple Agent

```python
from demiurge.rig import AgentBuilder, AnthropicCompletionModel, tool

# Create a simple tool
@tool(name="greet", description="Greet someone by name")
async def greet(name: str) -> str:
    return f"Hello, {name}! Welcome to the philosophical realm."

# Build an agent
model = AnthropicCompletionModel(api_key="your-api-key")
agent = (AgentBuilder(model)
    .preamble("You are a friendly philosophical guide.")
    .tool(greet)
    .build())

# Use the agent
response = await agent.prompt("Say hello to Socrates")
print(response)  # Will use the greet tool automatically
```

### Wrapping Existing Demiurge Agents

```python
from demiurge.agents.axioma import Axioma
from demiurge.rig import wrap_agent

# Create a Demiurge agent
axioma = Axioma("axioma_001")

# Wrap with Rig capabilities
rig_axioma = wrap_agent(axioma, api_key="your-api-key")

# Now Axioma can use tools
response = await rig_axioma.generate_with_tools(
    "Create a temple to honor the sacred geometry of truth"
)
```

## Components

### Tools

Tools are the core capability that agents can use. Define tools using the `@tool` decorator or by subclassing `Tool`:

```python
from demiurge.rig import tool, Tool, ToolDefinition

# Using decorator
@tool(name="calculate", description="Perform calculations")
async def calculate(expression: str) -> float:
    return eval(expression)  # Don't do this in production!

# Using class
class SearchTool(Tool):
    name = "search"
    description = "Search the knowledge base"

    async def definition(self, prompt: str = "") -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        )

    async def call(self, args: dict) -> list:
        return [{"result": f"Found: {args['query']}"}]
```

### ToolSets

Group tools together for agent use:

```python
from demiurge.rig import ToolSetBuilder, ToolSetConfig

toolset = (ToolSetBuilder()
    .config(ToolSetConfig(use_rag=True))
    .tool(calculate)
    .tool(SearchTool())
    .build())
```

### Context

Provide static and dynamic context to agents:

```python
from demiurge.rig import Context, ContextDocument

context = (Context()
    .document("rules", "Core Rules", "Always speak with wisdom...")
    .document("history", "Recent Events", "In the last cycle..."))
```

### RAG with Vector Stores

Enable semantic search over documents:

```python
from demiurge.rig import InMemoryVectorStore, KeywordEmbeddingModel

# Create embedding model and store
embedder = KeywordEmbeddingModel()
store = InMemoryVectorStore()

# Add documents
embedding = await embedder.embed_one("The nature of truth is complex")
await store.add("doc1", "The nature of truth is complex", embedding)

# Search
query_emb = await embedder.embed_one("What is truth?")
results = await store.search(query_emb, limit=5)
```

## Philosophical Tools

Demiurge-specific tools for agent world interaction:

### World Manipulation
- `create_structure` - Build temples, monuments, altars
- `create_particle_effect` - Visual effects and spiritual energy
- `modify_terrain` - Shape the landscape

### Reasoning
- `analyze_doctrine` - Examine theological consistency
- `recall_memory` - Search past debates and interactions
- `propose_doctrine` - Formally propose new beliefs

### Social
- `send_message` - Communicate with other agents
- `express_emotion` - Visual emotional expression
- `form_alliance` - Propose collaboration

### Observation
- `observe_world` - View current world state
- `observe_agent` - Monitor other agents

## Integration with Claude

### Using RigClaudeClient

```python
from demiurge.orchestration.claude_client import RigClaudeClient
from demiurge.rig import ToolSetBuilder, CreateStructureTool

client = RigClaudeClient()
toolset = ToolSetBuilder().tool(CreateStructureTool()).build()

result = await client.generate_with_rig_tools(
    system_prompt="You are Axioma, the Agent of Divine Order...",
    user_prompt="The time has come to build a monument to truth.",
    toolset=toolset
)

print(result["content"])
print(result["tool_calls"])
```

## Architecture

```
demiurge/rig/
├── __init__.py          # Main exports
├── tool.py              # Tool base class and decorator
├── toolset.py           # ToolSet aggregation
├── agent.py             # RigAgent and AgentBuilder
├── completion.py        # Completion model abstractions
├── context.py           # Static and dynamic context
├── embedding.py         # Vector stores and embeddings
├── agent_wrapper.py     # Wrapper for Demiurge agents
├── philosophical_tools.py # Demiurge-specific tools
└── README.md            # This file
```

## Comparison with Rust Rig

| Rust Rig | Python Rig |
|----------|------------|
| `#[tool_macro]` derive | `@tool` decorator |
| `impl Tool for T` | Subclass `Tool` |
| `AgentBuilder::new()` | `AgentBuilder(model)` |
| `.preamble("...")` | `.preamble("...")` |
| `.tool(t)` | `.tool(t)` |
| `.build()` | `.build()` |
| `agent.prompt("...")` | `await agent.prompt("...")` |

## Resources

- [Original Rig (Rust)](https://github.com/0xPlaygrounds/rig)
- [Rig Documentation](https://docs.rig.rs)
- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
