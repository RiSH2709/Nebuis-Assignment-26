"""
Enhanced logging configuration with error tracking and runtime metrics
"""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
APP_LOG = LOGS_DIR / "app.log"
ERROR_LOG = LOGS_DIR / "errors.log"
PERFORMANCE_LOG = LOGS_DIR / "performance.log"

# Custom formatter with more details
class DetailedFormatter(logging.Formatter):
    """Enhanced formatter with color support for console"""
    
    # Color codes for terminal
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def __init__(self, use_colors=False):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.use_colors = use_colors
    
    def format(self, record):
        if self.use_colors and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class PerformanceLogger:
    """Custom logger for tracking runtime metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger('performance')
        self.logger.setLevel(logging.INFO)
        
        # File handler for performance logs
        handler = logging.handlers.RotatingFileHandler(
            PERFORMANCE_LOG,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(handler)
    
    def log_request(self, repo_url: str, duration: float, status: str, files_processed: int, context_size: int):
        """Log performance metrics for a request"""
        self.logger.info(
            f"REPO: {repo_url} | "
            f"STATUS: {status} | "
            f"DURATION: {duration:.2f}s | "
            f"FILES: {files_processed} | "
            f"CONTEXT_SIZE: {context_size} chars"
        )


class ErrorTracker:
    """Custom logger for categorizing and tracking errors"""
    
    ERROR_TYPES = {
        'VALIDATION': 'Invalid input or URL format',
        'GITHUB_API': 'GitHub API errors (rate limit, not found, etc.)',
        'LLM_API': 'LLM provider errors',
        'TIMEOUT': 'Request timeout',
        'NETWORK': 'Network/connection errors',
        'PROCESSING': 'Data processing errors',
        'SYSTEM': 'System/unexpected errors'
    }
    
    def __init__(self):
        self.logger = logging.getLogger('errors')
        self.logger.setLevel(logging.WARNING)
        
        # File handler for error logs
        handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(handler)
    
    def log_error(self, error_type: str, repo_url: str, error_msg: str, exception: Exception = None):
        """Log an error with categorization"""
        error_desc = self.ERROR_TYPES.get(error_type, 'Unknown error type')
        
        log_msg = (
            f"TYPE: {error_type} ({error_desc}) | "
            f"REPO: {repo_url} | "
            f"ERROR: {error_msg}"
        )
        
        if exception:
            log_msg += f" | EXCEPTION: {type(exception).__name__}: {str(exception)}"
        
        self.logger.error(log_msg)


def setup_logging(log_level: str = "INFO"):
    """
    Configure application-wide logging with multiple handlers
    
    Creates three log files:
    - app.log: General application logs
    - errors.log: Error tracking with categorization
    - performance.log: Runtime metrics and performance data
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # Console handler (colored output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(DetailedFormatter(use_colors=True))
    root_logger.addHandler(console_handler)
    
    # App log file handler (rotating)
    app_handler = logging.handlers.RotatingFileHandler(
        APP_LOG,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(level)
    app_handler.setFormatter(DetailedFormatter(use_colors=False))
    root_logger.addHandler(app_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info("=" * 80)
    root_logger.info(f"Logging system initialized | Level: {log_level} | Logs dir: {LOGS_DIR.absolute()}")
    root_logger.info("=" * 80)
    
    return root_logger


# Create singleton instances
performance_logger = PerformanceLogger()
error_tracker = ErrorTracker()
