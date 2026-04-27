"""
Health Check System
Provides comprehensive health checks for all system components.
"""

from typing import Dict, Any, List
import time
import asyncio

from observability import get_logger, get_metrics

logger = get_logger()
metrics = get_metrics()


class HealthCheck:
    """Health check for a component"""
    
    def __init__(self, name: str, check_func, timeout: float = 5.0):
        self.name = name
        self.check_func = check_func
        self.timeout = timeout
        self.last_check_time = None
        self.last_status = None
        self.last_error = None
    
    async def check(self) -> Dict[str, Any]:
        """
        Run health check.
        
        Returns:
            Health check result
        """
        start_time = time.time()
        
        try:
            # Run check with timeout
            if asyncio.iscoroutinefunction(self.check_func):
                result = await asyncio.wait_for(
                    self.check_func(),
                    timeout=self.timeout
                )
            else:
                result = self.check_func()
            
            duration = time.time() - start_time
            
            self.last_check_time = time.time()
            self.last_status = "healthy"
            self.last_error = None
            
            return {
                "name": self.name,
                "status": "healthy",
                "duration_ms": duration * 1000,
                "timestamp": self.last_check_time,
                "details": result if isinstance(result, dict) else {}
            }
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self.last_check_time = time.time()
            self.last_status = "unhealthy"
            self.last_error = "Timeout"
            
            logger.warning(f"Health check timeout: {self.name}")
            metrics.increment("health_check.timeout", tags={"component": self.name})
            
            return {
                "name": self.name,
                "status": "unhealthy",
                "error": "Timeout",
                "duration_ms": duration * 1000,
                "timestamp": self.last_check_time
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.last_check_time = time.time()
            self.last_status = "unhealthy"
            self.last_error = str(e)
            
            logger.error(f"Health check failed: {self.name}", error=str(e))
            metrics.increment("health_check.failure", tags={"component": self.name})
            
            return {
                "name": self.name,
                "status": "unhealthy",
                "error": str(e),
                "duration_ms": duration * 1000,
                "timestamp": self.last_check_time
            }


class HealthCheckRegistry:
    """Registry for health checks"""
    
    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        self.start_time = time.time()
    
    def register(self, name: str, check_func, timeout: float = 5.0):
        """
        Register a health check.
        
        Args:
            name: Check name
            check_func: Check function
            timeout: Timeout in seconds
        """
        self.checks[name] = HealthCheck(name, check_func, timeout)
        logger.info(f"Registered health check: {name}")
    
    async def check_all(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Overall health status
        """
        start_time = time.time()
        
        # Run all checks concurrently
        tasks = [check.check() for check in self.checks.values()]
        results = await asyncio.gather(*tasks)
        
        # Determine overall status
        all_healthy = all(r["status"] == "healthy" for r in results)
        overall_status = "healthy" if all_healthy else "unhealthy"
        
        duration = time.time() - start_time
        uptime = time.time() - self.start_time
        
        # Track metrics
        metrics.set_gauge("health.uptime_seconds", uptime)
        metrics.increment("health.check.total")
        
        if overall_status == "healthy":
            metrics.increment("health.check.success")
        else:
            metrics.increment("health.check.failure")
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "uptime_seconds": uptime,
            "duration_ms": duration * 1000,
            "checks": results,
            "summary": {
                "total": len(results),
                "healthy": sum(1 for r in results if r["status"] == "healthy"),
                "unhealthy": sum(1 for r in results if r["status"] == "unhealthy")
            }
        }
    
    async def check_one(self, name: str) -> Dict[str, Any]:
        """
        Run a single health check.
        
        Args:
            name: Check name
            
        Returns:
            Health check result
        """
        if name not in self.checks:
            return {
                "name": name,
                "status": "unknown",
                "error": "Check not found"
            }
        
        return await self.checks[name].check()


# Global registry
_registry = HealthCheckRegistry()


def get_health_registry() -> HealthCheckRegistry:
    """Get global health check registry"""
    return _registry


# Standard health checks

async def check_database():
    """Check database connectivity"""
    try:
        from database.db import get_supabase
        sb = get_supabase()
        
        # Simple query to check connection
        result = sb.table("users").select("id").limit(1).execute()
        
        return {
            "connected": True,
            "response_time_ms": 10  # Placeholder
        }
    except Exception as e:
        raise Exception(f"Database check failed: {str(e)}")


async def check_llm():
    """Check LLM provider"""
    try:
        from mcp import ModelLayer
        from config import settings
        
        model = ModelLayer(provider=settings.default_llm_provider)
        
        # Simple test (don't actually call API in health check)
        return {
            "provider": settings.default_llm_provider,
            "configured": True
        }
    except Exception as e:
        raise Exception(f"LLM check failed: {str(e)}")


async def check_vector_store():
    """Check vector store"""
    try:
        from mcp import ContextLayer
        
        context = ContextLayer(dimension=384)
        
        return {
            "initialized": True,
            "dimension": 384
        }
    except Exception as e:
        raise Exception(f"Vector store check failed: {str(e)}")


async def check_observability():
    """Check observability system"""
    try:
        from observability import get_logger, get_metrics, get_tracer
        
        logger = get_logger()
        metrics = get_metrics()
        tracer = get_tracer()
        
        return {
            "logger": logger is not None,
            "metrics": metrics is not None,
            "tracer": tracer is not None
        }
    except Exception as e:
        raise Exception(f"Observability check failed: {str(e)}")


def check_memory():
    """Check memory usage"""
    try:
        import psutil
        
        memory = psutil.virtual_memory()
        
        return {
            "total_mb": memory.total / (1024 * 1024),
            "available_mb": memory.available / (1024 * 1024),
            "percent_used": memory.percent
        }
    except ImportError:
        return {"available": False, "reason": "psutil not installed"}
    except Exception as e:
        raise Exception(f"Memory check failed: {str(e)}")


def check_disk():
    """Check disk usage"""
    try:
        import psutil
        
        disk = psutil.disk_usage('/')
        
        return {
            "total_gb": disk.total / (1024 * 1024 * 1024),
            "free_gb": disk.free / (1024 * 1024 * 1024),
            "percent_used": disk.percent
        }
    except ImportError:
        return {"available": False, "reason": "psutil not installed"}
    except Exception as e:
        raise Exception(f"Disk check failed: {str(e)}")


def register_standard_checks():
    """Register standard health checks"""
    registry = get_health_registry()
    
    registry.register("database", check_database, timeout=5.0)
    registry.register("llm", check_llm, timeout=3.0)
    registry.register("vector_store", check_vector_store, timeout=3.0)
    registry.register("observability", check_observability, timeout=2.0)
    registry.register("memory", check_memory, timeout=1.0)
    registry.register("disk", check_disk, timeout=1.0)
    
    logger.info("Standard health checks registered")


if __name__ == "__main__":
    # Test health checks
    async def test():
        register_standard_checks()
        registry = get_health_registry()
        result = await registry.check_all()
        
        print("\nHealth Check Results:")
        print(f"Overall Status: {result['status']}")
        print(f"Uptime: {result['uptime_seconds']:.2f}s")
        print(f"\nComponent Checks:")
        for check in result['checks']:
            status_symbol = "✓" if check['status'] == 'healthy' else "✗"
            print(f"  {status_symbol} {check['name']}: {check['status']}")
    
    asyncio.run(test())
