from typing import Dict, List, Optional, Any, Union
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.schema import Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.node_parser import SentenceSplitter
import chromadb
import os
from pydantic import BaseModel, Field


class KnowledgeEntity(BaseModel):
    """Represents an entity in the knowledge base (character, location, concept, etc.)"""
    id: str
    name: str
    type: str  # character, location, concept, event, etc.
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relationships: List[str] = Field(default_factory=list)  # IDs of related entities


class KnowledgeBase:
    """Central knowledge base using LlamaIndex and Chroma for storing and retrieving story elements"""

    def __init__(self, storage_path: str = "./storage", collection_name: str = "story_knowledge"):
        self.storage_path = storage_path
        self.collection_name = collection_name

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)

        # Initialize Chroma client and collection
        self.chroma_client = chromadb.PersistentClient(path=self.storage_path)

        # Create or get existing collection
        try:
            self.chroma_collection = self.chroma_client.get_collection(self.collection_name)
        except:
            self.chroma_collection = self.chroma_client.create_collection(self.collection_name)

        # Initialize vector store
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)

        # Initialize storage context
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        # Initialize index (empty until data is added)
        try:
            self.index = load_index_from_storage(self.storage_context)
        except:
            # If no stored index exists, create a new empty one
            self.index = VectorStoreIndex.from_documents([], storage_context=self.storage_context)

        # Set up document parser
        self.text_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    def add_document(self, document: Union[Document, str], doc_id: Optional[str] = None) -> str:
        """Add a document to the knowledge base"""
        if isinstance(document, str):
            doc = Document(text=document, doc_id=doc_id)
        else:
            doc = document
            if doc_id:
                doc.doc_id = doc_id

        # Insert document to index
        self.index.insert(doc)
        return doc.doc_id if doc.doc_id else str(hash(doc.text))

    def add_entity(self, entity: KnowledgeEntity) -> str:
        """Add an entity (character, location, etc.) to the knowledge base"""
        # Convert entity to document format
        entity_text = f"{entity.name}: {entity.description}\nType: {entity.type}\nMetadata: {entity.metadata}\nRelationships: {', '.join(entity.relationships)}"
        entity_doc = Document(
            text=entity_text,
            doc_id=entity.id,
            metadata={
                "type": "entity",
                "entity_type": entity.type,
                "name": entity.name
            }
        )

        return self.add_document(entity_doc, doc_id=entity.id)

    def query(self, query_str: str, similarity_top_k: int = 5) -> List[Document]:
        """Query the knowledge base for relevant information"""
        query_engine = self.index.as_query_engine(similarity_top_k=similarity_top_k)
        response = query_engine.query(query_str)

        # Convert response to list of documents
        if hasattr(response, 'source_nodes'):
            return [node.node for node in response.source_nodes]
        else:
            # Fallback if response format is different
            return []

    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """Retrieve a specific entity by its ID"""
        try:
            results = self.chroma_collection.get(ids=[entity_id])
            if results and len(results['documents']) > 0:
                # Parse the document to reconstruct the entity
                doc_text = results['documents'][0]
                doc_metadata = results['metadatas'][0] if results['metadatas'] else {}

                # Extract entity information from text (this is simplified)
                lines = doc_text.split('\n')
                name_line = lines[0].split(':', 1)
                name = name_line[0].strip() if len(name_line) > 0 else "Unknown"
                description = name_line[1].strip() if len(name_line) > 1 else ""

                entity_type = doc_metadata.get('entity_type', doc_metadata.get('type', 'unknown'))

                return KnowledgeEntity(
                    id=entity_id,
                    name=name,
                    type=entity_type,
                    description=description,
                    metadata=doc_metadata
                )
        except Exception as e:
            print(f"Error retrieving entity {entity_id}: {e}")
            return None

    def update_entity(self, entity: KnowledgeEntity) -> bool:
        """Update an existing entity in the knowledge base"""
        try:
            # For simplicity, we'll delete and re-add the entity
            self.delete_entity(entity.id)
            self.add_entity(entity)
            return True
        except Exception as e:
            print(f"Error updating entity {entity.id}: {e}")
            return False

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity from the knowledge base"""
        try:
            self.chroma_collection.delete(ids=[entity_id])
            return True
        except Exception as e:
            print(f"Error deleting entity {entity_id}: {e}")
            return False

    def search_entities(self, query: str, entity_type: Optional[str] = None, top_k: int = 10) -> List[KnowledgeEntity]:
        """Search for entities by name or description"""
        filters = None
        if entity_type:
            filters = {"entity_type": entity_type}

        # This is a basic implementation - the actual implementation might need more complex filtering
        query_engine = self.index.as_query_engine(similarity_top_k=top_k)
        response = query_engine.query(query)

        entities = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                entity = self.get_entity(node.node.ref_doc_id)
                if entity:
                    entities.append(entity)

        return entities

    def save(self):
        """Save the index to persistent storage"""
        self.index.storage_context.persist(persist_dir=self.storage_path)

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the knowledge base"""
        try:
            count = self.chroma_collection.count()
            return {
                "total_documents": count,
                "storage_path": self.storage_path
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {"total_documents": 0, "storage_path": self.storage_path}