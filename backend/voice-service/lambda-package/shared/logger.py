"""
Centralized logging configuration for Lambda functions
"""
import logging
import json
from typing import Any, Dict
from .config import settings


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with consistent formatting
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler with JSON formatting for CloudWatch
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, settings.log_level.upper()))
    
    # JSON formatter for structured logging
    class JSONFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            # Add extra fields
            if hasattr(record, 'extra'):
                log_data.update(record.extra)
            
            return json.dumps(log_data)
    
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger


def log_lambda_event(logger: logging.Logger, event: Dict[str, Any], context: Any = None) -> None:
    """
    Log Lambda invocation event
    
    Args:
        logger: Logger instance
        event: Lambda event
        context: Lambda context (optional)
    """
    log_data = {
        'event_type': 'lambda_invocation',
        'event': event
    }
    
    if context:
        log_data['context'] = {
            'request_id': context.request_id,
            'function_name': context.function_name,
            'memory_limit': context.memory_limit_in_mb,
            'remaining_time': context.get_remaining_time_in_millis()
        }
    
    logger.info('Lambda invocation', extra=log_data)
