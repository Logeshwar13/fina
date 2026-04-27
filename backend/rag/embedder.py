"""
Embedding Generation Module
Generates vector embeddings for text chunks using various models.
"""

import os
from typing import List, Optional
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """
    Generates embeddings for text using sentence-transformers.
    Falls back to local models when API keys are not available.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        use_api: bool = False
    ):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Name of the sentence-transformers model
            dimension: Embedding dimension (384 for MiniLM, 768 for BERT, 1536 for OpenAI)
            use_api: Whether to use API-based embeddings (OpenAI/Groq)
        """
        self.model_name = model_name
        self.dimension = dimension
        self.use_api = use_api
        
        # Initialize local model
        if not use_api:
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
        else:
            self.model = None
            # API-based embedding will be handled by ModelLayer
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if self.use_api:
            raise NotImplementedError(
                "API-based embeddings should use ModelLayer.generate_embedding()"
            )
        
        # Use local model (run in executor to avoid blocking)
        import asyncio
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self.model.encode(text, convert_to_numpy=True)
        )
        return embedding.tolist()
    
    async def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if self.use_api:
            raise NotImplementedError(
                "API-based embeddings should use ModelLayer.generate_embedding()"
            )
        
        # Process in batches for efficiency (run in executor to avoid blocking)
        import asyncio
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 100
            )
        )
        
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension
    
    @staticmethod
    def get_recommended_model(use_case: str = "general") -> str:
        """
        Get recommended model for specific use case.
        
        Args:
            use_case: Use case (general, financial, multilingual)
            
        Returns:
            Model name
        """
        models = {
            "general": "all-MiniLM-L6-v2",  # 384 dim, fast, good quality
            "financial": "sentence-transformers/all-mpnet-base-v2",  # 768 dim, better quality
            "multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "fast": "all-MiniLM-L6-v2",  # Fastest
            "quality": "sentence-transformers/all-mpnet-base-v2"  # Best quality
        }
        return models.get(use_case, models["general"])


class FinancialEmbedder(EmbeddingGenerator):
    """
    Specialized embedder for financial text.
    Optimized for financial terminology and concepts.
    """
    
    def __init__(self):
        """Initialize with financial-optimized model"""
        super().__init__(
            model_name="sentence-transformers/all-mpnet-base-v2",
            dimension=768
        )
    
    def preprocess_financial_text(self, text: str) -> str:
        """
        Preprocess financial text for better embeddings.
        
        Args:
            text: Raw financial text
            
        Returns:
            Preprocessed text
        """
        # Normalize currency symbols
        text = text.replace('₹', 'INR ')
        text = text.replace('$', 'USD ')
        text = text.replace('€', 'EUR ')
        
        # Normalize common financial abbreviations
        replacements = {
            'txn': 'transaction',
            'amt': 'amount',
            'acc': 'account',
            'bal': 'balance',
            'cr': 'credit',
            'dr': 'debit',
        }
        
        for abbr, full in replacements.items():
            text = text.replace(f' {abbr} ', f' {full} ')
            text = text.replace(f' {abbr.upper()} ', f' {full} ')
        
        return text
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding with financial preprocessing"""
        preprocessed = self.preprocess_financial_text(text)
        return await super().generate_embedding(preprocessed)
    
    async def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings with financial preprocessing"""
        preprocessed = [self.preprocess_financial_text(t) for t in texts]
        return await super().generate_embeddings(preprocessed, batch_size)


class HybridEmbedder:
    """
    Hybrid embedder that uses API when available, falls back to local.
    """
    
    def __init__(self, model_layer=None):
        """
        Initialize hybrid embedder.
        
        Args:
            model_layer: Optional ModelLayer instance for API embeddings
        """
        self.model_layer = model_layer
        self.local_embedder = FinancialEmbedder()
        self.dimension = 768  # Use local model dimension
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using API or local model"""
        if self.model_layer:
            try:
                # Try API first
                return await self.model_layer.generate_embedding(text)
            except Exception:
                # Fall back to local
                pass
        
        # Use local model
        return self.local_embedder.generate_embedding(text)
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings in batch"""
        if self.model_layer:
            try:
                # Try API first (may need to batch manually)
                embeddings = []
                for text in texts:
                    emb = await self.model_layer.generate_embedding(text)
                    embeddings.append(emb)
                return embeddings
            except Exception:
                # Fall back to local
                pass
        
        # Use local model (efficient batching)
        return self.local_embedder.generate_embeddings(texts)
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension
