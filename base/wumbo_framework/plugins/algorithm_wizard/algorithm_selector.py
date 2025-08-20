
"""
algorithm_selector.py

This module provides utilities for selecting appropriate algorithms based on user requirements,
problem characteristics, or data properties. It is designed to help users, developers, or automated
systems choose the most suitable algorithm for a given task, such as sorting, searching, optimization,
graph processing, etc.

The selection process can be interactive (prompting the user for details), rule-based (using heuristics),
or data-driven (using metadata or even ML models in advanced scenarios).


"""

from typing import Any, Dict, List, Optional, Callable

# Example: Metadata for available algorithms
ALGORITHM_CATALOG = [
    {
        "name": "QuickSort",
        "type": "sorting",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(log n)",
        "stable": False,
        "in_place": True,
        "best_for": ["large datasets", "average case performance"],
        "limitations": ["not stable", "worst case O(n^2)"],
    },
    {
        "name": "MergeSort",
        "type": "sorting",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)",
        "stable": True,
        "in_place": False,
        "best_for": ["linked lists", "stability required"],
        "limitations": ["extra space required"],
    },
    # Add more algorithms as needed...
]

def list_algorithms(algorithm_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all available algorithms, optionally filtered by type.

    Args:
        algorithm_type (str, optional): The type of algorithm to filter by (e.g., 'sorting', 'searching').

    Returns:
        List[Dict[str, Any]]: List of algorithm metadata dictionaries.
    """
    if algorithm_type:
        return [algo for algo in ALGORITHM_CATALOG if algo["type"] == algorithm_type]
    return ALGORITHM_CATALOG

def select_algorithm(
    problem_type: str,
    constraints: Optional[Dict[str, Any]] = None,
    custom_filter: Optional[Callable[[Dict[str, Any]], bool]] = None
) -> List[Dict[str, Any]]:
    """
    Select algorithms that match the given problem type and constraints.

    Args:
        problem_type (str): The type of problem (e.g., 'sorting', 'searching').
        constraints (dict, optional): Constraints such as 'stable', 'in_place', 'time_complexity', etc.
        custom_filter (Callable, optional): A custom filter function that takes an algorithm metadata dict
                                            and returns True if it should be included.

    Returns:
        List[Dict[str, Any]]: List of matching algorithm metadata dictionaries.

    Example:
        select_algorithm(
            problem_type='sorting',
            constraints={'stable': True, 'in_place': False}
        )
    """
    candidates = list_algorithms(problem_type)
    if constraints:
        for key, value in constraints.items():
            candidates = [algo for algo in candidates if algo.get(key) == value]
    if custom_filter:
        candidates = [algo for algo in candidates if custom_filter(algo)]
    return candidates

def recommend_algorithm(
    problem_type: str,
    constraints: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Recommend a single best-fit algorithm for the given problem type and constraints.

    This function uses a simple heuristic: it returns the first matching algorithm.
    In a more advanced implementation, this could use scoring, ML models, or user feedback.

    Args:
        problem_type (str): The type of problem (e.g., 'sorting', 'searching').
        constraints (dict, optional): Constraints such as 'stable', 'in_place', etc.

    Returns:
        dict or None: The recommended algorithm metadata, or None if no match is found.
    """
    matches = select_algorithm(problem_type, constraints)
    if matches:
        return matches[0]
    return None

# Example usage (for demonstration and testing)
if __name__ == "__main__":
    print("Available sorting algorithms:")
    for algo in list_algorithms("sorting"):
        print(f"- {algo['name']} (Stable: {algo['stable']}, In-place: {algo['in_place']})")

    print("\nSelecting stable, out-of-place sorting algorithms:")
    selected = select_algorithm("sorting", {"stable": True, "in_place": False})
    for algo in selected:
        print(f"- {algo['name']}")

    print("\nRecommended algorithm for stable, out-of-place sorting:")
    recommendation = recommend_algorithm("sorting", {"stable": True, "in_place": False})
    if recommendation:
        print(f"Recommended: {recommendation['name']}")
    else:
        print("No suitable algorithm found.")
