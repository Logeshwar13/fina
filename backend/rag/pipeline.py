"""
RAG Pipeline Module
Main orchestration for Retrieval-Augmented Generation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from .chunker import DocumentChunker, ChunkingStrategy
from .embedder import FinancialEmbedder, HybridEmbedder
from .retriever import SemanticRetriever, HybridRetriever
from .indexer import DocumentIndexer


class RAGPipeline:
    """
    Complete RAG pipeline for financial data.
    Handles indexing, retrieval, and context generation.
    """
    
    def __init__(
        self,
        context_layer,
        model_layer=None,
        chunking_strategy: ChunkingStrategy = ChunkingStrategy.FINANCIAL,
        use_hybrid_retrieval: bool = True
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            context_layer: ContextLayer instance for vector storage
            model_layer: Optional ModelLayer for API embeddings
            chunking_strategy: Strategy for document chunking
            use_hybrid_retrieval: Whether to use hybrid retrieval
        """
        self.context = context_layer
        self.model = model_layer
        
        # Initialize components
        self.chunker = DocumentChunker(strategy=chunking_strategy)
        
        if model_layer:
            self.embedder = HybridEmbedder(model_layer)
        else:
            self.embedder = FinancialEmbedder()
        
        if use_hybrid_retrieval:
            self.retriever = HybridRetriever(context_layer, self.embedder)
        else:
            self.retriever = SemanticRetriever(context_layer, self.embedder)
        
        self.indexer = DocumentIndexer(context_layer, self.embedder, self.chunker)
        
        self.stats = {
            "queries_processed": 0,
            "documents_indexed": 0,
            "avg_retrieval_time": 0.0
        }
    
    async def query(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """
        Process a query with RAG.
        
        Args:
            query: User query
            user_id: User ID for filtering
            top_k: Number of results to retrieve
            filters: Additional metadata filters
            include_context: Whether to format context for LLM
            
        Returns:
            Query results with retrieved documents and formatted context
        """
        start_time = datetime.now()
        
        # Add user_id to filters
        if filters is None:
            filters = {}
        filters["user_id"] = user_id
        
        # Retrieve relevant documents
        results = await self.retriever.retrieve(
            query=query,
            top_k=top_k,
            filters=filters
        )
        
        # Format context if requested
        context = None
        if include_context:
            context = self.retriever.format_context(results)
        
        # Update statistics
        elapsed = (datetime.now() - start_time).total_seconds()
        self.stats["queries_processed"] += 1
        self.stats["avg_retrieval_time"] = (
            (self.stats["avg_retrieval_time"] * (self.stats["queries_processed"] - 1) + elapsed)
            / self.stats["queries_processed"]
        )
        
        return {
            "query": query,
            "results": [
                {
                    "text": r.text,
                    "metadata": r.metadata,
                    "score": r.score,
                    "chunk_id": r.chunk_id
                }
                for r in results
            ],
            "context": context,
            "retrieval_time": elapsed,
            "num_results": len(results)
        }
    
    async def query_with_rerank(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        rerank_top_k: int = 20
    ) -> Dict[str, Any]:
        """Query with re-ranking for better relevance"""
        start_time = datetime.now()
        
        results = await self.retriever.retrieve_with_rerank(
            query=query,
            top_k=top_k,
            rerank_top_k=rerank_top_k,
            filters={"user_id": user_id}
        )
        
        context = self.retriever.format_context(results)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            "query": query,
            "results": [
                {
                    "text": r.text,
                    "metadata": r.metadata,
                    "score": r.score
                }
                for r in results
            ],
            "context": context,
            "retrieval_time": elapsed
        }
    
    async def index_user_data(
        self,
        user_id: str,
        transactions: Optional[List[Dict[str, Any]]] = None,
        budgets: Optional[List[Dict[str, Any]]] = None,
        insurance: Optional[List[Dict[str, Any]]] = None,
        risk_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Index all data for a user.
        
        Args:
            user_id: User ID
            transactions: Transaction list
            budgets: Budget list
            insurance: Insurance policy list
            risk_data: Risk assessment data
            
        Returns:
            Indexing statistics
        """
        tasks = []
        
        if transactions:
            tasks.append(self.indexer.index_transactions(transactions, user_id))
        
        if budgets:
            tasks.append(self.indexer.index_budgets(budgets, user_id))
        
        if insurance:
            tasks.append(self.indexer.index_insurance_policies(insurance, user_id))
        
        if risk_data:
            tasks.append(self.indexer.index_risk_data(risk_data, user_id))
        
        # Execute all indexing tasks in parallel
        results = await asyncio.gather(*tasks)
        
        # Combine statistics
        total_stats = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        for i, result in enumerate(results):
            total_stats[f"task_{i}"] = result
        
        self.stats["documents_indexed"] += sum(
            r.get("chunks_created", 0) for r in results
        )
        
        return total_stats
    
    async def search_transactions(
        self,
        query: str,
        user_id: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Search transaction data"""
        results = await self.retriever.retrieve_transactions(
            query=query,
            user_id=user_id,
            top_k=top_k
        )
        
        return {
            "query": query,
            "type": "transactions",
            "results": [
                {
                    "text": r.text,
                    "metadata": r.metadata,
                    "score": r.score
                }
                for r in results
            ],
            "context": self.retriever.format_context(results)
        }
    
    async def search_budgets(
        self,
        query: str,
        user_id: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Search budget data"""
        results = await self.retriever.retrieve_budgets(
            query=query,
            user_id=user_id,
            top_k=top_k
        )
        
        return {
            "query": query,
            "type": "budgets",
            "results": [
                {
                    "text": r.text,
                    "metadata": r.metadata,
                    "score": r.score
                }
                for r in results
            ],
            "context": self.retriever.format_context(results)
        }
    
    async def search_insurance(
        self,
        query: str,
        user_id: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Search insurance data"""
        results = await self.retriever.retrieve_insurance(
            query=query,
            user_id=user_id,
            top_k=top_k
        )
        
        return {
            "query": query,
            "type": "insurance",
            "results": [
                {
                    "text": r.text,
                    "metadata": r.metadata,
                    "score": r.score
                }
                for r in results
            ],
            "context": self.retriever.format_context(results)
        }
    
    async def generate_rag_response(
        self,
        query: str,
        user_id: str,
        system_prompt: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Generate LLM response with RAG context.
        
        Args:
            query: User query
            user_id: User ID
            system_prompt: Optional system prompt
            top_k: Number of documents to retrieve
            
        Returns:
            LLM response with sources
        """
        if not self.model:
            raise ValueError("ModelLayer required for response generation")
        
        # Retrieve relevant context
        rag_result = await self.query(
            query=query,
            user_id=user_id,
            top_k=top_k,
            include_context=True
        )
        
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add context and query
        user_message = f"""Context from your financial data:
{rag_result['context']}

Question: {query}

Please provide a helpful response based on the context above."""
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Generate response
        response = await self.model.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "query": query,
            "response": response["content"],
            "sources": rag_result["results"],
            "retrieval_time": rag_result["retrieval_time"],
            "tokens_used": response.get("usage", {})
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            **self.stats,
            "index_stats": self.indexer.get_index_stats()
        }
    
    def reset_statistics(self):
        """Reset pipeline statistics"""
        self.stats = {
            "queries_processed": 0,
            "documents_indexed": 0,
            "avg_retrieval_time": 0.0
        }


class FinancialRAGPipeline(RAGPipeline):
    """
    Specialized RAG pipeline for financial advisory.
    Includes domain-specific optimizations.
    """
    
    def __init__(self, context_layer, model_layer=None):
        super().__init__(
            context_layer=context_layer,
            model_layer=model_layer,
            chunking_strategy=ChunkingStrategy.FINANCIAL,
            use_hybrid_retrieval=True
        )
    
    async def get_spending_insights(
        self,
        user_id: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get AI-powered spending insights"""
        query = f"spending patterns and trends"
        if category:
            query += f" for {category}"
        
        return await self.search_transactions(
            query=query,
            user_id=user_id,
            top_k=10
        )
    
    async def get_budget_recommendations(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get budget recommendations based on spending"""
        query = "budget limits and spending patterns"
        
        return await self.search_budgets(
            query=query,
            user_id=user_id,
            top_k=5
        )
    
    async def get_insurance_recommendations(
        self,
        user_id: str,
        policy_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get insurance recommendations"""
        query = "insurance coverage and recommendations"
        if policy_type:
            query += f" for {policy_type}"
        
        return await self.search_insurance(
            query=query,
            user_id=user_id,
            top_k=5
        )
    
    async def answer_financial_question(
        self,
        question: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Answer financial questions using RAG.
        
        Args:
            question: User's financial question
            user_id: User ID
            
        Returns:
            AI-generated answer with sources
        """
        system_prompt = """You are a helpful financial advisor assistant.
Use the provided context from the user's financial data to answer their questions.
Be specific and reference actual numbers from their data.
If the context doesn't contain enough information, say so clearly.
Always provide actionable advice when appropriate."""
        
        return await self.generate_rag_response(
            query=question,
            user_id=user_id,
            system_prompt=system_prompt,
            top_k=5
        )
