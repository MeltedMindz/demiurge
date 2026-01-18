"""
Tool System - Rig-inspired tool definitions for LLM agents

Provides a structured way to define tools that agents can use,
with automatic schema generation and type-safe execution.

Inspired by: https://github.com/0xPlaygrounds/rig
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any, Dict, Generic, List, Optional, Type, TypeVar, Callable,
    get_type_hints, Union
)
from enum import Enum
import json
import inspect
import functools
import logging

logger = logging.getLogger("demiurge.rig.tool")

# Type variables for generic tool definition
TArgs = TypeVar("TArgs")
TOutput = TypeVar("TOutput")


class ToolError(Exception):
    """Base exception for tool errors"""
    pass


class ToolExecutionError(ToolError):
    """Error during tool execution"""
    pass


class ToolValidationError(ToolError):
    """Error validating tool arguments"""
    pass


@dataclass
class ToolDefinition:
    """
    Definition of a tool for LLM consumption.

    Contains the name, description, and JSON schema for parameters.
    This is what gets sent to the LLM to describe available tools.
    """
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_anthropic_format(self) -> Dict[str, Any]:
        """Convert to Anthropic tool use format"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters.get("properties", {}),
                "required": self.parameters.get("required", [])
            }
        }

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


@dataclass
class ToolResult:
    """Result of executing a tool"""
    success: bool
    tool_name: str
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "tool_name": self.tool_name,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata
        }


class Tool(ABC, Generic[TArgs, TOutput]):
    """
    Abstract base class for tools.

    Inspired by Rig's Tool trait:
    ```rust
    pub trait Tool: Send + Sync {
        const NAME: &'static str;
        type Error: std::error::Error + Send + Sync + 'static;
        type Args: for<'a> Deserialize<'a> + Send + Sync;
        type Output: Serialize + Send + Sync;

        fn definition(&self, prompt: String) -> impl Future<Output = ToolDefinition>;
        fn call(&self, args: Self::Args) -> impl Future<Output = Result<Self::Output, Self::Error>>;
    }
    ```

    Usage:
        class Calculator(Tool[CalculatorArgs, int]):
            name = "calculator"
            description = "Performs basic arithmetic"

            async def definition(self) -> ToolDefinition:
                return ToolDefinition(...)

            async def call(self, args: CalculatorArgs) -> int:
                return args.a + args.b
    """

    # Class-level constants (override in subclass)
    name: str = "tool"
    description: str = "A tool"

    # Optional: argument and output types for schema generation
    args_type: Optional[Type[TArgs]] = None
    output_type: Optional[Type[TOutput]] = None

    @abstractmethod
    async def definition(self, prompt: str = "") -> ToolDefinition:
        """
        Generate the tool definition.

        The prompt parameter allows dynamic definition based on context.
        """
        pass

    @abstractmethod
    async def call(self, args: TArgs) -> TOutput:
        """Execute the tool with the given arguments"""
        pass

    async def validate_args(self, args: Dict[str, Any]) -> TArgs:
        """
        Validate and convert raw arguments to the expected type.

        Override this for custom validation logic.
        """
        if self.args_type:
            try:
                # Try to instantiate the args type
                if hasattr(self.args_type, "from_dict"):
                    return self.args_type.from_dict(args)
                elif hasattr(self.args_type, "__dataclass_fields__"):
                    return self.args_type(**args)
                else:
                    return args
            except Exception as e:
                raise ToolValidationError(f"Invalid arguments for {self.name}: {e}")
        return args

    async def execute(self, args: Dict[str, Any]) -> ToolResult:
        """
        Full execution pipeline: validate, call, wrap result.
        """
        try:
            validated_args = await self.validate_args(args)
            output = await self.call(validated_args)
            return ToolResult(
                success=True,
                tool_name=self.name,
                output=output
            )
        except ToolError as e:
            logger.error(f"Tool {self.name} error: {e}")
            return ToolResult(
                success=False,
                tool_name=self.name,
                error=str(e)
            )
        except Exception as e:
            logger.exception(f"Unexpected error in tool {self.name}")
            return ToolResult(
                success=False,
                tool_name=self.name,
                error=f"Unexpected error: {e}"
            )


