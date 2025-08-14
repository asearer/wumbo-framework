"""
🌀 Wumbo Framework - Utility Helper Functions

This module provides utility functions and helpers for the Wumbo framework,
including common operations, decorators, and convenience functions that
make working with templates easier and more efficient.
"""

import functools
import inspect
import json
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar, Generic
from pathlib import Path
import logging
from contextlib import contextmanager
from dataclasses import asdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Type definitions
T = TypeVar('T')
F = TypeVar('F', bound=Callable)


# Timing utilities
class Timer:
    """Context manager and decorator for timing operations."""

    def __init__(self, name: str = "operation", logger: Optional[logging.Logger] = None):
        self.name = name
        self.logger = logger or logging.getLogger("wumbo.timer")
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.elapsed
        self.logger.debug(f"{self.name} completed in {duration:.4f} seconds")

    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time

    def __call__(self, func: F) -> F:
        """Use as a decorator."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with Timer(f"{func.__name__}", self.logger):
                return func(*args, **kwargs)
        return wrapper


def timed(name: Optional[str] = None, logger: Optional[logging.Logger] = None):
    """Decorator to time function execution."""
    def decorator(func: F) -> F:
        timer_name = name or func.__name__
        return Timer(timer_name, logger)(func)
    return decorator


# Retry utilities
def retry(max_attempts: int = 3,
          delay: float = 1.0,
          backoff: float = 1.0,
          exceptions: tuple = (Exception,),
          logger: Optional[logging.Logger] = None):
    """
    Decorator to retry function execution on failure.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts (seconds)
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch and retry on
        logger: Optional logger for retry messages

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            log = logger or logging.getLogger("wumbo.retry")

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        log.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    else:
                        log.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}, retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff

        return wrapper
    return decorator


# Validation utilities
def validate_callable(obj: Any, name: str = "object") -> None:
    """Validate that an object is callable."""
    if not callable(obj):
        raise TypeError(f"{name} must be callable, got {type(obj).__name__}")


def validate_type(obj: Any, expected_type: type, name: str = "object") -> None:
    """Validate that an object is of expected type."""
    if not isinstance(obj, expected_type):
        raise TypeError(f"{name} must be {expected_type.__name__}, got {type(obj).__name__}")


def validate_config(config: Dict[str, Any], required_keys: List[str] = None,
                   optional_keys: List[str] = None) -> None:
    """
    Validate configuration dictionary.

    Args:
        config: Configuration dictionary to validate
        required_keys: List of required keys
        optional_keys: List of optional keys (if provided, no other keys allowed)
    """
    if required_keys:
        missing = [key for key in required_keys if key not in config]
        if missing:
            raise ValueError(f"Missing required configuration keys: {missing}")

    if optional_keys:
        allowed_keys = set(required_keys or []) | set(optional_keys)
        extra_keys = set(config.keys()) - allowed_keys
        if extra_keys:
            raise ValueError(f"Unknown configuration keys: {extra_keys}")


# Data manipulation utilities
def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """Unflatten a flattened dictionary."""
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def safe_get(obj: Any, path: str, default: Any = None, sep: str = ".") -> Any:
    """Safely get nested attribute or key from object."""
    try:
        parts = path.split(sep)
        current = obj
        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif hasattr(current, '__getitem__'):
                current = current[part]
            else:
                return default
        return current
    except (KeyError, AttributeError, IndexError, TypeError):
        return default


# Function inspection utilities
def get_function_signature(func: Callable) -> Dict[str, Any]:
    """Get detailed information about a function's signature."""
    sig = inspect.signature(func)
    return {
        'name': func.__name__,
        'parameters': {
            name: {
                'annotation': param.annotation if param.annotation != param.empty else None,
                'default': param.default if param.default != param.empty else None,
                'kind': param.kind.name
            }
            for name, param in sig.parameters.items()
        },
        'return_annotation': sig.return_annotation if sig.return_annotation != sig.empty else None,
        'docstring': inspect.getdoc(func)
    }


def accepts_kwargs(func: Callable) -> bool:
    """Check if a function accepts **kwargs."""
    sig = inspect.signature(func)
    return any(param.kind == param.VAR_KEYWORD for param in sig.parameters.values())


def accepts_args(func: Callable) -> bool:
    """Check if a function accepts *args."""
    sig = inspect.signature(func)
    return any(param.kind == param.VAR_POSITIONAL for param in sig.parameters.values())


def get_required_params(func: Callable) -> List[str]:
    """Get list of required parameter names for a function."""
    sig = inspect.signature(func)
    return [
        name for name, param in sig.parameters.items()
        if param.default == param.empty and param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)
    ]


# Serialization utilities
def serialize_object(obj: Any, include_private: bool = False) -> Dict[str, Any]:
    """Serialize an object to a JSON-compatible dictionary."""
    if hasattr(obj, '__dict__'):
        data = obj.__dict__.copy()
        if not include_private:
            data = {k: v for k, v in data.items() if not k.startswith('_')}
        return serialize_dict(data)
    elif hasattr(obj, '_asdict'):  # namedtuple
        return serialize_dict(obj._asdict())
    elif hasattr(obj, '__dataclass_fields__'):  # dataclass
        return serialize_dict(asdict(obj))
    else:
        return obj


