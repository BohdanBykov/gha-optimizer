"""Simple utility helpers for common operations."""

import logging
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

F = TypeVar('F', bound=Callable[..., Any])


def safe_execute(
    operation: str,
    logger: Optional[logging.Logger] = None,
    default_return: Any = None,
    reraise: bool = False
) -> Callable[[F], F]:
    """
    Simple decorator for safe operation execution with logging.
    
    Args:
        operation: Description of the operation for logging
        logger: Logger instance (optional)
        default_return: Value to return on error (if not re-raising)
        reraise: Whether to re-raise exceptions after logging
        
    Example:
        @safe_execute("parsing workflow YAML", default_return=[])
        def parse_workflow(content):
            return yaml.safe_load(content)
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or logging.getLogger(__name__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.error(f"Failed {operation}: {e}")
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def validate_string(value: Any, field_name: str, allow_empty: bool = False) -> str:
    """
    Simple string validation with clear error messages.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        allow_empty: Whether empty strings are allowed
        
    Returns:
        Validated string
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")
    
    if not allow_empty and not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    
    return value


def validate_list(value: Any, field_name: str, allow_empty: bool = True) -> list:
    """
    Simple list validation with clear error messages.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        allow_empty: Whether empty lists are allowed
        
    Returns:
        Validated list
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list, got {type(value).__name__}")
    
    if not allow_empty and not value:
        raise ValueError(f"{field_name} cannot be empty")
    
    return value


def safe_get(dictionary: dict, key: str, default: Any = None, expected_type: type = None) -> Any:
    """
    Safely get value from dictionary with optional type checking.
    
    Args:
        dictionary: Dictionary to get value from
        key: Key to retrieve
        default: Default value if key not found
        expected_type: Expected type for validation
        
    Returns:
        Value from dictionary or default
    """
    value = dictionary.get(key, default)
    
    if expected_type and value is not None and not isinstance(value, expected_type):
        logging.warning(f"Expected {expected_type.__name__} for key '{key}', got {type(value).__name__}")
        return default
    
    return value


class SimpleTimer:
    """Simple context manager for timing operations."""
    
    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        self.logger.debug(f"{self.operation_name} completed in {duration:.2f}s")


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format error message consistently.
    
    Args:
        error: Exception to format
        context: Additional context for the error
        
    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        return f"{context}: {error_type}: {error_msg}"
    else:
        return f"{error_type}: {error_msg}"


def find_yaml_line_numbers(yaml_content: str, search_patterns: list) -> dict:
    """
    Find line numbers for specific patterns in YAML content.
    
    Args:
        yaml_content: Raw YAML content
        search_patterns: List of patterns to search for (e.g., ['npm install', 'actions/cache'])
        
    Returns:
        Dictionary mapping patterns to line numbers where they're found
    """
    lines = yaml_content.split('\n')
    line_numbers = {}
    
    for pattern in search_patterns:
        pattern_lower = pattern.lower()
        for i, line in enumerate(lines, 1):
            if pattern_lower in line.lower():
                if pattern not in line_numbers:
                    line_numbers[pattern] = []
                line_numbers[pattern].append(i)
    
    return line_numbers


def calculate_github_actions_cost(time_minutes: float, runner_type: str = "ubuntu-latest", runs_per_week: float = 0) -> float:
    """
    Calculate GitHub Actions cost based on time and runner type.
    
    Args:
        time_minutes: Time in minutes per run
        runner_type: Type of runner (ubuntu-latest, ubuntu-latest-4-core, etc.)
        runs_per_week: Number of runs per week for monthly calculation
        
    Returns:
        Monthly cost savings in USD
    """
    # GitHub Actions pricing (per minute)
    runner_costs = {
        "ubuntu-latest": 0.008,      # $0.008/minute
        "ubuntu-latest-4-core": 0.016,  # $0.016/minute  
        "ubuntu-latest-8-core": 0.032,  # $0.032/minute
        "windows-latest": 0.016,     # $0.016/minute
        "macos-latest": 0.08,        # $0.08/minute
        "macos-latest-large": 0.16   # $0.16/minute
    }
    
    cost_per_minute = runner_costs.get(runner_type, 0.008)  # Default to ubuntu-latest
    
    if runs_per_week <= 0:
        # Return per-run cost if no weekly data
        return time_minutes * cost_per_minute
    
    # Calculate monthly savings (4.33 weeks per month average)
    monthly_runs = runs_per_week * 4.33
    monthly_cost_savings = time_minutes * cost_per_minute * monthly_runs
    
    return monthly_cost_savings


def validate_cost_calculation(time_savings: float, monthly_savings: float, runs_per_week: float, runner_type: str = "ubuntu-latest") -> dict:
    """
    validation of cost calculations with strict rules.
    
    Args:
        time_savings: Time saved per run in minutes
        monthly_savings: Claimed monthly savings in USD
        runs_per_week: Estimated runs per week (uses default if 0)
        runner_type: Runner type used
        
    Returns:
        Dictionary with validation results and recommendations
    """
    # Ensure we always have some baseline for validation
    if runs_per_week <= 0:
        runs_per_week = 50  # Conservative default: ~2 runs per workday
    
    expected_savings = calculate_github_actions_cost(time_savings, runner_type, runs_per_week)
    
    # Handle edge cases
    if expected_savings <= 0:
        return {
            "is_reasonable": False,
            "expected_savings": 0.0,
            "actual_savings": monthly_savings,
            "difference": monthly_savings,
            "percentage_difference": 100.0,
            "recommendation": f"Invalid calculation: Expected $0.00, got ${monthly_savings:.2f}",
            "validation_method": "zero_expected"
        }
    
    difference = abs(monthly_savings - expected_savings)
    percentage_diff = (difference / expected_savings * 100)
    
    # Stricter validation: Allow only 25% variance (down from 30%)
    is_reasonable = percentage_diff < 25
    
    # Additional validation rules
    if monthly_savings > 1000:  # Flag suspiciously high savings
        is_reasonable = False
        
    if time_savings > 60:  # Flag savings over 1 hour per run
        is_reasonable = False
    
    validation_method = "usage_based" if runs_per_week > 50 else "conservative_default"
    
    return {
        "is_reasonable": is_reasonable,
        "expected_savings": expected_savings,
        "actual_savings": monthly_savings,
        "difference": difference,
        "percentage_difference": percentage_diff,
        "runs_per_week": runs_per_week,
        "validation_method": validation_method,
        "recommendation": f"Expected ${expected_savings:.2f}, got ${monthly_savings:.2f} ({percentage_diff:.1f}% diff)" if not is_reasonable else f"Validated: ${monthly_savings:.2f}/month ({validation_method})"
    }