def _generate_json_schema(func: Callable) -> Dict[str, Any]:
    """Generate JSON schema from function signature"""
    hints = get_type_hints(func)
    sig = inspect.signature(func)

    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue

        param_type = hints.get(param_name, Any)
        schema = _type_to_json_schema(param_type)
        properties[param_name] = schema

        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }


def _type_to_json_schema(python_type: Type) -> Dict[str, Any]:
    """Convert Python type to JSON schema"""
    origin = getattr(python_type, "__origin__", None)

    if python_type is str:
        return {"type": "string"}
    elif python_type is int:
        return {"type": "integer"}
    elif python_type is float:
        return {"type": "number"}
    elif python_type is bool:
        return {"type": "boolean"}
    elif python_type is None or python_type is type(None):
        return {"type": "null"}
    elif origin is list or origin is List:
        args = getattr(python_type, "__args__", (Any,))
        return {
            "type": "array",
            "items": _type_to_json_schema(args[0])
        }
    elif origin is dict or origin is Dict:
        return {"type": "object"}
    elif origin is Union:
        args = getattr(python_type, "__args__", ())
        # Handle Optional (Union with None)
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            schema = _type_to_json_schema(non_none[0])
            schema["nullable"] = True
            return schema
        return {"anyOf": [_type_to_json_schema(a) for a in args]}
    elif isinstance(python_type, type) and issubclass(python_type, Enum):
        return {
            "type": "string",
            "enum": [e.value for e in python_type]
        }
    else:
        return {"type": "string", "description": f"Type: {python_type}"}


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Callable:
    """
    Decorator to easily create a tool from a function.

    Inspired by Rig's #[tool_macro] derive macro.

    Usage:
        @tool(name="add", description="Add two numbers")
        async def add(a: int, b: int) -> int:
            return a + b

        # Or with automatic name/description from docstring:
        @tool()
        async def multiply(a: int, b: int) -> int:
            '''Multiply two numbers together'''
            return a * b
    """
    def decorator(func: Callable) -> "FunctionTool":
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Execute {func.__name__}"

        # Generate schema from function signature
        schema = _generate_json_schema(func)

        class FunctionTool(Tool):
            name = tool_name
            description = tool_description

            async def definition(self, prompt: str = "") -> ToolDefinition:
                return ToolDefinition(
                    name=self.name,
                    description=self.description,
                    parameters=schema
                )

            async def call(self, args: Dict[str, Any]) -> Any:
                if inspect.iscoroutinefunction(func):
                    return await func(**args)
                return func(**args)

        # Create instance and preserve function metadata
        tool_instance = FunctionTool()
        functools.update_wrapper(tool_instance, func)
        tool_instance._original_func = func

        return tool_instance

    return decorator


class ToolEmbedding(Tool[TArgs, TOutput]):
    """
    Tool with embedding support for RAG-based retrieval.

    Inspired by Rig's ToolEmbedding trait that extends Tool
    for vector store integration.

    Usage:
        class SearchTool(ToolEmbedding[SearchArgs, SearchResult]):
            name = "search"
            description = "Search the knowledge base"

            def embedding_docs(self) -> List[str]:
                return [
                    "search for information",
                    "find documents",
                    "query knowledge base"
                ]
    """

    @abstractmethod
    def embedding_docs(self) -> List[str]:
        """
        Return documents to embed for this tool.

        These documents are used to determine tool relevance
        based on the user's query.
        """
        pass

    def context(self) -> str:
        """
        Return additional context about the tool.

        This is injected into the prompt when the tool is selected.
        """
        return ""
