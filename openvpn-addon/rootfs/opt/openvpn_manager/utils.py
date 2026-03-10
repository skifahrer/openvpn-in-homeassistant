"""OpenVPN Manager - Utility functions."""
import os
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        Timestamp string
    """
    return datetime.now().isoformat()


def format_uptime(seconds: int) -> str:
    """
    Format uptime seconds into human-readable string.

    Args:
        seconds: Uptime in seconds

    Returns:
        Formatted string (e.g., "2h 30m" or "45s")
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"


def create_api_response(success: bool, data: Any = None, error: str = None, status: str = None) -> Dict[str, Any]:
    """
    Create standardized API response.

    Args:
        success: Whether the operation was successful
        data: Response data (optional)
        error: Error message if not successful (optional)
        status: Status string (optional)

    Returns:
        Dictionary with standardized response format
    """
    response = {
        "success": success,
        "timestamp": get_timestamp()
    }

    if status:
        response["status"] = status

    if data is not None:
        response["data"] = data

    if error:
        response["error"] = error

    return response


def ensure_directory(directory: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Path to directory

    Returns:
        True if directory exists or was created, False on error
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except OSError as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False


def read_file_safe(file_path: str, default: str = "") -> str:
    """
    Safely read a file with error handling.

    Args:
        file_path: Path to file
        default: Default value to return on error

    Returns:
        File content or default value
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return f.read().strip()
    except IOError as e:
        logger.debug(f"Could not read file {file_path}: {e}")

    return default


def write_file_safe(file_path: str, content: str) -> bool:
    """
    Safely write to a file with error handling.

    Args:
        file_path: Path to file
        content: Content to write

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    except IOError as e:
        logger.error(f"Could not write file {file_path}: {e}")
        return False


def parse_boolean(value: Any) -> bool:
    """
    Parse various types to boolean.

    Args:
        value: Value to parse

    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on')

    return bool(value)


def get_log_level(level_str: str) -> int:
    """
    Convert log level string to logging constant.

    Args:
        level_str: Log level as string (debug, info, warning, error)

    Returns:
        Logging level constant
    """
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }

    return levels.get(level_str.lower(), logging.INFO)
