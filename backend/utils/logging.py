# logging.py
import logging
import time
import json
from functools import wraps
from typing import Optional, Dict, Any
from datetime import datetime

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class AICallMonitor:
    """Monitor and log AI model calls"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.start_time: Optional[float] = None
        self.metrics: Dict[str, Any] = {}

    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting AI call to {self.model_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.metrics = {
            "model": self.model_name,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "success": exc_type is None
        }

        if exc_type:
            logger.error(f"AI call failed: {exc_val}", extra=self.metrics)
        else:
            logger.info(f"AI call completed in {duration:.2f}s", extra=self.metrics)


def monitor_ai_call(func):
    """Decorator to monitor AI function calls"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                f"AI call success: {func.__name__}",
                extra={
                    "duration": duration,
                    "function": func.__name__,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"AI call failed: {func.__name__}",
                extra={
                    "error": str(e),
                    "duration": duration,
                    "function": func.__name__,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            raise

    return wrapper
