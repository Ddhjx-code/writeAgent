from typing import Any, Dict, List, Optional
import asyncio
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import Document
from ..config import Config
from ..novel_types import Chapter
from .base import BaseKnowledgeBase


class LlamaIndexKnowledge(BaseKnowledgeBase):
    """LlamaIndex-based knowledge base implementation for the novel writing system."""

    def __init__(self, config: Config):
        self.config = config
        self.index = None
        self.storage_context = None
        self.query_engine = None
        self.documents_map = {}  # Map for metadata storage

    async def initialize(self):
        """Initialize the LlamaIndex knowledge base with persistent storage."""
        try:
            import os
            storage_dir = self.config.llamaindex_storage_dir

            # Create storage directory if it doesn't exist
            os.makedirs(storage_dir, exist_ok=True)

            # Check if storage already exists
            if os.path.exists(os.path.join(storage_dir, "docstore.json")):
                # Load existing index from storage
                self.storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
                self.index = load_index_from_storage(self.storage_context)
            else:
                # Create new storage context and index from initial data
                self.storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
                # Start with an empty list of documents
                documents = []
                self.index = VectorStoreIndex.from_documents(documents, storage_context=self.storage_context)

            # Create query engine
            retriever = VectorIndexRetriever(index=self.index, similarity_top_k=5)
            self.query_engine = RetrieverQueryEngine.from_args(retriever)
        except ImportError:
            raise ImportError("LlamaIndex is not installed. Please install it using 'pip install llama-index'.")

    async def store_memory(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """Store a memory in the LlamaIndex knowledge base."""
        # Convert value to string if it's not already
        if not isinstance(value, str):
            import json
            value_str = json.dumps(value)
        else:
            value_str = value

        # Create a document with the key as the filename and value as content
        doc = Document(
            text=value_str,
            doc_id=key,
            metadata=metadata or {"type": "memory", "key": key}
        )

        # Insert the node into the index
        self.index.insert(doc)

        # Store metadata in our map as well
        self.documents_map[key] = {"metadata": metadata, "value": value}

        # Persist to storage
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.index.storage_context.persist(persist_dir=self.config.llamaindex_storage_dir)
        )

    async def retrieve_memory(self, key: str, top_k: int = 1) -> List[Any]:
        """Retrieve memories from the LlamaIndex knowledge base."""
        # Since we have specific keys in our map, let's get exact match first
        if key in self.documents_map:
            return [self.documents_map[key]["value"]]

        # If no exact match, search for similar content
        similar_docs = await self.search(key, top_k)
        return [doc.get("text") for doc in similar_docs]

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant information in the LlamaIndex knowledge base."""
        try:
            results = self.index.as_retriever(similarity_top_k=top_k).retrieve(query)
            formatted_results = []
            for node in results:
                formatted_results.append({
                    "text": node.text,
                    "metadata": node.metadata,
                    "score": getattr(node, 'score', 1.0)
                })
            return formatted_results
        except Exception as e:
            # If search fails, return from documents map as fallback
            filtered_results = []
            query_lower = query.lower()
            for key, value_dict in self.documents_map.items():
                if query_lower in key.lower() or query_lower in str(value_dict["value"]).lower():
                    filtered_results.append({
                        "text": str(value_dict["value"]),
                        "metadata": value_dict["metadata"],
                        "score": 1.0,
                        "key": key
                    })
            # Sort by how well the query matches the keys, limit to top_k
            return sorted(filtered_results, key=lambda x: x["score"], reverse=True)[:top_k]

    async def delete_memory(self, key: str):
        """Delete a memory from the LlamaIndex knowledge base."""
        # Remove from documents map
        if key in self.documents_map:
            del self.documents_map[key]

        # For LlamaIndex, we need to create a new index without the specific document
        # This is a simplified approach - for a more detailed approach we'd need to rebuild the index
        # For now, we'll just mark it as deleted in our internal map
        pass  # Actual deletion from VectorStore index would require different approach

    async def get_all_keys(self) -> List[str]:
        """Get all stored memory keys."""  # Use our map since LlamaIndex doesn't have a direct method
        return list(self.documents_map.keys())

    async def clear(self):
        """Clear all memories from the LlamaIndex knowledge base."""
        # For now, reset our maps and create a new empty index
        self.documents_map = {}

        # Create a new empty index
        documents = []
        self.index = VectorStoreIndex.from_documents(documents, storage_context=self.storage_context)

        # Persist the cleared state
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.index.storage_context.persist(persist_dir=self.config.llamaindex_storage_dir)
        )

    async def store_chapter_content(self, chapter: Chapter) -> str:
        """Store chapter content with detailed metadata in the knowledge base."""
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