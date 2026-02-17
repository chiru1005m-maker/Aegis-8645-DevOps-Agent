"""Log monitoring agent node.

This module implements the monitor_logs node that reads log files,
parses entries, and detects error patterns for the Aegis-8645 workflow.
"""

import json
import logging
import re
from typing import List, Optional
from pathlib import Path

from backend.state.graph_state import GraphState

logger = logging.getLogger(__name__)


def monitor_logs(state: GraphState) -> GraphState:
    """Read log files and detect errors.
    
    This is the entry point node for the LangGraph workflow. It reads
    log files from the specified path, parses entries, detects error
    patterns, and updates the GraphState.
    
    Args:
        state: Current GraphState with log_path in metadata or as a key
        
    Returns:
        Updated GraphState with logs and detected_error populated
    """
    # Extract log_path from state (could be in metadata or direct key)
    log_path = state.get('log_path', '')
    
    if not log_path:
        logger.error("No log_path provided in state")
        state['logs'] = []
        state['detected_error'] = ""
        return state
    
    logger.info(f"Monitoring log file: {log_path}")
    
    try:
        # Validate log path
        if not Path(log_path).exists():
            raise FileNotFoundError(f"Log file not found: {log_path}")
        
        if not Path(log_path).is_file():
            raise ValueError(f"Path is not a file: {log_path}")
        
        # Read and parse log file
        logs = read_log_file(log_path)
        state['logs'] = logs
        
        # Detect errors in logs
        detected_error = detect_errors(logs)
        state['detected_error'] = detected_error
        
        if detected_error:
            logger.info(f"Error detected: {detected_error[:100]}...")
        else:
            logger.info("No errors detected in logs")
        
        return state
        
    except FileNotFoundError as e:
        logger.error(f"Log file not found: {log_path}")
        state['logs'] = []
        state['detected_error'] = ""
        raise
    except PermissionError as e:
        logger.error(f"Permission denied reading log file: {log_path}")
        state['logs'] = []
        state['detected_error'] = ""
        raise
    except UnicodeDecodeError as e:
        logger.error(f"Unable to decode log file (encoding issue): {log_path}")
        state['logs'] = []
        state['detected_error'] = ""
        raise ValueError(f"Log file encoding error: {str(e)}")
    except Exception as e:
        logger.error(f"Error reading log file: {e}", exc_info=True)
        state['logs'] = []
        state['detected_error'] = ""
        raise


def read_log_file(log_path: str) -> List[str]:
    """Read log file and parse entries.
    
    Supports both plain text and JSON log formats. Each line is treated
    as a separate log entry.
    
    Args:
        log_path: Path to the log file
        
    Returns:
        List of log entry strings
    """
    logs = []
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            
            # Try to parse as JSON first
            try:
                log_entry = json.loads(line)
                # Convert JSON to string representation
                logs.append(json.dumps(log_entry))
            except json.JSONDecodeError:
                # Treat as plain text log
                logs.append(line)
    
    logger.info(f"Read {len(logs)} log entries from {log_path}")
    return logs


def detect_errors(logs: List[str]) -> str:
    """Detect error patterns in log entries.
    
    Searches for HTTP 500 errors, exception stack traces, and ERROR-level
    log messages. Returns the first detected error with surrounding context.
    
    Args:
        logs: List of log entry strings
        
    Returns:
        Detected error message with context, or empty string if no errors
    """
    error_patterns = [
        # HTTP 500 errors
        (r'HTTP[/\s]*500', 'HTTP 500 error'),
        (r'500\s+Internal\s+Server\s+Error', 'HTTP 500 error'),
        (r'status[:\s]+500', 'HTTP 500 error'),
        
        # HTTP 502, 503, 504 errors
        (r'HTTP[/\s]*50[234]', 'HTTP 50x error'),
        (r'50[234]\s+(Bad\s+Gateway|Service\s+Unavailable|Gateway\s+Timeout)', 'HTTP 50x error'),
        
        # Exception keywords
        (r'Exception:', 'Exception'),
        (r'Traceback\s+\(most\s+recent\s+call\s+last\)', 'Exception traceback'),
        (r'Error:', 'Error'),
        (r'raise\s+\w+Error', 'Raised exception'),
        
        # Log levels
        (r'\bERROR\b', 'ERROR level log'),
        (r'\bCRITICAL\b', 'CRITICAL level log'),
        (r'\bFATAL\b', 'FATAL level log'),
    ]
    
    for i, log_entry in enumerate(logs):
        for pattern, error_type in error_patterns:
            if re.search(pattern, log_entry, re.IGNORECASE):
                # Extract error with surrounding context
                error_message = extract_error_with_context(logs, i)
                logger.info(f"Detected {error_type} at line {i+1}")
                return error_message
    
    return ""


def extract_error_with_context(logs: List[str], error_index: int, context_lines: int = 3) -> str:
    """Extract error message with surrounding log context.
    
    Args:
        logs: List of all log entries
        error_index: Index of the log entry containing the error
        context_lines: Number of lines before and after to include
        
    Returns:
        Error message with context
    """
    start_idx = max(0, error_index - context_lines)
    end_idx = min(len(logs), error_index + context_lines + 1)
    
    context_logs = logs[start_idx:end_idx]
    
    # Build error message with line numbers
    error_lines = []
    for i, log in enumerate(context_logs):
        line_num = start_idx + i + 1
        marker = ">>> " if (start_idx + i) == error_index else "    "
        error_lines.append(f"{marker}Line {line_num}: {log}")
    
    return "\n".join(error_lines)
