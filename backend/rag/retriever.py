"""
Semantic Retrieval Module
Retrieves relevant documents using vector similarity search.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class RetrievalResult:
    """Represents a retrieved document"""
    text: str
    metadata: Dict[str, Any]
    score: float
    chunk_id: str
    source_id: str


class SemanticRetriever:
    """
    Retrieves relevant documents using semantic search.
    Supports filtering, re-ranking, and hybrid search.
    """
    
    def __init__(self, context_layer, embedder):
        """
        Initialize retriever.
        
        Args:
            context_layer: ContextLayer instance for vector search
            embedder: EmbeddingGenerator instance
        """
        self.context = context_layer
        self.embedder = embedder
    
    def _create_filter_fn(self, filters: Dict[str, Any]):
        """Create a filter function from filter dictionary"""
        def filter_fn(metadata: Dict[str, Any]) -> bool:
            for key, value in filters.items():
                if metadata.get(key) != value:
                    return False
            return True
        return filter_fn
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters
            min_score: Minimum similarity score
            
        Returns:
            List of retrieval results
        """
        # Generate query embedding
        query_embedding = await self.embedder.generate_embedding(query)
        
        # Search vector store
        results = self.context.search(
            query_embedding=query_embedding,
            k=top_k * 2,  # Get more for filtering
            filter_fn=self._create_filter_fn(filters) if filters else None
        )
        
        # Convert to RetrievalResult objects
        retrieval_results = []
        for doc in results:
            score = doc.get("similarity", 0)  # Use similarity instead of distance
            if score >= min_score:
                result = RetrievalResult(
                    text=doc.get("text", ""),
                    metadata={k: v for k, v in doc.items() if k not in ["text", "score", "similarity"]},
                    score=float(score),
                    chunk_id=doc.get("chunk_id", ""),
                    source_id=doc.get("source_id", "")
                )
                retrieval_results.append(result)
        
        # Return top_k after filtering
        return retrieval_results[:top_k]
    
    async def retrieve_with_rerank(
        self,
        query: str,
        top_k: int = 5,
        rerank_top_k: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve with re-ranking for better relevance.
        
        Args:
            query: Search query
            top_k: Final number of results
            rerank_top_k: Number of candidates for re-ranking
            filters: Metadata filters
            
        Returns:
            Re-ranked retrieval results
        """
        # Get initial candidates
        candidates = await self.retrieve(
            query=query,
            top_k=rerank_top_k,
            filters=filters
        )
        
        # Re-rank using cross-encoder or keyword matching
        reranked = self._rerank_results(query, candidates)
        
        return reranked[:top_k]
    
    def _rerank_results(
        self,
        query: str,
        results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """
        Re-rank results using keyword matching and metadata.
        
        Args:
            query: Original query
            results: Initial retrieval results
            
        Returns:
            Re-ranked results
        """
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        # Calculate re-ranking scores
        for result in results:
            text_lower = result.text.lower()
            
            # Keyword overlap score
            text_terms = set(text_lower.split())
            overlap = len(query_terms & text_terms)
            keyword_score = overlap / len(query_terms) if query_terms else 0
            
            # Exact phrase match bonus
            phrase_bonus = 0.2 if query_lower in text_lower else 0
            
            # Metadata relevance bonus
            metadata_bonus = self._calculate_metadata_bonus(query_lower, result.metadata)
            
            # Combined score
            result.score = (
                result.score * 0.6 +  # Original similarity
                keyword_score * 0.2 +  # Keyword overlap
                phrase_bonus +  # Exact match
                metadata_bonus * 0.2  # Metadata relevance
            )
        
        # Sort by new scores
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    @staticmethod
    def _calculate_metadata_bonus(query: str, metadata: Dict[str, Any]) -> float:
        """Calculate relevance bonus from metadata"""
        bonus = 0.0
        
        # Category match
        if "category" in metadata:
            category = str(metadata["category"]).lower()
            if category in query:
                bonus += 0.3
        
        # Type match
        if "type" in metadata:
            doc_type = str(metadata["type"]).lower()
            if doc_type in query:
                bonus += 0.2
        
        # Recent documents bonus
        if "date" in metadata:
            # Could add recency scoring here
            pass
        
        return min(bonus, 1.0)
    
    async def retrieve_by_category(
        self,
        query: str,
        category: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """Retrieve documents filtered by category"""
        return await self.retrieve(
            query=query,
            top_k=top_k,
            filters={"category": category}
        )
    
    async def retrieve_by_type(
        self,
        query: str,
        doc_type: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """Retrieve documents filtered by type"""
        return await self.retrieve(
            query=query,
            top_k=top_k,
            filters={"type": doc_type}
        )
    
    async def retrieve_by_date_range(
        self,
        query: str,
        start_date: str,
        end_date: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """Retrieve documents within date range"""
        # Note: This requires custom filtering in ContextLayer
        # For now, retrieve all and filter
        results = await self.retrieve(query=query, top_k=top_k * 3)
        
        filtered = []
        for result in results:
            date = result.metadata.get("date", "")
            if start_date <= date <= end_date:
                filtered.append(result)
        
        return filtered[:top_k]
    
    async def retrieve_transactions(
        self,
        query: str,
        user_id: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """Retrieve transaction documents"""
        return await self.retrieve(
            query=query,
            top_k=top_k,
            filters={"type": "transaction", "user_id": user_id}
        )
    
    async def retrieve_budgets(
        self,
        query: str,
        user_id: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """Retrieve budget documents"""
        return await self.retrieve(
            query=query,
            top_k=top_k,
            filters={"type": "budget", "user_id": user_id}
        )
    
    async def retrieve_insurance(
        self,
        query: str,
        user_id: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """Retrieve insurance documents"""
        return await self.retrieve(
            query=query,
            top_k=top_k,
            filters={"type": "insurance", "user_id": user_id}
        )
    
    def format_context(
        self,
        results: List[RetrievalResult],
        max_length: int = 2000
    ) -> str:
        """
        Format retrieval results as context for LLM.
        
        Args:
            results: Retrieval results
            max_length: Maximum context length
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant information found."
        
        context_parts = ["Retrieved Information:\n"]
        current_length = len(context_parts[0])
        
        for i, result in enumerate(results, 1):
            # Format result
            part = f"\n[{i}] (Score: {result.score:.2f})\n{result.text}\n"
            
            # Check length
            if current_length + len(part) > max_length:
                break
            
            context_parts.append(part)
            current_length += len(part)
        
        return "".join(context_parts)
    
    def get_statistics(self, results: List[RetrievalResult]) -> Dict[str, Any]:
        """Get statistics about retrieval results"""
        if not results:
            return {
                "count": 0,
                "avg_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0
            }
        
        scores = [r.score for r in results]
        types = [r.metadata.get("type", "unknown") for r in results]
        
        return {
            "count": len(results),
            "avg_score": np.mean(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "types": dict(zip(*np.unique(types, return_counts=True)))
        }


class HybridRetriever(SemanticRetriever):
    """
    Hybrid retriever combining semantic and keyword search.
    """
    
    def __init__(self, context_layer, embedder):
        super().__init__(context_layer, embedder)
    
    async def retrieve_hybrid(
        self,
        query: str,
        top_k: int = 5,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Hybrid retrieval combining semantic and keyword search.
        
        Args:
            query: Search query
            top_k: Number of results
            semantic_weight: Weight for semantic scores
            keyword_weight: Weight for keyword scores
            filters: Metadata filters
            
        Returns:
            Hybrid retrieval results
        """
        # Get semantic results
        semantic_results = await self.retrieve(
            query=query,
            top_k=top_k * 2,
            filters=filters
        )
        
        # Calculate keyword scores
        query_terms = set(query.lower().split())
        
        for result in semantic_results:
            text_terms = set(result.text.lower().split())
            keyword_score = len(query_terms & text_terms) / len(query_terms)
            
            # Combine scores
            result.score = (
                semantic_weight * result.score +
                keyword_weight * keyword_score
            )
        
        # Re-sort and return top_k
        semantic_results.sort(key=lambda x: x.score, reverse=True)
        return semantic_results[:top_k]
