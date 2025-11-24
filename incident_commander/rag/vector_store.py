import os
import json
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from .embedder import Embedder
from ..config import VECTOR_STORE_PATH


class VectorStore:
    def __init__(self, embedder: Embedder = None, index_path: str = None):
        self.embedder = embedder or Embedder()
        self.index_path = index_path or VECTOR_STORE_PATH
        self.index = None
        self.documents = []
        self.metadata = []
        self.dimension = 384
        self._initialized = False
    
    def is_initialized(self) -> bool:
        return self._initialized and self.index is not None
    
    def initialize(self, documents: List[str], metadata: List[Dict[str, Any]] = None):
        if not documents:
            return
        
        self.documents = documents
        self.metadata = metadata or [{}] * len(documents)
        
        embeddings = self.embedder.embed_batch(documents)
        embeddings_array = np.array(embeddings).astype('float32')
        
        if len(embeddings) > 0:
            self.dimension = len(embeddings[0])
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings_array)
        
        self._initialized = True
    
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]] = None):
        if not self._initialized:
            self.initialize(documents, metadata)
            return
        
        embeddings = self.embedder.embed_batch(documents)
        embeddings_array = np.array(embeddings).astype('float32')
        
        self.index.add(embeddings_array)
        
        self.documents.extend(documents)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(documents))
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.is_initialized():
            return []
        
        query_embedding = self.embedder.embed(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        distances, indices = self.index.search(query_vector, min(top_k, len(self.documents)))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    "content": self.documents[idx],
                    "score": float(1.0 / (1.0 + distances[0][i])),
                    "metadata": self.metadata[idx] if idx < len(self.metadata) else {},
                    "source": self.metadata[idx].get("source", "unknown") if idx < len(self.metadata) else "unknown"
                })
        
        return results
    
    def save(self, path: str = None):
        save_path = path or self.index_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        faiss.write_index(self.index, f"{save_path}.index")
        
        with open(f"{save_path}.docs.pkl", "wb") as f:
            pickle.dump({"documents": self.documents, "metadata": self.metadata}, f)
    
    def load(self, path: str = None) -> bool:
        load_path = path or self.index_path
        
        try:
            if os.path.exists(f"{load_path}.index"):
                self.index = faiss.read_index(f"{load_path}.index")
                
                if os.path.exists(f"{load_path}.docs.pkl"):
                    with open(f"{load_path}.docs.pkl", "rb") as f:
                        data = pickle.load(f)
                        self.documents = data.get("documents", [])
                        self.metadata = data.get("metadata", [])
                
                self.dimension = self.index.d
                self._initialized = True
                return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
        
        return False
