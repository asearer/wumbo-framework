Wumbo/base/wumbo_framework/plugins/algorithm_wizard/algorithm_creator.py
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

from typing import Callable, Any, Dict, Optional, List

class AlgorithmMetadata:
    """
    Stores metadata about an algorithm for documentation and discovery.

    Attributes:
        name (str): The name of the algorithm.
        description (str): A short description of what the algorithm does.
        complexity (str): Time/space complexity (e.g., "O(n log n)").
        tags (List[str]): Tags for categorization (e.g., ["sorting", "divide and conquer"]).
        author (str): Author or contributor.
    """
    def __init__(
        self,
        name: str,
        description: str,
        complexity: str = "",
        tags: Optional[List[str]] = None,
        author: str = ""
    ):
        self.name = name
        self.description = description
        self.complexity = complexity
        self.tags = tags or []
        self.author = author

    def as_dict(self) -> Dict[str, Any]:
        """Return metadata as a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "complexity": self.complexity,
            "tags": self.tags,
            "author": self.author
        }

class AlgorithmRegistry:
    """
    Registry for storing and retrieving algorithms by name.

    Usage:
        registry = AlgorithmRegistry()
        registry.register("bubble_sort", bubble_sort, metadata)
        algo = registry.get("bubble_sort")
    """
    def __init__(self):
        self._algorithms: Dict[str, Callable] = {}
        self._metadata: Dict[str, AlgorithmMetadata] = {}

    def register(self, name: str, func: Callable, metadata: AlgorithmMetadata):
        """
        Register a new algorithm with its metadata.

        Args:
            name (str): Unique name for the algorithm.
            func (Callable): The algorithm implementation.
            metadata (AlgorithmMetadata): Metadata describing the algorithm.
        """
        self._algorithms[name] = func
        self._metadata[name] = metadata

    def get(self, name: str) -> Optional[Callable]:
        """
        Retrieve an algorithm by name.

        Args:
            name (str): The name of the algorithm.

        Returns:
            Callable or None: The algorithm function, or None if not found.
        """
        return self._algorithms.get(name)

    def get_metadata(self, name: str) -> Optional[AlgorithmMetadata]:
        """
        Retrieve metadata for a registered algorithm.

        Args:
            name (str): The name of the algorithm.

        Returns:
            AlgorithmMetadata or None: Metadata, or None if not found.
        """
        return self._metadata.get(name)

    def list_algorithms(self) -> List[str]:
        """
        List all registered algorithm names.

        Returns:
            List[str]: Names of all registered algorithms.
        """
        return list(self._algorithms.keys())

# Example algorithm template
def algorithm_template(data: Any, *args, **kwargs) -> Any:
    """
    Template for a new algorithm.

    Args:
        data (Any): Input data to process.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        Any: The result of the algorithm.

    Example:
        result = algorithm_template([1, 2, 3])
    """
    # TODO: Implement algorithm logic here
    raise NotImplementedError("This is a template. Implement your algorithm here.")

# Example: Registering a simple bubble sort algorithm
def bubble_sort(arr: List[int]) -> List[int]:
    """
    Bubble Sort Algorithm

    Args:
        arr (List[int]): List of integers to sort.

    Returns:
        List[int]: Sorted list.
    """
    n = len(arr)
    result = arr.copy()
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result

bubble_sort_metadata = AlgorithmMetadata(
    name="bubble_sort",
    description="A simple comparison-based sorting algorithm.",
    complexity="O(n^2)",
    tags=["sorting", "comparison sort"],
    author="[Your Name]"
)

# Instantiate a registry and register the example algorithm
algorithm_registry = AlgorithmRegistry()
algorithm_registry.register("bubble_sort", bubble_sort, bubble_sort_metadata)

# Usage example (uncomment to use):
# sorted_list = algorithm_registry.get("bubble_sort")([5, 2, 9, 1])
# print(sorted_list)

# Note:
# - Extend this module with more algorithm templates and registration patterns as needed.
# - Encourage contributors to provide rich metadata for discoverability and documentation.
