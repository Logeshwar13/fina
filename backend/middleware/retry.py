"""
Retry Middleware
Provides retry logic for failed operations.
"""

import asyncio
import time
from typing import Callable, Any, Optional, Type
from functools import wraps

from observability import get_logger, get_metrics

logger = get_logger()
metrics = get_metrics()


class RetryConfig:
    """Retry configuration"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
        retry_on: tuple = (Exception,),
        retry_on_result: Optional[Callable[[Any], bool]] = None
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.retry_on = retry_on
        self.retry_on_result = retry_on_result


def retry_with_backoff(config: Optional[RetryConfig] = None):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        config: Retry configuration
        
    Returns:
        Decorated function
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            """Async wrapper"""
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(config.max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    
                    # Check if result should trigger retry
                    if config.retry_on_result and config.retry_on_result(result):
                        if attempt < config.max_retries:
                            logger.warning(
                                f"Retry on result: {func.__name__}",
                                attempt=attempt + 1,
                                max_retries=config.max_retries,
                                delay=delay
                            )
                            await asyncio.sleep(delay)
                            delay = min(delay * config.backoff_factor, config.max_delay)
                            continue
                    
                    # Success
                    if attempt > 0:
                        logger.info(
                            f"Retry succeeded: {func.__name__}",
                            attempt=attempt + 1
                        )
                        metrics.increment("retry.success", tags={"function": func.__name__})
                    
                    return result
                    
                except config.retry_on as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        logger.warning(
                            f"Retry attempt {attempt + 1}/{config.max_retries}: {func.__name__}",
                            error=str(e),
                            delay=delay
                        )
                        
                        metrics.increment("retry.attempt", tags={
                            "function": func.__name__,
                            "error_type": type(e).__name__
                        })
                        
                        await asyncio.sleep(delay)
                        delay = min(delay * config.backoff_factor, config.max_delay)
                    else:
                        logger.error(
                            f"Retry exhausted: {func.__name__}",
                            attempts=attempt + 1,
                            error=str(e)
                        )
                        metrics.increment("retry.exhausted", tags={"function": func.__name__})
            
            # All retries exhausted
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Sync wrapper"""
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(config.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Check if result should trigger retry
                    if config.retry_on_result and config.retry_on_result(result):
                        if attempt < config.max_retries:
                            logger.warning(
                                f"Retry on result: {func.__name__}",
                                attempt=attempt + 1,
                                max_retries=config.max_retries,
                                delay=delay
                            )
                            time.sleep(delay)
                            delay = min(delay * config.backoff_factor, config.max_delay)
                            continue
                    
                    # Success
                    if attempt > 0:
                        logger.info(
                            f"Retry succeeded: {func.__name__}",
                            attempt=attempt + 1
                        )
                        metrics.increment("retry.success", tags={"function": func.__name__})
                    
                    return result
                    
                except config.retry_on as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        logger.warning(
                            f"Retry attempt {attempt + 1}/{config.max_retries}: {func.__name__}",
                            error=str(e),
                            delay=delay
                        )
                        
                        metrics.increment("retry.attempt", tags={
                            "function": func.__name__,
                            "error_type": type(e).__name__
                        })
                        
                        time.sleep(delay)
                        delay = min(delay * config.backoff_factor, config.max_delay)
                    else:
                        logger.error(
                            f"Retry exhausted: {func.__name__}",
                            attempts=attempt + 1,
                            error=str(e)
                        )
                        metrics.increment("retry.exhausted", tags={"function": func.__name__})
            
            # All retries exhausted
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Predefined retry configurations

# For LLM API calls
LLM_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay=1.0,
    backoff_factor=2.0,
    retry_on=(TimeoutError, ConnectionError, Exception)
)

# For database operations
DATABASE_RETRY_CONFIG = RetryConfig(
    max_retries=2,
    initial_delay=0.5,
    backoff_factor=2.0,
    retry_on=(ConnectionError, TimeoutError)
)

# For external API calls
API_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay=1.0,
    backoff_factor=2.0,
    retry_on=(TimeoutError, ConnectionError)
)

# For vector store operations
VECTOR_STORE_RETRY_CONFIG = RetryConfig(
    max_retries=2,
    initial_delay=0.5,
    backoff_factor=1.5,
    retry_on=(Exception,)
)


# Convenience decorators

def retry_llm(func: Callable):
    """Retry decorator for LLM operations"""
    return retry_with_backoff(LLM_RETRY_CONFIG)(func)


def retry_database(func: Callable):
    """Retry decorator for database operations"""
    return retry_with_backoff(DATABASE_RETRY_CONFIG)(func)


def retry_api(func: Callable):
    """Retry decorator for API operations"""
    return retry_with_backoff(API_RETRY_CONFIG)(func)


def retry_vector_store(func: Callable):
    """Retry decorator for vector store operations"""
    return retry_with_backoff(VECTOR_STORE_RETRY_CONFIG)(func)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    @retry_with_backoff(RetryConfig(max_retries=3, initial_delay=0.5))
    async def flaky_function():
        """Example flaky function"""
        import random
        if random.random() < 0.7:
            raise Exception("Random failure")
        return "Success"
    
    async def test():
        try:
            result = await flaky_function()
            print(f"Result: {result}")
        except Exception as e:
            print(f"Failed: {e}")
    
    asyncio.run(test())
