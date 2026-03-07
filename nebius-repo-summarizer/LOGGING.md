# Logging System Documentation

The GitHub Repository Summarizer includes a comprehensive logging system that tracks application behavior, errors, and performance metrics.

## Log Files

All logs are stored in the `logs/` directory with automatic rotation when they reach size limits:

### 1. **app.log** (General Application Logs)
- **Size Limit:** 10MB (rotates to backup files)
- **Backup Count:** 5 files
- **Contents:**
  - Application startup/shutdown
  - Request processing steps
  - GitHub API interactions
  - File selection and processing
  - LLM API calls
  - General info, debug, and warning messages

**Example:**
```
2026-03-07 14:23:15 | INFO     | backend.main | summarize:61 | New summarize request for: https://github.com/psf/requests
2026-03-07 14:23:16 | INFO     | backend.main | summarize:70 | Fetched 145 files from psf/requests
2026-03-07 14:23:16 | INFO     | backend.main | summarize:85 | Selected 50 important files for analysis
```

### 2. **errors.log** (Error Tracking)
- **Size Limit:** 10MB (rotates to backup files)
- **Backup Count:** 5 files
- **Contents:**
  - Categorized error types
  - Repository URL where error occurred
  - Error messages and exception details
  - Stack traces for debugging

**Error Categories:**
- `VALIDATION`: Invalid input or URL format
- `GITHUB_API`: GitHub API errors (rate limit, not found, private repos)
- `LLM_API`: LLM provider errors (API key issues, model errors)
- `TIMEOUT`: Request timeout errors
- `NETWORK`: Network/connection errors
- `PROCESSING`: Data processing errors
- `SYSTEM`: System/unexpected errors

**Example:**
```
2026-03-07 14:25:30 | ERROR | TYPE: GITHUB_API (GitHub API errors) | REPO: https://github.com/invalid/repo | ERROR: Repository not found | EXCEPTION: HTTPStatusError: 404
```

### 3. **performance.log** (Runtime Metrics)
- **Size Limit:** 5MB (rotates to backup files)
- **Backup Count:** 3 files
- **Contents:**
  - Request duration (in seconds)
  - Success/failure status
  - Number of files processed
  - Context size sent to LLM
  - Repository URL

**Example:**
```
2026-03-07 14:23:18 | REPO: https://github.com/psf/requests | STATUS: SUCCESS | DURATION: 3.45s | FILES: 50 | CONTEXT_SIZE: 75432 chars
2026-03-07 14:25:30 | REPO: https://github.com/invalid/repo | STATUS: FAILED_GITHUB_API | DURATION: 0.82s | FILES: 0 | CONTEXT_SIZE: 0 chars
```

## Log Format

### Console Output (Colored)
```
2026-03-07 14:23:15 | INFO     | backend.main | summarize:61 | New summarize request for: https://github.com/psf/requests
```

### File Output
```
2026-03-07 14:23:15 | INFO     | backend.main | summarize:61 | New summarize request for: https://github.com/requests
```

**Format Fields:**
- Timestamp (YYYY-MM-DD HH:MM:SS)
- Log Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Module name
- Function name and line number
- Log message

## Monitoring Logs

### Real-time Monitoring

**Watch all application logs:**
```bash
tail -f logs/app.log
```

**Monitor only errors:**
```bash
tail -f logs/errors.log
```

**Track performance:**
```bash
tail -f logs/performance.log
```

### Analyzing Logs

**Count errors by type:**
```bash
grep "TYPE:" logs/errors.log | cut -d'|' -f2 | sort | uniq -c
```

**Find slow requests (>5 seconds):**
```bash
grep "DURATION:" logs/performance.log | awk -F'|' '{print $3, $2}' | awk '$3 > 5'
```

**Check success rate:**
```bash
echo "Total requests: $(grep -c "REPO:" logs/performance.log)"
echo "Successful: $(grep -c "SUCCESS" logs/performance.log)"
echo "Failed: $(grep -c "FAILED" logs/performance.log)"
```

**Most analyzed repositories:**
```bash
grep "REPO:" logs/performance.log | cut -d'|' -f1 | cut -d':' -f2- | sort | uniq -c | sort -rn | head -10
```

## Log Rotation

Logs automatically rotate when they reach their size limits:
- Current log: `app.log`
- First backup: `app.log.1`
- Second backup: `app.log.2`
- etc.

Oldest backups are automatically deleted when the backup count is exceeded.

## Configuration

To change log levels, edit `backend/logger_config.py`:

```python
# In backend/main.py
setup_logging(log_level="DEBUG")  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Troubleshooting

### Logs directory not created
The `logs/` directory is automatically created on first run. If it doesn't exist:
```bash
mkdir logs
```

### Permission errors
Ensure the application has write permissions:
```bash
chmod 755 logs/
```

### Logs growing too large
Current rotation settings:
- `app.log`: 10MB max, 5 backups (50MB total)
- `errors.log`: 10MB max, 5 backups (50MB total)
- `performance.log`: 5MB max, 3 backups (15MB total)

To change, edit `backend/logger_config.py` and modify `maxBytes` and `backupCount` values.

## Best Practices

1. **Monitor errors regularly** to identify common issues
2. **Track performance metrics** to optimize slow operations
3. **Archive old logs** periodically if you need long-term history
4. **Use structured queries** to extract meaningful insights from logs
5. **Check logs after deployment** to ensure everything is working correctly

## Integration with Monitoring Tools

You can integrate these logs with monitoring tools:

- **ELK Stack:** Use Filebeat to ship logs to Elasticsearch
- **Grafana Loki:** Configure promtail to tail log files
- **Splunk:** Set up forwarders to collect logs
- **CloudWatch:** Use CloudWatch agent for AWS deployments
