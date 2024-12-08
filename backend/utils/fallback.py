# fallback.py
from typing import Any, Optional, List
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class AIModelError(Exception):
    """Custom exception for AI model errors"""
    pass

def with_fallback(fallback_function: Optional[callable] = None, max_retries: int = 3):
    """Decorator to handle AI model failures with fallback options"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        if fallback_function:
                            logger.info("Using fallback function")
                            return fallback_function(*args, **kwargs)
                        raise AIModelError(f"All attempts failed: {str(e)}")
        return wrapper
    return decorator

class AIModelChain:
    """Chain of AI models with fallback capability"""
    def __init__(self, models: List[callable]):
        self.models = models

    def process(self, input_data: Any) -> Any:
        for model in self.models:
            try:
                return model(input_data)
            except Exception as e:
                logger.warning(f"Model failed: {str(e)}")
                continue
        raise AIModelError("All models in chain failed")
