"""
Document Indexing Module
Indexes financial documents into the vector store.
"""

from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime


class DocumentIndexer:
    """
    Indexes documents into the vector store with automatic chunking and embedding.
    """
    
    def __init__(self, context_layer, embedder, chunker):
        """
        Initialize indexer.
        
        Args:
            context_layer: ContextLayer instance
            embedder: EmbeddingGenerator instance
            chunker: DocumentChunker instance
        """
        self.context = context_layer
        self.embedder = embedder
        self.chunker = chunker
        self.indexed_count = 0
    
    async def index_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 32
    ) -> Dict[str, Any]:
        """
        Index multiple documents.
        
        Args:
            documents: List of documents with 'text' and 'metadata'
            batch_size: Batch size for embedding generation
            
        Returns:
            Indexing statistics
        """
        start_time = datetime.now()
        chunks_indexed = 0
        
        # Process documents in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Chunk documents
            all_chunks = []
            for doc in batch:
                chunks = self.chunker.chunk_document(
                    text=doc["text"],
                    metadata=doc.get("metadata", {}),
                    source_id=doc.get("id", f"doc_{i}")
                )
                all_chunks.extend(chunks)
            
            # Generate embeddings
            texts = [chunk.text for chunk in all_chunks]
            embeddings = await self.embedder.generate_embeddings(texts)
            
            # Index chunks in batch
            texts = [chunk.text for chunk in all_chunks]
            metadatas = [chunk.metadata for chunk in all_chunks]
            
            self.context.add_documents(
                texts=texts,
                embeddings=embeddings,
                metadata=metadatas
            )
            chunks_indexed += len(all_chunks)
        
        # Save index
        self.context.save_index()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            "documents_indexed": len(documents),
            "chunks_created": chunks_indexed,
            "elapsed_seconds": elapsed,
            "chunks_per_second": chunks_indexed / elapsed if elapsed > 0 else 0
        }
    
    async def index_transactions(
        self,
        transactions: List[Dict[str, Any]],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Index transaction data.
        
        Args:
            transactions: List of transaction dictionaries
            user_id: User ID for filtering
            
        Returns:
            Indexing statistics
        """
        # Add user_id to each transaction
        for txn in transactions:
            txn["user_id"] = user_id
        
        # Chunk transactions
        chunks = self.chunker.chunk_transactions(transactions)
        
        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = await self.embedder.generate_embeddings(texts)
        
        # Index in batch
        texts = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        self.context.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadata=metadatas
        )
        
        self.context.save_index()
        
        return {
            "transactions_indexed": len(transactions),
            "chunks_created": len(chunks)
        }
    
    async def index_budgets(
        self,
        budgets: List[Dict[str, Any]],
        user_id: str
    ) -> Dict[str, Any]:
        """Index budget data"""
        for budget in budgets:
            budget["user_id"] = user_id
        
        chunks = self.chunker.chunk_budgets(budgets)
        texts = [chunk.text for chunk in chunks]
        embeddings = await self.embedder.generate_embeddings(texts)
        
        metadatas = [chunk.metadata for chunk in chunks]
        self.context.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadata=metadatas
        )
        
        self.context.save_index()
        
        return {
            "budgets_indexed": len(budgets),
            "chunks_created": len(chunks)
        }
    
    async def index_insurance_policies(
        self,
        policies: List[Dict[str, Any]],
        user_id: str
    ) -> Dict[str, Any]:
        """Index insurance policy data"""
        for policy in policies:
            policy["user_id"] = user_id
        
        chunks = self.chunker.chunk_insurance_policies(policies)
        texts = [chunk.text for chunk in chunks]
        embeddings = await self.embedder.generate_embeddings(texts)
        
        metadatas = [chunk.metadata for chunk in chunks]
        self.context.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadata=metadatas
        )
        
        self.context.save_index()
        
        return {
            "policies_indexed": len(policies),
            "chunks_created": len(chunks)
        }
    
    async def index_risk_data(
        self,
        risk_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Index risk assessment data.
        
        Args:
            risk_data: Risk score and breakdown
            user_id: User ID
            
        Returns:
            Indexing statistics
        """
        # Format risk data as text
        text = self._format_risk_data(risk_data)
        
        # Generate embedding
        embedding = await self.embedder.generate_embedding(text)
        
        # Index
        self.context.add_documents(
            texts=[text],
            embeddings=[embedding],
            metadata=[{
                "type": "risk_assessment",
                "user_id": user_id,
                "risk_score": risk_data.get("risk_score"),
                "date": datetime.now().isoformat()
            }]
        )
        
        self.context.save_index()
        
        return {"risk_data_indexed": 1}
    
    def _format_risk_data(self, risk_data: Dict[str, Any]) -> str:
        """Format risk data as searchable text"""
        score = risk_data.get("risk_score", 0)
        breakdown = risk_data.get("breakdown", {})
        
        text_parts = [f"Financial Risk Score: {score}/100"]
        
        for factor, value in breakdown.items():
            text_parts.append(f"{factor}: {value}")
        
        return " | ".join(text_parts)
    
    async def reindex_user_data(
        self,
        user_id: str,
        transactions: List[Dict[str, Any]],
        budgets: List[Dict[str, Any]],
        insurance: List[Dict[str, Any]],
        risk_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Reindex all data for a user.
        
        Args:
            user_id: User ID
            transactions: Transaction list
            budgets: Budget list
            insurance: Insurance policy list
            risk_data: Optional risk assessment data
            
        Returns:
            Combined indexing statistics
        """
        # Clear existing user data
        self.clear_user_data(user_id)
        
        # Index all data types
        results = await asyncio.gather(
            self.index_transactions(transactions, user_id),
            self.index_budgets(budgets, user_id),
            self.index_insurance_policies(insurance, user_id)
        )
        
        # Index risk data if provided
        if risk_data:
            risk_result = await self.index_risk_data(risk_data, user_id)
            results.append(risk_result)
        
        # Combine statistics
        total_stats = {
            "user_id": user_id,
            "transactions": results[0],
            "budgets": results[1],
            "insurance": results[2]
        }
        
        if risk_data:
            total_stats["risk"] = results[3]
        
        return total_stats
    
    def clear_user_data(self, user_id: str):
        """
        Clear all indexed data for a user.
        
        Args:
            user_id: User ID
        """
        # Note: This requires implementing delete functionality in ContextLayer
        # For now, this is a placeholder
        pass
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index"""
        return {
            "total_documents": len(self.context.documents),
            "index_dimension": self.context.dimension,
            "indexed_count": self.indexed_count
        }
    
    async def incremental_index(
        self,
        new_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Incrementally add new documents without full reindex.
        
        Args:
            new_documents: New documents to add
            
        Returns:
            Indexing statistics
        """
        return await self.index_documents(new_documents)
    
    def optimize_index(self):
        """Optimize the index for better performance"""
        # Save and reload to optimize FAISS index
        self.context.save_index()
        # Could add index optimization logic here
        pass
