"""
MCP Model Layer
===============
Manages LLM interactions and ML model orchestration.
"""

import os
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ModelLayer:
    """
    Handles all model interactions (LLM + ML).
    Supports multiple providers: OpenAI, Anthropic, Groq (free & fast!).
    """
    
    def __init__(self, provider: str = "groq", model: str = None):
        self.provider = provider.lower()
        self.model = model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = OpenAI(api_key=api_key)
            self.model = self.model or "gpt-4-turbo-preview"
            
        elif self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            # Groq uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            # Default to fastest model (updated to current model)
            self.model = self.model or "llama-3.3-70b-versatile"
            
        elif self.provider == "anthropic":
            try:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment")
                self.client = anthropic.Anthropic(api_key=api_key)
                self.model = self.model or "claude-3-sonnet-20240229"
            except ImportError:
                raise ValueError("anthropic package not installed. Run: pip install anthropic")
            
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response from LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: Optional tool definitions for function calling
            
        Returns:
            Dict with 'content', 'tool_calls', 'usage', etc.
        """
        try:
            if self.provider in ["openai", "groq"]:
                return await self._generate_openai(messages, temperature, max_tokens, tools, **kwargs)
            elif self.provider == "anthropic":
                return await self._generate_anthropic(messages, temperature, max_tokens, tools, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Model generation failed: {str(e)}")
    
    async def _generate_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate using OpenAI API."""
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = kwargs.get("tool_choice", "auto")
        
        response = self.client.chat.completions.create(**params)
        message = response.choices[0].message
        
        result = {
            "content": message.content,
            "role": message.role,
            "tool_calls": [],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "finish_reason": response.choices[0].finish_reason,
        }
        
        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in message.tool_calls
            ]
        
        return result
    
    async def _generate_anthropic(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate using Anthropic API."""
        # Extract system message if present
        system_message = None
        filtered_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)
        
        params = {
            "model": self.model,
            "messages": filtered_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if system_message:
            params["system"] = system_message
        
        if tools:
            params["tools"] = tools
        
        response = self.client.messages.create(**params)
        
        result = {
            "content": "",
            "role": "assistant",
            "tool_calls": [],
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            "finish_reason": response.stop_reason,
        }
        
        for block in response.content:
            if block.type == "text":
                result["content"] += block.text
            elif block.type == "tool_use":
                result["tool_calls"].append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": str(block.input),
                    }
                })
        
        return result
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text chunks.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        if self.provider == "openai":
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [item.embedding for item in response.data]
        elif self.provider == "groq":
            # Groq doesn't have embeddings API yet
            # Use sentence-transformers as fallback
            try:
                from sentence_transformers import SentenceTransformer
                if not hasattr(self, '_embedding_model'):
                    self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                embeddings = self._embedding_model.encode(texts)
                return embeddings.tolist()
            except ImportError:
                raise NotImplementedError(
                    "Groq doesn't support embeddings. Install sentence-transformers: "
                    "pip install sentence-transformers"
                )
        else:
            raise NotImplementedError(f"Embeddings not implemented for {self.provider}")
