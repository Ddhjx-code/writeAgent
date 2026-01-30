from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
import os
import json


class KnowledgeEntity(BaseModel):
    """Represents an entity in the knowledge base (character, location, concept, etc.)"""
    id: str
    name: str
    type: str  # character, location, concept, event, etc.
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relationships: List[str] = Field(default_factory=list)  # IDs of related entities


class KnowledgeBase:
    """Minimal knowledge base using local file storage instead of LlamaIndex"""

    def __init__(self, storage_path: str = "./storage", collection_name: str = "story_knowledge"):
        self.storage_path = storage_path
        self.collection_name = collection_name
        self.entities: Dict[str, KnowledgeEntity] = {}
        self.documents: Dict[str, str] = {}

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)

    def add_document(self, document: Union[str, Any], doc_id: Optional[str] = None) -> str:
        """Add a document to the knowledge base"""
        if isinstance(document, str):
            text = document
        else:
            text = str(document)

        # Generate ID if not provided
        if not doc_id:
            doc_id = f"doc_{len(self.documents) + 1}"

        self.documents[doc_id] = text
        return doc_id

    def add_entity(self, entity: KnowledgeEntity) -> str:
        """Add an entity (character, location, etc.) to the knowledge base"""
        self.entities[entity.id] = entity
        entity_doc = f"{entity.name}: {entity.description}\nType: {entity.type}\nMetadata: {entity.metadata}"
        self.add_document(entity_doc, doc_id=entity.id)
        return entity.id

    def query(self, query_str: str, similarity_top_k: int = 5) -> List:
        """Minimal query implementation"""
        results = []
        query_lower = query_str.lower()

        # Simple text-based search
        for doc_id, content in self.documents.items():
            if query_lower in content.lower():
                # Create a mock Document-like object
                class MockDoc:
                    def __init__(self, doc_id, content):
                        self.doc_id = doc_id
                        self.text = content
                results.append(MockDoc(doc_id, content))

        return results[:similarity_top_k]

    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """Retrieve a specific entity by its ID"""
        return self.entities.get(entity_id)

    def update_entity(self, entity: KnowledgeEntity) -> bool:
        """Update an existing entity in the knowledge base"""
        self.entities[entity.id] = entity
        entity_doc = f"{entity.name}: {entity.description}\nType: {entity.type}\nMetadata: {entity.metadata}"
        self.add_document(entity_doc, doc_id=entity.id)
        return True

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity from the knowledge base"""
        if entity_id in self.entities:
            del self.entities[entity_id]
            if entity_id in self.documents:
                del self.documents[entity_id]
            return True
        return False

    def search_entities(self, query: str, entity_type: Optional[str] = None, top_k: int = 10) -> List[KnowledgeEntity]:
        """Search for entities by name or description"""
        results = []
        query_lower = query.lower()

        for entity_id, entity in self.entities.items():
            if query_lower in entity.name.lower() or query_lower in entity.description.lower():
                if entity_type and entity.type != entity_type:
                    continue
                results.append(entity)

        return results[:top_k]

    def save(self):
        """Save the index to persistent storage"""
        data = {
            "entities": {k: v.model_dump() for k, v in self.entities.items()},
            "documents": self.documents
        }
        filepath = os.path.join(self.storage_path, f"{self.collection_name}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, default=str)  # default=str handles datetime serialization

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the knowledge base"""
        return {
            "total_documents": len(self.documents),
            "total_entities": len(self.entities),
            "storage_path": self.storage_path
        }

    def load_from_file(self):
        """Load the knowledge base from file"""
        filepath = os.path.join(self.storage_path, f"{self.collection_name}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.entities = {k: KnowledgeEntity.model_validate(v) for k, v in data.get("entities", {}).items()}
                self.documents = data.get("documents", {})