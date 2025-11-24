from typing import List
from sentence_transformers import SentenceTransformer
from ..config import EMBEDDING_MODEL


class Embedder:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or EMBEDDING_MODEL
        self.model = None
    
    def _load_model(self):
        if self.model is None:
            try:
                self.model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"Warning: Could not load embedding model {self.model_name}: {e}")
                print("Using dummy embeddings")
                self.model = None
    
    def embed(self, text: str) -> List[float]:
        self._load_model()
        
        if self.model is None:
            return [0.0] * 384
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Embedding error: {e}")
            return [0.0] * 384
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        
        if self.model is None:
            return [[0.0] * 384] * len(texts)
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            print(f"Batch embedding error: {e}")
            return [[0.0] * 384] * len(texts)
