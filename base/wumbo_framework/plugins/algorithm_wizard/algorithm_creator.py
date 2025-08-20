
"""
algorithm_creator.py

This module provides utilities and templates for creating new algorithms within the Wumbo framework.
It is designed to help users and developers rapidly prototype, implement, and document algorithms
in a standardized and extensible way.

Key Features:
- Algorithm scaffolding: Generate boilerplate code for new algorithms.
- Registration utilities: Register algorithms for discovery and use within the framework.
- Metadata support: Attach descriptions, complexity, and tags to algorithms.
- Example templates for common algorithm types (sorting, searching, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from threading import RLock
from typing import (
    Callable,
    Any,
    Dict,
    Optional,
    List,
    TypeVar,
    Generic,
    Iterable,
    Sequence,
)

__all__ = [
    "AlgorithmMetadata",
    "AlgorithmRegistry",
    "algorithm_template",
    "bubble_sort",
    "bubble_sort_metadata",
    "algorithm_registry",
]

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True)
class AlgorithmMetadata:
    """
    Stores metadata about an algorithm for documentation and discovery.

    Attributes:
        name (str): The name of the algorithm (unique within a registry).
        description (str): A short description of what the algorithm does.
        complexity (str): Time/space complexity (e.g., "O(n log n)").
        tags (List[str]): Tags for categorization (e.g., ["sorting", "divide and conquer"]).
        author (str): Author or contributor.
    """
    name: str
    description: str
    complexity: str = ""
    tags: List[str] = field(default_factory=list)
    author: str = ""

    def as_dict(self) -> Dict[str, Any]:
        """Return metadata as a dictionary."""
        # asdict handles dataclasses (including nested) safely
        return asdict(self)


class AlgorithmRegistry:
    """
    Thread-safe registry for storing and retrieving algorithms by name.

    Usage:
        registry = AlgorithmRegistry()
        registry.register("bubble_sort", bubble_sort, metadata)
        algo = registry.get("bubble_sort")
    """

    def __init__(self):
        self._algorithms: Dict[str, Callable[..., Any]] = {}
        self._metadata: Dict[str, AlgorithmMetadata] = {}
        self._lock = RLock()

    def register(self, name: str, func: Callable[..., Any], metadata: AlgorithmMetadata) -> None:
        """
        Register a new algorithm with its metadata.

        Args:
            name: Unique name for the algorithm (must match metadata.name).
            func: The algorithm implementation (callable).
            metadata: Metadata describing the algorithm.

        Raises:
            ValueError: If name already exists, func is not callable, or names mismatch.
        """
        if not callable(func):
            raise ValueError("func must be callable")
        if name != metadata.name:
            raise ValueError(f"name '{name}' must match metadata.name '{metadata.name}'")

        with self._lock:
            if name in self._algorithms:
                raise ValueError(f"Algorithm '{name}' is already registered")
            self._algorithms[name] = func
            self._metadata[name] = metadata

    def register_decorator(self, metadata: AlgorithmMetadata) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a function as an algorithm with the provided metadata.

        Example:
            @registry.register_decorator(AlgorithmMetadata(name="my_algo", description="..."))
            def my_algo(x): ...
        """
        def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.register(metadata.name, func, metadata)
            return func
        return _decorator

    def unregister(self, name: str) -> bool:
        """
        Unregister an algorithm by name.

        Returns:
            True if the algorithm existed and was removed, False otherwise.
        """
        with self._lock:
            existed = name in self._algorithms
            if existed:
                self._algorithms.pop(name, None)
                self._metadata.pop(name, None)
            return existed

    def get(self, name: str) -> Optional[Callable[..., Any]]:
        """
        Retrieve an algorithm by name.

        Returns:
            The algorithm function, or None if not found.
        """
        with self._lock:
            return self._algorithms.get(name)

    def get_or_raise(self, name: str) -> Callable[..., Any]:
        """
        Retrieve an algorithm by name, raising KeyError if not found.
        """
        algo = self.get(name)
        if algo is None:
            raise KeyError(f"Algorithm '{name}' is not registered")
        return algo

    def get_metadata(self, name: str) -> Optional[AlgorithmMetadata]:
        """
        Retrieve metadata for a registered algorithm.

        Returns:
            The metadata, or None if not found.
        """
        with self._lock:
            return self._metadata.get(name)

    def list_algorithms(self, *, sort: bool = True) -> List[str]:
        """
        List all registered algorithm names.

        Args:
            sort: If True, return names sorted ascending.

        Returns:
            Names of all registered algorithms.
        """
        with self._lock:
            names = list(self._algorithms.keys())
        return sorted(names) if sort else names

    def list_metadata(self, *, sort: bool = True) -> List[AlgorithmMetadata]:
        """
        List metadata for all registered algorithms.
        """
        with self._lock:
            metas = list(self._metadata.values())
        return sorted(metas, key=lambda m: m.name) if sort else metas

    def find_by_tag(self, tag: str) -> List[str]:
        """
        Find algorithm names that contain the given tag (case-insensitive).
        """
        t = tag.strip().lower()
        with self._lock:
            return [
                name
                for name, meta in self._metadata.items()
                if any(t == s.lower() for s in meta.tags)
            ]


# Example algorithm template
def algorithm_template(data: Any, *args: Any, **kwargs: Any) -> Any:
    """
    Template for a new algorithm.

    Args:
        data: Input data to process.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        The result of the algorithm.

    Example:
        result = algorithm_template([1, 2, 3])
    """
    # TODO: Implement algorithm logic here
    raise NotImplementedError("This is a template. Implement your algorithm here.")


# Example: Registering a simple bubble sort algorithm (optimized with early exit)
def bubble_sort(arr: Sequence[T]) -> List[T]:
    """
    Bubble Sort Algorithm (with early-exit optimization).

    Args:
        arr: Sequence of comparable items to sort.

    Returns:
        A new list containing the sorted items (ascending).
    """
    n = len(arr)
    result: List[T] = list(arr)
    if n < 2:
        return result

    for i in range(n - 1):
        swapped = False
        # After each outer pass, the largest element is at the end
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break
    return result


bubble_sort_metadata = AlgorithmMetadata(
    name="bubble_sort",
    description="A simple comparison-based sorting algorithm.",
    complexity="O(n^2)",
    tags=["sorting", "comparison sort"],
    author="<your-name>",
)

# Instantiate a registry and register the example algorithm
algorithm_registry = AlgorithmRegistry()
algorithm_registry.register("bubble_sort", bubble_sort, bubble_sort_metadata)

# Usage example (uncomment to use):
# sorted_list = algorithm_registry.get_or_raise("bubble_sort")([5, 2, 9, 1])
# print(sorted_list)
def create_algorithm():
    return None