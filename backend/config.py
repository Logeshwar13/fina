"""
Configuration Management
Centralized configuration for the application.
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "FinA"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    port: int = Field(default=8000, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")
    workers: int = Field(default=4, env="WORKERS")
    
    # Database
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    
    # LLM Providers
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    default_llm_provider: str = Field(default="groq", env="DEFAULT_LLM_PROVIDER")
    default_llm_model: str = Field(default="llama-3.3-70b-versatile", env="DEFAULT_LLM_MODEL")
    
    # Vector Store
    faiss_index_path: str = Field(default="./data/vector_index", env="FAISS_INDEX_PATH")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=384, env="EMBEDDING_DIMENSION")
    
    # Guardrails
    max_transaction_amount: float = Field(default=10000000, env="MAX_TRANSACTION_AMOUNT")
    max_budget_limit: float = Field(default=5000000, env="MAX_BUDGET_LIMIT")
    max_insurance_coverage: float = Field(default=100000000, env="MAX_INSURANCE_COVERAGE")
    max_query_length: int = Field(default=1000, env="MAX_QUERY_LENGTH")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Caching
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    cache_enabled: bool = Field(default=False, env="CACHE_ENABLED")
    cache_ttl: int = Field(default=300, env="CACHE_TTL")
    
    # Observability
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    tracing_enabled: bool = Field(default=True, env="TRACING_ENABLED")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # CORS
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # Security
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Retry Configuration
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: float = Field(default=1.0, env="RETRY_DELAY")
    retry_backoff: float = Field(default=2.0, env="RETRY_BACKOFF")
    
    # Timeouts
    llm_timeout: int = Field(default=30, env="LLM_TIMEOUT")
    database_timeout: int = Field(default=10, env="DATABASE_TIMEOUT")
    http_timeout: int = Field(default=30, env="HTTP_TIMEOUT")
    
    # Agent Configuration
    agent_max_iterations: int = Field(default=5, env="AGENT_MAX_ITERATIONS")
    agent_timeout: int = Field(default=60, env="AGENT_TIMEOUT")
    
    # RAG Configuration
    rag_top_k: int = Field(default=5, env="RAG_TOP_K")
    rag_score_threshold: float = Field(default=0.7, env="RAG_SCORE_THRESHOLD")
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return {
            "provider": self.default_llm_provider,
            "model": self.default_llm_model,
            "timeout": self.llm_timeout,
            "api_keys": {
                "groq": self.groq_api_key,
                "openai": self.openai_api_key,
                "anthropic": self.anthropic_api_key
            }
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.supabase_url,
            "key": self.supabase_key,
            "pool_size": self.database_pool_size,
            "timeout": self.database_timeout
        }
    
    def get_guardrails_config(self) -> Dict[str, Any]:
        """Get guardrails configuration"""
        return {
            "max_transaction_amount": self.max_transaction_amount,
            "max_budget_limit": self.max_budget_limit,
            "max_insurance_coverage": self.max_insurance_coverage,
            "max_query_length": self.max_query_length
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()


def validate_configuration():
    """
    Validate configuration on startup.
    
    Raises:
        ValueError: If configuration is invalid
    """
    errors = []
    
    # Check required API keys
    if not settings.groq_api_key and not settings.openai_api_key and not settings.anthropic_api_key:
        errors.append("At least one LLM API key must be provided")
    
    # Check database configuration
    if not settings.supabase_url or not settings.supabase_key:
        errors.append("Supabase URL and key are required")
    
    # Check production settings
    if settings.is_production:
        if settings.secret_key == "change-me-in-production":
            errors.append("SECRET_KEY must be changed in production")
        
        if settings.debug:
            errors.append("DEBUG must be False in production")
        
        if "*" in settings.cors_origins:
            errors.append("CORS origins should be restricted in production")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    print("✓ Configuration validated successfully")


def print_configuration():
    """Print current configuration (safe for logging)"""
    print("\n" + "="*60)
    print("CONFIGURATION")
    print("="*60)
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")
    print(f"Log Level: {settings.log_level}")
    print(f"Port: {settings.port}")
    print(f"Workers: {settings.workers}")
    print(f"\nLLM Provider: {settings.default_llm_provider}")
    print(f"LLM Model: {settings.default_llm_model}")
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"\nMetrics Enabled: {settings.metrics_enabled}")
    print(f"Tracing Enabled: {settings.tracing_enabled}")
    print(f"Rate Limiting: {settings.rate_limit_enabled}")
    print(f"Cache Enabled: {settings.cache_enabled}")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Test configuration
    try:
        validate_configuration()
        print_configuration()
    except Exception as e:
        print(f"Configuration error: {e}")
