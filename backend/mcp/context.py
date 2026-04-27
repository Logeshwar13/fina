"""
MCP Context Layer
=================
Manages structured memory and vector storage for RAG.
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import faiss
from pathlib import Path


class ContextLayer:
    """
    Manages context storage and retrieval.
    - Structured memory: Recent transactions, budgets, risk scores
    - Vector memory: Embeddings for semantic search
    """
    
    def __init__(self, dimension: int = 1536, index_path: Optional[str] = None):
        """
        Initialize context layer.
        
        Args:
            dimension: Embedding dimension (1536 for OpenAI text-embedding-3-small)
            index_path: Path to save/load FAISS index
        """
        self.dimension = dimension
        self.index_path = index_path or "backend/mcp/vector_index"
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []  # Store metadata for each vector
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index from disk if it exists."""
        index_file = Path(f"{self.index_path}.index")
        metadata_file = Path(f"{self.index_path}.json")
        
        if index_file.exists() and metadata_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                with open(metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                print(f"[ContextLayer] Loaded index with {self.index.ntotal} vectors")
            except Exception as e:
                print(f"[ContextLayer] Failed to load index: {e}")
    
    def save_index(self):
        """Save FAISS index to disk."""
        try:
            Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, f"{self.index_path}.index")
            with open(f"{self.index_path}.json", 'w') as f:
                json.dump(self.metadata, f)
            print(f"[ContextLayer] Saved index with {self.index.ntotal} vectors")
        except Exception as e:
            print(f"[ContextLayer] Failed to save index: {e}")
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ):
        """
        Add documents to vector store.
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadata: List of metadata dicts (must include 'text')
        """
        if len(texts) != len(embeddings) != len(metadata):
            raise ValueError("texts, embeddings, and metadata must have same length")
        
        # Convert to numpy array
        vectors = np.array(embeddings, dtype=np.float32)
        
        # Add to FAISS index
        self.index.add(vectors)
        
        # Store metadata
        for i, (text, meta) in enumerate(zip(texts, metadata)):
            self.metadata.append({
                **meta,
                "text": text,
                "index": len(self.metadata),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        print(f"[ContextLayer] Added {len(texts)} documents. Total: {self.index.ntotal}")
    
    def search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter_fn: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector
            k: Number of results to return
            filter_fn: Optional function to filter results
            
        Returns:
            List of dicts with 'text', 'score', and metadata
        """
        if self.index.ntotal == 0:
            return []
        
        # Convert to numpy array
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = self.index.search(query_vector, min(k * 2, self.index.ntotal))
        
        # Build results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            
            meta = self.metadata[idx]
            
            # Apply filter if provided
            if filter_fn and not filter_fn(meta):
                continue
            
            results.append({
                **meta,
                "score": float(dist),
                "similarity": 1 / (1 + float(dist))  # Convert distance to similarity
            })
            
            if len(results) >= k:
                break
        
        return results
    
    def clear(self):
        """Clear all vectors and metadata."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        print("[ContextLayer] Cleared all vectors")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "metadata_count": len(self.metadata),
        }
