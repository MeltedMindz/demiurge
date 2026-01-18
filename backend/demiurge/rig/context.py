"""
Context Management for Agents

Provides static and dynamic context injection for agent prompts.
Inspired by Rig's context document system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable, Awaitable
from datetime import datetime
import logging

logger = logging.getLogger("demiurge.rig.context")


@dataclass
class ContextDocument:
    """
    A document that provides context to an agent.

    Can be static (always included) or dynamically retrieved.
    """
    id: str
    title: str
    content: str
    source: Optional[str] = None
    relevance_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_prompt_text(self) -> str:
        """Format document for inclusion in prompt"""
        return f"""### {self.title}
{self.content}
"""


class Context:
    """
    Static context that is always included in agent prompts.

    Usage:
        context = (Context()
            .document("rules", "Core Rules", "...")
            .document("history", "Recent Events", "..."))
    """

    def __init__(self):
        self._documents: List[ContextDocument] = []

    def document(
        self,
        id: str,
        title: str,
        content: str,
        **kwargs
    ) -> "Context":
        """Add a document to the context"""
        self._documents.append(ContextDocument(
            id=id,
            title=title,
            content=content,
            **kwargs
        ))
        return self

    def add(self, doc: ContextDocument) -> "Context":
        """Add a pre-built document"""
        self._documents.append(doc)
        return self

    def documents(self) -> List[ContextDocument]:
        """Get all documents"""
        return self._documents

    def to_prompt_text(self) -> str:
        """Format all documents for prompt inclusion"""
        if not self._documents:
            return ""

        parts = ["## Context\n"]
        for doc in self._documents:
            parts.append(doc.to_prompt_text())

        return "\n".join(parts)


class DynamicContext(ABC):
    """
    Context that is retrieved dynamically based on the query.

    Used for RAG (Retrieval Augmented Generation) where relevant
    documents are fetched based on the user's input.
    """

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        limit: int = 5
    ) -> List[ContextDocument]:
        """Retrieve relevant documents based on query"""
        pass


class FunctionContext(DynamicContext):
    """
    Dynamic context using a custom retrieval function.

    Usage:
        async def get_relevant_docs(query: str, limit: int):
            # Custom retrieval logic
            return [ContextDocument(...), ...]

        context = FunctionContext(get_relevant_docs)
    """

    def __init__(
        self,
        retrieval_fn: Callable[[str, int], Awaitable[List[ContextDocument]]]
    ):
        self._retrieve_fn = retrieval_fn

    async def retrieve(
        self,
        query: str,
        limit: int = 5
    ) -> List[ContextDocument]:
        return await self._retrieve_fn(query, limit)


class MemoryContext(DynamicContext):
    """
    Dynamic context from agent memory.

    Retrieves relevant memories and past interactions
    to provide historical context.
    """

    def __init__(
        self,
        memories: List[Dict[str, Any]],
        relevance_fn: Optional[Callable[[Dict, str], float]] = None
    ):
        self._memories = memories
        self._relevance_fn = relevance_fn or self._default_relevance

    def _default_relevance(self, memory: Dict, query: str) -> float:
        """Simple keyword-based relevance scoring"""
        query_words = set(query.lower().split())
        content = str(memory.get("content", "")).lower()
        content_words = set(content.split())

        overlap = len(query_words & content_words)
        return overlap / max(len(query_words), 1)

    async def retrieve(
        self,
        query: str,
        limit: int = 5
    ) -> List[ContextDocument]:
        # Score all memories
        scored = [
            (memory, self._relevance_fn(memory, query))
            for memory in self._memories
        ]

        # Sort by relevance and take top
        scored.sort(key=lambda x: x[1], reverse=True)
        top_memories = scored[:limit]

        # Convert to documents
        docs = []
        for memory, score in top_memories:
            if score > 0:
                docs.append(ContextDocument(
                    id=memory.get("id", str(hash(str(memory)))),
                    title=memory.get("title", "Memory"),
                    content=str(memory.get("content", "")),
                    relevance_score=score,
                    metadata={"source": "memory"}
                ))

        return docs


class CombinedContext:
    """
    Combines static and dynamic context sources.

    Usage:
        combined = CombinedContext(
            static=Context().document(...),
            dynamic=[memory_context, rag_context]
        )
    """

    def __init__(
        self,
        static: Optional[Context] = None,
        dynamic: Optional[List[DynamicContext]] = None
    ):
        self.static = static or Context()
        self.dynamic = dynamic or []

    async def get_context(
        self,
        query: str = "",
        dynamic_limit: int = 5
    ) -> str:
        """Get combined context text for a prompt"""
        parts = []

        # Add static context
        static_text = self.static.to_prompt_text()
        if static_text:
            parts.append(static_text)

        # Add dynamic context
        if self.dynamic and query:
            all_dynamic_docs = []
            for source in self.dynamic:
                docs = await source.retrieve(query, dynamic_limit)
                all_dynamic_docs.extend(docs)

            # Sort by relevance and deduplicate
            seen_ids = set()
            unique_docs = []
            for doc in sorted(
                all_dynamic_docs,
                key=lambda d: d.relevance_score,
                reverse=True
            ):
                if doc.id not in seen_ids:
                    seen_ids.add(doc.id)
                    unique_docs.append(doc)

            if unique_docs:
                parts.append("\n## Retrieved Context\n")
                for doc in unique_docs[:dynamic_limit]:
                    parts.append(doc.to_prompt_text())

        return "\n".join(parts)
