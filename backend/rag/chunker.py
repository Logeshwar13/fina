"""
Document Chunking Module
Splits documents into optimal chunks for embedding and retrieval.
"""

from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass


class ChunkingStrategy(Enum):
    """Available chunking strategies"""
    FIXED_SIZE = "fixed_size"
    SENTENCE = "sentence"
    SEMANTIC = "semantic"
    FINANCIAL = "financial"  # Custom for financial data


@dataclass
class Chunk:
    """Represents a document chunk"""
    text: str
    metadata: Dict[str, Any]
    chunk_id: str
    source_id: str
    start_pos: int
    end_pos: int


class DocumentChunker:
    """
    Chunks documents using various strategies optimized for financial data.
    """
    
    def __init__(
        self,
        strategy: ChunkingStrategy = ChunkingStrategy.FINANCIAL,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        """
        Initialize chunker.
        
        Args:
            strategy: Chunking strategy to use
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
        """
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(
        self,
        text: str,
        metadata: Dict[str, Any],
        source_id: str
    ) -> List[Chunk]:
        """
        Chunk a document based on the selected strategy.
        
        Args:
            text: Document text to chunk
            metadata: Document metadata
            source_id: Unique identifier for the source document
            
        Returns:
            List of chunks
        """
        if self.strategy == ChunkingStrategy.FIXED_SIZE:
            return self._chunk_fixed_size(text, metadata, source_id)
        elif self.strategy == ChunkingStrategy.SENTENCE:
            return self._chunk_by_sentence(text, metadata, source_id)
        elif self.strategy == ChunkingStrategy.FINANCIAL:
            return self._chunk_financial(text, metadata, source_id)
        else:
            return self._chunk_fixed_size(text, metadata, source_id)
    
    def _chunk_fixed_size(
        self,
        text: str,
        metadata: Dict[str, Any],
        source_id: str
    ) -> List[Chunk]:
        """Fixed-size chunking with overlap"""
        chunks = []
        start = 0
        chunk_num = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            
            chunk = Chunk(
                text=chunk_text,
                metadata={**metadata, "chunk_num": chunk_num},
                chunk_id=f"{source_id}_chunk_{chunk_num}",
                source_id=source_id,
                start_pos=start,
                end_pos=end
            )
            chunks.append(chunk)
            
            start += self.chunk_size - self.chunk_overlap
            chunk_num += 1
        
        return chunks
    
    def _chunk_by_sentence(
        self,
        text: str,
        metadata: Dict[str, Any],
        source_id: str
    ) -> List[Chunk]:
        """Chunk by sentences, grouping to target size"""
        # Simple sentence splitting
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_num = 0
        start_pos = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Create chunk from accumulated sentences
                chunk_text = '. '.join(current_chunk) + '.'
                chunk = Chunk(
                    text=chunk_text,
                    metadata={**metadata, "chunk_num": chunk_num},
                    chunk_id=f"{source_id}_chunk_{chunk_num}",
                    source_id=source_id,
                    start_pos=start_pos,
                    end_pos=start_pos + len(chunk_text)
                )
                chunks.append(chunk)
                
                # Keep last sentence for overlap
                if self.chunk_overlap > 0 and current_chunk:
                    current_chunk = [current_chunk[-1]]
                    current_size = len(current_chunk[0])
                else:
                    current_chunk = []
                    current_size = 0
                
                start_pos += len(chunk_text)
                chunk_num += 1
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = '. '.join(current_chunk) + '.'
            chunk = Chunk(
                text=chunk_text,
                metadata={**metadata, "chunk_num": chunk_num},
                chunk_id=f"{source_id}_chunk_{chunk_num}",
                source_id=source_id,
                start_pos=start_pos,
                end_pos=start_pos + len(chunk_text)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_financial(
        self,
        text: str,
        metadata: Dict[str, Any],
        source_id: str
    ) -> List[Chunk]:
        """
        Financial-specific chunking.
        Preserves transaction records, budget entries, etc. as complete units.
        """
        # For structured financial data, treat each record as a chunk
        doc_type = metadata.get("type", "")
        
        if doc_type == "transaction":
            # Single transaction = single chunk
            return [Chunk(
                text=text,
                metadata=metadata,
                chunk_id=f"{source_id}_chunk_0",
                source_id=source_id,
                start_pos=0,
                end_pos=len(text)
            )]
        
        elif doc_type == "budget":
            # Budget entry = single chunk
            return [Chunk(
                text=text,
                metadata=metadata,
                chunk_id=f"{source_id}_chunk_0",
                source_id=source_id,
                start_pos=0,
                end_pos=len(text)
            )]
        
        elif doc_type == "insurance":
            # Insurance policy = single chunk
            return [Chunk(
                text=text,
                metadata=metadata,
                chunk_id=f"{source_id}_chunk_0",
                source_id=source_id,
                start_pos=0,
                end_pos=len(text)
            )]
        
        else:
            # Fall back to sentence-based chunking
            return self._chunk_by_sentence(text, metadata, source_id)
    
    def chunk_transactions(self, transactions: List[Dict[str, Any]]) -> List[Chunk]:
        """
        Chunk transaction data for indexing.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of chunks
        """
        chunks = []
        
        for txn in transactions:
            # Create rich text representation
            text = self._format_transaction(txn)
            
            chunk = Chunk(
                text=text,
                metadata={
                    "type": "transaction",
                    "transaction_id": txn.get("id"),
                    "category": txn.get("category"),
                    "amount": txn.get("amount"),
                    "date": txn.get("date"),
                    "user_id": txn.get("user_id")
                },
                chunk_id=f"txn_{txn.get('id')}",
                source_id=f"transaction_{txn.get('id')}",
                start_pos=0,
                end_pos=len(text)
            )
            chunks.append(chunk)
        
        return chunks
    
    def chunk_budgets(self, budgets: List[Dict[str, Any]]) -> List[Chunk]:
        """Chunk budget data for indexing"""
        chunks = []
        
        for budget in budgets:
            text = self._format_budget(budget)
            
            chunk = Chunk(
                text=text,
                metadata={
                    "type": "budget",
                    "budget_id": budget.get("id"),
                    "category": budget.get("category"),
                    "limit": budget.get("limit"),
                    "spent": budget.get("spent"),
                    "user_id": budget.get("user_id")
                },
                chunk_id=f"budget_{budget.get('id')}",
                source_id=f"budget_{budget.get('id')}",
                start_pos=0,
                end_pos=len(text)
            )
            chunks.append(chunk)
        
        return chunks
    
    def chunk_insurance_policies(self, policies: List[Dict[str, Any]]) -> List[Chunk]:
        """Chunk insurance policy data for indexing"""
        chunks = []
        
        for policy in policies:
            text = self._format_insurance(policy)
            
            chunk = Chunk(
                text=text,
                metadata={
                    "type": "insurance",
                    "policy_id": policy.get("id"),
                    "policy_type": policy.get("policy_type"),
                    "coverage": policy.get("coverage_amount"),
                    "premium": policy.get("premium"),
                    "user_id": policy.get("user_id")
                },
                chunk_id=f"insurance_{policy.get('id')}",
                source_id=f"insurance_{policy.get('id')}",
                start_pos=0,
                end_pos=len(text)
            )
            chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def _format_transaction(txn: Dict[str, Any]) -> str:
        """Format transaction as searchable text"""
        return (
            f"Transaction: {txn.get('description', 'N/A')} "
            f"Category: {txn.get('category', 'N/A')} "
            f"Amount: ₹{txn.get('amount', 0)} "
            f"Type: {txn.get('type', 'N/A')} "
            f"Date: {txn.get('date', 'N/A')} "
            f"Payment Method: {txn.get('payment_method', 'N/A')}"
        )
    
    @staticmethod
    def _format_budget(budget: Dict[str, Any]) -> str:
        """Format budget as searchable text"""
        spent = budget.get('spent', 0)
        limit = budget.get('limit', 0)
        remaining = limit - spent
        percentage = (spent / limit * 100) if limit > 0 else 0
        
        return (
            f"Budget for {budget.get('category', 'N/A')} "
            f"Limit: ₹{limit} "
            f"Spent: ₹{spent} ({percentage:.1f}%) "
            f"Remaining: ₹{remaining} "
            f"Period: {budget.get('month', 'N/A')}"
        )
    
    @staticmethod
    def _format_insurance(policy: Dict[str, Any]) -> str:
        """Format insurance policy as searchable text"""
        return (
            f"Insurance Policy: {policy.get('policy_type', 'N/A')} "
            f"Provider: {policy.get('provider', 'N/A')} "
            f"Coverage: ₹{policy.get('coverage_amount', 0)} "
            f"Premium: ₹{policy.get('premium', 0)} "
            f"Status: {policy.get('status', 'N/A')} "
            f"Start: {policy.get('start_date', 'N/A')} "
            f"End: {policy.get('end_date', 'N/A')}"
        )
