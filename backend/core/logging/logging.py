# core/logging/logging.py

def log_error(logger, message, error=None, context=None):
    """Standardized error logging"""
    log_data = {"message": message}
    
    if context:
        log_data.update(context)
    
    if error:
        log_data["error"] = str(error)
        log_data["error_type"] = error.__class__.__name__
        logger.error(message, extra=log_data, exc_info=error)
    else:
        logger.error(message, extra=log_data)