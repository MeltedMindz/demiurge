"""
Embedding and Vector Store abstractions

Provides interfaces for text embedding and vector similarity search,
enabling RAG (Retrieval Augmented Generation) capabilities.

Inspired by Rig's VectorStore and EmbeddingModel traits.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import logging
import numpy as np

logger = logging.getLogger("demiurge.rig.embedding")


@dataclass
class EmbeddingResult:
    """Result of an embedding operation"""
    text: str
    embedding: List[float]
    model: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Result from a vector search"""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class EmbeddingModel(ABC):
    """
    Abstract base for embedding models.

    Inspired by Rig's EmbeddingModel trait:
    ```rust
    pub trait EmbeddingModel: Clone + Send + Sync {
        fn embed(&self, texts: &[&str]) -> impl Future<Output = Result<Vec<Vec<f64>>>>;
    }
    ```
    """

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        pass

    async def embed_one(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = await self.embed([text])
        return embeddings[0]


class VectorStore(ABC):
    """
    Abstract base for vector stores.

    Inspired by Rig's VectorStoreIndex trait:
    ```rust
    pub trait VectorStoreIndex: Send + Sync {
        fn top_n(&self, query: &str, n: usize) -> impl Future<Output = Result<Vec<Document>>>;
        fn top_n_ids(&self, query: &str, n: usize) -> impl Future<Output = Result<Vec<String>>>;
    }
    ```
    """

    @abstractmethod
    async def add(
        self,
        id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a document to the store"""
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.0
    ) -> List[SearchResult]:
        """Search for similar documents"""
        pass

    @abstractmethod
    async def delete(self, id: str):
        """Delete a document from the store"""
        pass

    async def add_many(
        self,
        documents: List[Tuple[str, str, List[float], Optional[Dict]]]
    ):
        """Add multiple documents"""
        for id, content, embedding, metadata in documents:
            await self.add(id, content, embedding, metadata)


class InMemoryVectorStore(VectorStore):
    """
    Simple in-memory vector store using numpy.

    Good for development and small datasets.
    For production, use a dedicated vector database.
    """

    def __init__(self):
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._embeddings: Dict[str, np.ndarray] = {}

    async def add(
        self,
        id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self._documents[id] = {
            "content": content,
            "metadata": metadata or {}
        }
        self._embeddings[id] = np.array(embedding)

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.0
    ) -> List[SearchResult]:
        if not self._embeddings:
            return []

        query = np.array(query_embedding)

        # Calculate cosine similarity with all documents
        results = []
        for id, embedding in self._embeddings.items():
            score = self._cosine_similarity(query, embedding)
            if score >= threshold:
                doc = self._documents[id]
                results.append(SearchResult(
                    id=id,
                    content=doc["content"],
                    score=float(score),
                    metadata=doc["metadata"]
                ))

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    async def delete(self, id: str):
        self._documents.pop(id, None)
        self._embeddings.pop(id, None)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return np.dot(a, b) / (norm_a * norm_b)


# Optional: Anthropic Voyager embeddings
class VoyagerEmbeddingModel(EmbeddingModel):
    """Anthropic Voyage embeddings (if available)"""

    def __init__(self, api_key: str, model: str = "voyage-2"):
        try:
            import voyageai
            self.client = voyageai.AsyncClient(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("voyageai package required for VoyagerEmbeddingModel")

    async def embed(self, texts: List[str]) -> List[List[float]]:
        result = await self.client.embed(texts, model=self.model)
        return result.embeddings


# Optional: OpenAI embeddings
class OpenAIEmbeddingModel(EmbeddingModel):
    """OpenAI text embeddings"""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("openai package required for OpenAIEmbeddingModel")

    async def embed(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]


# Simple keyword-based "embedding" for testing
class KeywordEmbeddingModel(EmbeddingModel):
    """
    Simple keyword-based embeddings for testing.

    Uses bag-of-words style embeddings without external dependencies.
    """

    def __init__(self, vocabulary_size: int = 1000):
        self.vocab_size = vocabulary_size

    async def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            # Simple hash-based embedding
            words = text.lower().split()
            embedding = [0.0] * self.vocab_size

            for word in words:
                idx = hash(word) % self.vocab_size
                embedding[idx] += 1.0

            # Normalize
            total = sum(embedding)
            if total > 0:
                embedding = [v / total for v in embedding]

            embeddings.append(embedding)

        return embeddings
