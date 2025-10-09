"""
Standardized logging configuration for Insurance Claim Agent microservices.
Provides structured logging with context propagation and correlation IDs.
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from contextvars import ContextVar

# Context variables for request tracking
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
service_name: ContextVar[Optional[str]] = ContextVar('service_name', default=None)


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'service': service_name.get() or os.getenv('SERVICE_NAME', 'unknown'),
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'correlation_id': correlation_id.get() or str(uuid.uuid4()),
            'user_id': user_id.get(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields
        if hasattr(record, '__dict__'):
            extra_fields = {
                k: v for k, v in record.__dict__.items()
                if k not in ['name', 'msg', 'args', 'created', 'filename', 
                           'funcName', 'levelname', 'levelno', 'lineno', 
                           'module', 'msecs', 'pathname', 'process', 'processName',
                           'relativeCreated', 'thread', 'threadName', 'exc_info',
                           'exc_text', 'stack_info', 'getMessage']
            }
            if extra_fields:
                log_data['extra'] = extra_fields
                
        return json.dumps(log_data, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        if levelname in self.COLORS:
            levelname_color = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
            record.levelname = levelname_color
        
        # Add correlation ID if available
        corr_id = correlation_id.get()
        if corr_id:
            record.msg = f"[{corr_id[:8]}] {record.msg}"
            
        return super().format(record)


def setup_logger(
    name: str = None,
    level: str = None,
    service: str = None,
    log_file: str = None,
    enable_console: bool = True,
    enable_file: bool = True,
    structured: bool = None
) -> logging.Logger:
    """
    Set up a logger with structured output and proper formatting.
    
    Args:
        name: Logger name (defaults to root logger)
        level: Log level (defaults to env var LOG_LEVEL or INFO)
        service: Service name for structured logs
        log_file: Path to log file (defaults to logs/{service}.log)
        enable_console: Enable console output
        enable_file: Enable file output
        structured: Use structured JSON output (defaults to True in production)
    
    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name or __name__)
    
    # Set log level
    log_level = level or os.getenv('LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Set service name context
    if service:
        service_name.set(service)
    
    # Determine if we should use structured logging
    if structured is None:
        structured = os.getenv('ENVIRONMENT', 'development').lower() in ['production', 'staging']
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        if structured:
            console_handler.setFormatter(StructuredFormatter())
        else:
            # Use colored formatter for development
            console_handler.setFormatter(ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
        logger.addHandler(console_handler)
    
    # File handler
    if enable_file:
        # Create logs directory if it doesn't exist
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # Determine log file path
        if not log_file:
            service_name_str = service or os.getenv('SERVICE_NAME', 'app')
            log_file = os.path.join(log_dir, f'{service_name_str}.log')
        
        # Rotating file handler (10MB per file, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10_485_760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the default configuration.
    
    Args:
        name: Logger name (defaults to caller's module)
    
    Returns:
        Logger instance
    """
    if not name:
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get('__name__', 'app')
    
    return setup_logger(name=name)


def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs):
    """
    Log a message with additional context.
    
    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional context to include in the log
    """
    log_method = getattr(logger, level.lower())
    extra = kwargs if kwargs else {}
    log_method(message, extra=extra)


def set_correlation_id(corr_id: str = None) -> str:
    """
    Set the correlation ID for the current context.
    
    Args:
        corr_id: Correlation ID (generates new UUID if not provided)
    
    Returns:
        The correlation ID that was set
    """
    if not corr_id:
        corr_id = str(uuid.uuid4())
    correlation_id.set(corr_id)
    return corr_id


def set_user_context(user_id_value: str):
    """Set the user ID for the current context."""
    user_id.set(user_id_value)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that automatically includes context variables.
    """
    
    def process(self, msg, kwargs):
        extra = kwargs.get('extra', {})
        extra['correlation_id'] = correlation_id.get()
        extra['user_id'] = user_id.get()
        extra['service'] = service_name.get()
        kwargs['extra'] = extra
        return msg, kwargs


# Example usage and testing
if __name__ == '__main__':
    # Set up logger for testing
    logger = setup_logger(
        name='test_logger',
        service='test_service',
        structured=False  # Use colored output for demo
    )
    
    # Set correlation ID
    set_correlation_id('test-correlation-123')
    set_user_context('user-456')
    
    # Test different log levels
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')
    
    # Test with extra context
    log_with_context(
        logger, 'info', 'Processing claim',
        claim_id='CLM-789',
        status='pending',
        amount=1500.00
    )
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("An error occurred")
    
    print("\n✅ Logging module test complete!")