def serialize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize a dictionary to be JSON-compatible."""
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            result[key] = serialize_dict(value)
        elif isinstance(value, (list, tuple)):
            result[key] = [serialize_object(item) for item in value]
        elif callable(value):
            result[key] = f"<function:{value.__name__}>"
        elif hasattr(value, '__dict__'):
            result[key] = serialize_object(value)
        else:
            try:
                json.dumps(value)  # Test if JSON serializable
                result[key] = value
            except TypeError:
                result[key] = str(value)
    return result


# Concurrency utilities
class ThreadSafeCounter:
    """Thread-safe counter for tracking operations."""

    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()

    def increment(self, amount: int = 1) -> int:
        """Increment counter and return new value."""
        with self._lock:
            self._value += amount
            return self._value

    def decrement(self, amount: int = 1) -> int:
        """Decrement counter and return new value."""
        with self._lock:
            self._value -= amount
            return self._value

    @property
    def value(self) -> int:
        """Get current counter value."""
        with self._lock:
            return self._value

    def reset(self, value: int = 0) -> None:
        """Reset counter to specified value."""
        with self._lock:
            self._value = value


@contextmanager
def parallel_executor(max_workers: Optional[int] = None):
    """Context manager for parallel execution."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        yield executor


def run_parallel(func: Callable, items: List[Any], max_workers: Optional[int] = None) -> List[Any]:
    """Run a function in parallel over a list of items."""
    if not items:
        return []

    with parallel_executor(max_workers) as executor:
        future_to_item = {executor.submit(func, item): item for item in items}
        results = []

        for future in as_completed(future_to_item):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                # Could log error here, for now just append None
                results.append(None)

    return results


# File and path utilities
def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def find_files(directory: Union[str, Path], pattern: str = "*", recursive: bool = True) -> List[Path]:
    """Find files matching pattern in directory."""
    directory = Path(directory)
    if not directory.exists():
        return []

    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def safe_filename(name: str, replacement: str = "_") -> str:
    """Convert string to safe filename by replacing invalid characters."""
    import re
    # Remove or replace characters that are not safe for filenames
    safe_name = re.sub(r'[<>:"/\\|?*]', replacement, name)
    # Remove leading/trailing dots and spaces
    safe_name = safe_name.strip('. ')
    # Limit length
    return safe_name[:255] if safe_name else "unnamed"


# Logging utilities
def setup_logger(name: str, level: int = logging.INFO,
                format_string: Optional[str] = None) -> logging.Logger:
    """Set up a logger with consistent formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Don't add handlers if they already exist
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            format_string or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


@contextmanager
def log_execution(logger: logging.Logger, operation: str, level: int = logging.INFO):
    """Context manager to log operation start and completion."""
    logger.log(level, f"Starting {operation}")
    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        logger.log(level, f"Completed {operation} in {duration:.4f}s")
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Failed {operation} after {duration:.4f}s: {e}")
        raise


# ID generation utilities
def generate_id(prefix: str = "", length: int = 8) -> str:
    """Generate a unique ID with optional prefix."""
    uid = str(uuid.uuid4()).replace('-', '')[:length]
    return f"{prefix}_{uid}" if prefix else uid


def generate_execution_id() -> str:
    """Generate a unique execution ID."""
    return generate_id("exec", 12)


# Cache utilities
class SimpleCache:
    """Simple in-memory cache with optional TTL."""

    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                return default

            entry = self._cache[key]

            # Check TTL
            if entry.get('expires') and time.time() > entry['expires']:
                del self._cache[key]
                return default

            return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache."""
        with self._lock:
            # Remove oldest entries if cache is full
            if len(self._cache) >= self.max_size and key not in self._cache:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

            # Calculate expiration time
            expires = None
            ttl_to_use = ttl if ttl is not None else self.default_ttl
            if ttl_to_use:
                expires = time.time() + ttl_to_use

            self._cache[key] = {
                'value': value,
                'expires': expires,
                'created': time.time()
            }

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)


def cached(ttl: Optional[float] = None, max_size: int = 100):
    """Decorator to cache function results."""
    cache = SimpleCache(max_size=max_size, default_ttl=ttl)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = "|".join(key_parts)

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        # Add cache control methods
        wrapper.cache_clear = cache.clear
        wrapper.cache_size = cache.size
        return wrapper

    return decorator


# Utility functions for common operations
def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def deduplicate(items: List[T], key: Optional[Callable[[T], Any]] = None) -> List[T]:
    """Remove duplicates from list while preserving order."""
    seen = set()
    result = []

    for item in items:
        lookup_key = key(item) if key else item
        if lookup_key not in seen:
            seen.add(lookup_key)
            result.append(item)

    return result


def group_by(items: List[T], key: Callable[[T], Any]) -> Dict[Any, List[T]]:
    """Group items by a key function."""
    groups = {}
    for item in items:
        group_key = key(item)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    return groups
