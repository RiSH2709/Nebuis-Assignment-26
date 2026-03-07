#!/usr/bin/env python3
"""
Test script for the logging system
"""
from backend.logger_config import setup_logging, performance_logger, error_tracker
import logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Test different log levels
logger.debug("This is a DEBUG message")
logger.info("This is an INFO message")
logger.warning("This is a WARNING message")
logger.error("This is an ERROR message")

# Test performance logging
print("\n" + "="*80)
print("Testing Performance Logger")
print("="*80)
performance_logger.log_request(
    repo_url="https://github.com/test/repo",
    duration=2.5,
    status="SUCCESS",
    files_processed=45,
    context_size=65000
)
print("✓ Performance log created")

# Test error tracking
print("\n" + "="*80)
print("Testing Error Tracker")
print("="*80)
error_tracker.log_error(
    error_type="VALIDATION",
    repo_url="https://github.com/test/invalid",
    error_msg="Invalid repository URL format",
    exception=None
)
print("✓ Error log created")

error_tracker.log_error(
    error_type="GITHUB_API",
    repo_url="https://github.com/test/notfound",
    error_msg="Repository not found",
    exception=Exception("404 Not Found")
)
print("✓ Error log with exception created")

print("\n" + "="*80)
print("Logging system test completed!")
print("="*80)
print("\nCheck the following files:")
print("  - logs/app.log")
print("  - logs/errors.log")
print("  - logs/performance.log")
