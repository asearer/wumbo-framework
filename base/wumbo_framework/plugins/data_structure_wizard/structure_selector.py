Wumbo/base/wumbo_framework/plugins/data_structure_wizard/structure_selector.py
"""
structure_selector.py

This module provides utilities for selecting the most appropriate data structure
for a given problem or set of requirements. It is designed to assist users in
choosing between common data structures (such as lists, sets, dictionaries, trees, etc.)
based on their use case, performance needs, and data characteristics.

The selection logic can be extended to include custom data structures or advanced
decision-making algorithms.


"""

from typing import Any, Dict, List, Optional

class DataStructureRecommendation:
    """
    Represents a recommendation for a data structure, including rationale and
    relevant properties.
    """
    def __init__(self, name: str, rationale: str, properties: Optional[Dict[str, Any]] = None):
        """
        Initialize a recommendation.

        Args:
            name (str): Name of the recommended data structure.
            rationale (str): Explanation for the recommendation.
            properties (Optional[Dict[str, Any]]): Additional properties or metadata.
        """
        self.name = name
        self.rationale = rationale
        self.properties = properties or {}

    def __repr__(self):
        return f"<DataStructureRecommendation name={self.name} rationale={self.rationale}>"

def select_data_structure(
    needs_fast_lookup: bool = False,
    needs_ordered: bool = False,
    needs_unique: bool = False,
    needs_hierarchical: bool = False,
    data_size: Optional[int] = None,
    custom_requirements: Optional[Dict[str, Any]] = None
) -> DataStructureRecommendation:
    """
    Selects an appropriate data structure based on the provided requirements.

    Args:
        needs_fast_lookup (bool): If True, prioritize structures with O(1) or O(log n) lookup.
        needs_ordered (bool): If True, maintain insertion or sorted order.
        needs_unique (bool): If True, enforce uniqueness of elements.
        needs_hierarchical (bool): If True, support parent-child relationships (e.g., trees).
        data_size (Optional[int]): Expected number of elements (may influence choice).
        custom_requirements (Optional[Dict[str, Any]]): Additional custom requirements.

    Returns:
        DataStructureRecommendation: The recommended data structure and rationale.

    Example:
        >>> select_data_structure(needs_fast_lookup=True, needs_unique=True)
        <DataStructureRecommendation name='set' rationale='Provides O(1) lookup and enforces uniqueness.'>
    """
    # Example decision logic (expand as needed)
    if needs_hierarchical:
        return DataStructureRecommendation(
            name="tree",
            rationale="Supports hierarchical (parent-child) relationships.",
            properties={"type": "general tree"}
        )
    if needs_fast_lookup and needs_unique:
        return DataStructureRecommendation(
            name="set",
            rationale="Provides O(1) average-case lookup and enforces uniqueness.",
            properties={"lookup": "O(1)", "unique": True}
        )
    if needs_fast_lookup and not needs_unique:
        return DataStructureRecommendation(
            name="dict",
            rationale="Provides O(1) average-case key-based lookup and allows value association.",
            properties={"lookup": "O(1)", "unique_keys": True}
        )
    if needs_ordered and not needs_unique:
        return DataStructureRecommendation(
            name="list",
            rationale="Maintains insertion order and allows duplicates.",
            properties={"ordered": True, "duplicates": True}
        )
    if needs_ordered and needs_unique:
        return DataStructureRecommendation(
            name="OrderedSet",
            rationale="Maintains insertion order and enforces uniqueness (requires external library or custom implementation).",
            properties={"ordered": True, "unique": True}
        )
    # Fallback/default
    return DataStructureRecommendation(
        name="list",
        rationale="Default to list for general-purpose, ordered, and mutable collections.",
        properties={"ordered": True, "duplicates": True}
    )

def explain_data_structure(name: str) -> str:
    """
    Provides a detailed explanation of a given data structure, including its
    typical use cases, strengths, and weaknesses.

    Args:
        name (str): The name of the data structure (e.g., 'list', 'set', 'dict', 'tree').

    Returns:
        str: A detailed explanation.

    Example:
        >>> explain_data_structure('set')
        'A set is an unordered collection of unique elements...'
    """
    explanations = {
        "list": (
            "A list is an ordered, mutable collection that allows duplicate elements. "
            "Lists are ideal for maintaining sequences of items where order matters, "
            "and support efficient appends and random access."
        ),
        "set": (
            "A set is an unordered collection of unique elements. Sets are useful for "
            "membership testing, removing duplicates, and performing set operations "
            "like union, intersection, and difference. Lookup is typically O(1)."
        ),
        "dict": (
            "A dictionary (dict) is a collection of key-value pairs with unique keys. "
            "Dictionaries provide fast O(1) average-case lookup, insertion, and deletion "
            "by key. Useful for mapping relationships and fast retrieval by identifier."
        ),
        "tree": (
            "A tree is a hierarchical data structure with parent-child relationships. "
            "Trees are used for representing nested or hierarchical data, such as file "
            "systems, organizational charts, and parse trees. Common types include binary trees, "
            "AVL trees, and B-trees."
        ),
        "OrderedSet": (
            "An OrderedSet maintains the uniqueness of elements like a set, but also preserves "
            "the order of insertion. Not built-in to Python, but available via third-party libraries "
            "or custom implementations."
        ),
    }
    return explanations.get(name, "No explanation available for this data structure.")

# Example usage (for demonstration/testing purposes)
if __name__ == "__main__":
    # Select a data structure for fast lookup and uniqueness
    rec = select_data_structure(needs_fast_lookup=True, needs_unique=True)
    print(f"Recommended: {rec.name}")
    print(f"Rationale: {rec.rationale}")
    print(f"Details: {rec.properties}")
    print()
    # Explain a data structure
    print("Explanation for 'set':")
    print(explain_data_structure("set"))
