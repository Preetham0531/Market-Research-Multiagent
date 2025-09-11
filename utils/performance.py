"""
Performance monitoring and resource management utilities
"""

import psutil
import gc
import time
import logging
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system performance and resource usage"""
    
    def __init__(self):
        self.start_time = time.time()
        self.peak_memory = 0
        self.request_count = 0
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.peak_memory = max(self.peak_memory, memory_mb)
        return memory_mb
    
    def check_memory_limit(self, limit_mb: int = 512) -> bool:
        """Check if memory usage is within limits"""
        current_memory = self.get_memory_usage()
        if current_memory > limit_mb:
            logger.warning(f"Memory usage {current_memory:.2f}MB exceeds limit {limit_mb}MB")
            return False
        return True
    
    def cleanup_memory(self):
        """Force garbage collection to free memory"""
        gc.collect()
        logger.info(f"Memory cleanup completed. Current usage: {self.get_memory_usage():.2f}MB")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        current_memory = self.get_memory_usage()
        runtime = time.time() - self.start_time
        
        return {
            "current_memory_mb": round(current_memory, 2),
            "peak_memory_mb": round(self.peak_memory, 2),
            "runtime_seconds": round(runtime, 2),
            "request_count": self.request_count,
            "memory_efficient": current_memory < 256,  # Good if under 256MB
            "cpu_percent": psutil.cpu_percent(),
            "available_memory_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2)
        }

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()
        start_time = time.time()
        
        try:
            # Check memory before execution
            if not monitor.check_memory_limit():
                monitor.cleanup_memory()
            
            result = func(*args, **kwargs)
            
            # Log performance metrics
            execution_time = time.time() - start_time
            memory_usage = monitor.get_memory_usage()
            
            logger.info(f"Function {func.__name__} completed in {execution_time:.2f}s, memory: {memory_usage:.2f}MB")
            
            return result
            
        except Exception as e:
            logger.error(f"Function {func.__name__} failed after {time.time() - start_time:.2f}s: {str(e)}")
            raise
        finally:
            # Cleanup after execution
            monitor.cleanup_memory()
    
    return wrapper

def rate_limit(delay_seconds: float = 1.0):
    """Decorator to add rate limiting between function calls"""
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = delay_seconds - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

class ResourceManager:
    """Manage system resources and prevent overload"""
    
    def __init__(self, max_memory_mb: int = 512, max_requests: int = 10):
        self.max_memory_mb = max_memory_mb
        self.max_requests = max_requests
        self.active_requests = 0
        self.monitor = PerformanceMonitor()
    
    def can_process_request(self) -> bool:
        """Check if system can handle another request"""
        if self.active_requests >= self.max_requests:
            logger.warning("Maximum concurrent requests reached")
            return False
        
        if not self.monitor.check_memory_limit(self.max_memory_mb):
            logger.warning("Memory limit exceeded")
            return False
        
        return True
    
    def start_request(self):
        """Mark start of request processing"""
        self.active_requests += 1
        self.monitor.request_count += 1
    
    def end_request(self):
        """Mark end of request processing"""
        self.active_requests = max(0, self.active_requests - 1)
        self.monitor.cleanup_memory()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current resource status"""
        stats = self.monitor.get_performance_stats()
        stats.update({
            "active_requests": self.active_requests,
            "max_requests": self.max_requests,
            "can_process": self.can_process_request()
        })
        return stats

# Global resource manager instance
resource_manager = ResourceManager()
