from typing import Any, Dict, List, Optional
import asyncio
import chromadb
from chromadb.config import Settings
from chromadb.api.types import QueryResult
from ..config import Config
from ..novel_types import Chapter
from .base import BaseKnowledgeBase
from ..llm.embeddings import OllamaEmbeddingProvider


class ChromaDBKnowledge(BaseKnowledgeBase):
    """ChromaDB-based knowledge base implementation for the novel writing system."""

    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self.collection = None
        self.settings = Settings(
            persist_directory=config.chroma_persist_dir,
            is_persistent=True
        )
        self.collection_name = "novel_writing_kb"
        self.embedding_provider = OllamaEmbeddingProvider(config)

    async def initialize(self):
        """Initialize the ChromaDB knowledge base with persistent storage."""
        try:
            # Initialize client with persistent storage
            self.client = chromadb.Client(self.settings)

            # Create or get collection for the novel writing knowledge base
            try:
                self.collection = self.client.get_collection(self.collection_name)
            except:
                self.collection = self.client.create_collection(
                    self.collection_name,
                    metadata={"description": "Knowledge base for novel writing system"}
                )
        except ImportError:
            raise ImportError("ChromaDB is not installed. Please install it using 'pip install chromadb'.")

    async def store_memory(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """Store a memory in the ChromaDB knowledge base."""
        # Convert value to string if it's not already
        if not isinstance(value, str):
            import json
            value_str = json.dumps(value)
        else:
            value_str = value

        # Use the key as the ID and a placeholder for document text
        # ChromaDB requires documents to be strings
        self.collection.add(
            documents=[value_str],
            metadatas=[metadata or {"key": key}],
            ids=[key]
        )

    async def retrieve_memory(self, key: str, top_k: int = 1) -> List[Any]:
        """Retrieve a specific memory by key from the ChromaDB knowledge base."""
        try:
            result = self.collection.get(
                ids=[key],
                include=['documents', 'metadatas']
            )

            if result and result['documents']:
                return result['documents']
            return []
        except:
            return []

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant information in the ChromaDB knowledge base using Ollama embeddings."""
        try:
            # First, try to generate embedding for the query using Ollama
            query_embedding = self.embedding_provider.embed_query(query)

            if query_embedding:
                # If we successfully generated an embedding, use it for search
                result = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    include=['documents', 'metadatas', 'distances']
                )
            else:
                # If embedding generation failed, fall back to text-based search
                result = self.collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    include=['documents', 'metadatas', 'distances']
                )

            formatted_results = []
            if result['documents'] and len(result['documents']) > 0:
                docs = result['documents'][0]  # ChromaDB returns nested lists
                metadatas = result['metadatas'][0] if result['metadatas'] else [{}] * len(docs)
                distances = result['distances'][0] if result['distances'] else [0.0] * len(docs)

                for doc, meta, dist in zip(docs, metadatas, distances):
                    formatted_results.append({
                        "text": doc,
                        "metadata": meta,
                        "distance": dist
                    })

            return formatted_results
        except Exception as e:
            # Fallback if search fails
            return []

    async def delete_memory(self, key: str):
        """Delete a memory from the ChromaDB knowledge base."""
        try:
            # Try to delete by ID
            self.collection.delete(ids=[key])
        except:
            # If deletion fails, it's okay - the ID might not exist
            pass

    async def get_all_keys(self) -> List[str]:
        """Get all stored memory keys from ChromaDB."""
        try:
            result = self.collection.get(
                include=['metadatas', 'ids']
            )
            return result.get('ids', [])
        except:
            return []

    async def clear(self):
        """Clear all memories from the ChromaDB knowledge base."""
        # Drop and recreate the collection to clear all data
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                self.collection_name,
                metadata={"description": "Knowledge base for novel writing system"}
            )
        except:
            # If it doesn't exist yet, just create it
            self.collection = self.client.create_collection(
                self.collection_name,
                metadata={"description": "Knowledge base for novel writing system"}
            )

    async def store_chapter_content(self, chapter: Chapter) -> str:
        """Store chapter content with detailed metadata in the ChromaDB knowledge base."""
        content_summary = f"""
        Chapter {chapter.chapter_number}: {chapter.title}
        Content: {chapter.content}
        Characters mentioned: {', '.join(chapter.characters_mentioned)}
        Locations mentioned: {', '.join(chapter.locations_mentioned)}
        Key plot points: {', '.join(chapter.key_plot_points)}
        """

        metadata = {
            "type": "chapter",
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "characters": chapter.characters_mentioned,
            "locations": chapter.locations_mentioned,
            "plot_points": chapter.key_plot_points
        }

        await self.store_memory(f"chapter_{chapter.chapter_number}", content_summary, metadata)
        return f"chapter_{chapter.chapter_number}"

    async def get_chapter_by_number(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """Get a specific chapter by its number."""
        key = f"chapter_{chapter_number}"
        results = await self.retrieve_memory(key)
        if results:
            return {"content": results[0], "key": key}
        return None

    async def search_by_metadata(self, metadata_filters: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents based on metadata."""
        # ChromaDB allows querying with metadata filters
        # For this implementation, we'll retrieve all documents and filter on our side
        all_docs = await self.collection.get(include=["documents", "metadatas", "ids"])

        filtered_results = []
        for doc, meta, doc_id in zip(all_docs['documents'], all_docs['metadatas'], all_docs['ids']):
            matches_filter = all(
                meta.get(k) == v or (v in meta.get(k, [])) if isinstance(meta.get(k), list) else meta.get(k) == v
                for k, v in metadata_filters.items()
            )

            if matches_filter and len(filtered_results) < top_k:
                filtered_results.append({
                    "id": doc_id,
                    "text": doc,
                    "metadata": meta
                })

        return filtered_results