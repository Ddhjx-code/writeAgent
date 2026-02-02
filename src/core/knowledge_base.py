from typing import Dict, List, Optional, Any, Union
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.schema import Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.node_parser import SentenceSplitter
import chromadb
from pydantic import PrivateAttr
from pydantic import BaseModel, Field
import os
from llama_index.llms.openai import OpenAI


class OllamaEmbeddingAdapter(BaseEmbedding):
    """
    Ollama Embedding 适配器，实现 LlamaIndex 的 BaseEmbedding 接口
    """
    model_name: str = "qwen3-embedding:0.6b"
    _ollama_client: Any = PrivateAttr()

    def __init__(self, model_name: str = "qwen3-embedding:0.6b", **kwargs):
        import ollama
        super().__init__(model_name=model_name, **kwargs)
        self._ollama_client = ollama

    def _get_vector(self, text: str) -> List[float]:
        """获取单个文本的向量表示"""
        try:
            response = self._ollama_client.embed(model=self.model_name, input=[text])
            embeddings = response['embeddings']
            return embeddings[0]  # 返回第一个文本的嵌入
        except Exception as e:
            print(f"Ollama embedding error for text '{text[:50]}...': {e}")
            # 返回零向量作为失败时的fallback
            # 尝试使用qwen3-embedding:0.6b模型的典型维度, 这里使用一个常见维度
            return [0.0] * 1024  # 为兼容性设置常见embedding维度

    async def _aget_vector(self, text: str) -> List[float]:
        """异步获取单个文本的向量表示"""
        return self._get_vector(text)

    def _get_text_embedding(self, text: str) -> List[float]:
        """获取文本嵌入"""
        return self._get_vector(text)

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取多个文本的嵌入"""
        try:
            response = self._ollama_client.embed(model=self.model_name, input=texts)
            embeddings = response['embeddings']
            return embeddings
        except Exception as e:
            print(f"Ollama batch embedding error: {e}")
            # 返回零向量作为失败时的fallback
            return [[0.0] * 1024 for _ in texts]  # 假设维度为1024

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """异步获取文本嵌入"""
        return self._get_vector(text)

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """异步获取多个文本嵌入"""
        return self._get_text_embeddings(texts)

    def _get_query_embedding(self, query: str) -> List[float]:
        """获取查询嵌入，通常与文本嵌入相同"""
        return self._get_vector(query)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """异步获取查询嵌入"""
        return self._get_vector(query)


class KnowledgeBase:
    """使用Ollama提供embeddings的中央知识库"""

    def __init__(self, storage_path: str = "./storage", collection_name: str = "story_knowledge",
                 ollama_model: str = "qwen3-embedding:0.6b", openai_api_key: str = None,
                 openai_base_url: str = None):
        self.storage_path = storage_path
        self.collection_name = collection_name
        self.ollama_model = ollama_model

        import os
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)

        # Initialize settings using Ollama for embeddings and OpenAI for LLM
        from llama_index.core import Settings

        # Initialize Ollama embedding adapter
        embed_model = OllamaEmbeddingAdapter(model_name=self.ollama_model)

        # Initialize OpenAI LLM for generation (separate from embeddings)
        # Get API key from parameter or environment variable
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        base_url = openai_base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        if not api_key:
            raise ValueError("OpenAI API key is required for LLM generation. Please provide openai_api_key or set OPENAI_API_KEY environment variable.")

        llm = OpenAI(api_key=api_key, api_base=base_url)

        Settings.embed_model = embed_model
        Settings.llm = llm

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

    def add_entity(self, entity: 'KnowledgeEntity') -> str:
        """Add an entity (character, location, etc.) to the knowledge base"""
        # Convert relationships to string format to ensure compatibility
        relationships_str = ', '.join(str(rel) for rel in entity.relationships)

        # Convert entity to document format
        entity_text = f"{entity.name}: {entity.description}\nType: {entity.type}\nMetadata: {entity.metadata}\nRelationships: {relationships_str}"
        entity_doc = Document(
            text=entity_text,
            doc_id=entity.id,
            metadata={
                "type": "entity",
                "entity_type": entity.type,
                "name": entity.name,
                "relationships": relationships_str  # Convert to string to ensure compatibility
            }
        )

        entity_id = self.add_document(entity_doc, doc_id=entity.id)
        return entity_id

    def query(self, query_str: str, similarity_top_k: int = 5) -> List[Document]:
        """Query the knowledge base"""
        try:
            # Use the retriever directly to avoid LLM dependency issues
            retriever = self.index.as_retriever(similarity_top_k=similarity_top_k)
            nodes = retriever.retrieve(query_str)

            # Process nodes and extract content safely
            result_docs = []
            for i, node in enumerate(nodes):
                if node is not None:
                    try:
                        # Extract content from node with multiple fallback strategies
                        content = None
                        # Try different possible content access methods
                        if hasattr(node, 'get_content'):
                            try:
                                content = node.get_content()
                            except:
                                pass
                        if content is None and hasattr(node, 'text'):
                            content = node.text
                        elif content is None and hasattr(node, 'node_text'):
                            content = node.node_text
                        elif content is None and hasattr(node, 'content'):
                            content = node.content
                        elif content is None and hasattr(node, '_text'):
                            content = node._text
                        elif content is None:
                            # As a last resort, try string representation
                            content = str(node)

                        if content is not None and str(content).strip():
                            # Create document with node content
                            # Try to get the document ID from various possible attributes
                            doc_id = getattr(node, 'doc_id', None)
                            if doc_id is None:
                                doc_id = getattr(node, 'id_', getattr(node, 'ref_doc_id', f"node_{i}"))

                            doc = Document(text=str(content), doc_id=doc_id)
                            result_docs.append(doc)
                    except Exception as node_error:
                        print(f"Error processing node {i}: {node_error}")
                        continue

            return result_docs
        except Exception as e:
            print(f"Query error: {e}")
            import traceback
            traceback.print_exc()  # Show full traceback for debugging
            return []

    def get_entity(self, entity_id: str) -> Optional['KnowledgeEntity']:
        """Retrieve a specific entity by its ID"""
        # This is a simplified implementation - in a real system you would
        # query the index for the specific entity
        try:
            # Query with the entity ID
            results = self.query(entity_id, similarity_top_k=1)
            # Process results to find the entity
            # This is a simplified approach - you'd need more sophisticated logic to extract the entity
            return None
        except:
            return None

    def update_entity(self, entity: 'KnowledgeEntity') -> bool:
        """Update an existing entity in the knowledge base"""
        # Simplified implementation - remove and re-add
        # In a proper implementation you would need upsert capabilities
        try:
            # Delete old version and add new version
            # This is a basic approach - better approaches exist for upserting
            self.add_entity(entity)
            return True
        except Exception as e:
            print(f"Error updating entity {entity.id}: {str(e)}")
            return False

    def delete_entity(self, entity_id: str) -> bool:
        """Not directly supported in this simple chroma vector store implementation"""
        # Chroma doesn't have direct deletion capability in the basic implementation
        # You could implement a flagging-based "soft delete" approach
        print(f"Deletion of entity {entity_id} is not supported in this vector store implementation")
        return False

    def search_entities(self, query: str, entity_type: Optional[str] = None, top_k: int = 10) -> List['KnowledgeEntity']:
        """Search for entities by name or description"""
        # This method would need to be implemented based on entity metadata
        # Simplified for now - just return empty list
        return []

    def save(self):
        """Save the index to persistent storage"""
        # In LlamaIndex with Chroma, changes are generally persistent
        # This is a no-op in this implementation
        pass

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the knowledge base"""
        return {
            "total_documents": len(self.index.docstore.docs) if hasattr(self.index, 'docstore') else 0,
            "storage_path": self.storage_path
        }

    def load_from_file(self):
        """Load the knowledge base from file"""
        # This is handled by the load_index_from_storage in __init__
        pass


class KnowledgeEntity(BaseModel):
    """Represents an entity in the knowledge base (character, location, concept, etc.)"""
    id: str
    name: str
    type: str  # character, location, concept, event, etc.
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relationships: List[str] = Field(default_factory=list)  # IDs of related entities