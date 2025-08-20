
"""
algorithm_wizard.use_cases
--------------------------

This module provides example use cases and demonstrations for algorithms
created or managed by the Algorithm Wizard plugin.

Each use case is designed to illustrate how to utilize algorithm creation,
selection, and execution within the Wumbo framework. These examples can be
used as references for developers, testers, or as templates for new
algorithmic workflows.


"""

from .algorithm_creator import create_algorithm  # Example import, to be implemented
from .algorithm_selector import select_algorithm  # Example import, to be implemented

def use_case_sorting():
    """
    Demonstrates the creation and execution of a sorting algorithm.

    This use case shows how to:
    1. Create a new sorting algorithm (e.g., bubble sort).
    2. Select the algorithm for a given problem.
    3. Execute the algorithm on sample data.

    Returns:
        dict: A dictionary containing the algorithm name, input data, and sorted output.
    """
    # Example input data
    data = [5, 2, 9, 1, 5, 6]

    # Step 1: Create a bubble sort algorithm (stub function)
    bubble_sort = create_algorithm("bubble_sort")

    # Step 2: Select the best algorithm for sorting (stub function)
    selected_algorithm = select_algorithm(problem_type="sorting", data=data)

    # Step 3: Execute the selected algorithm
    if selected_algorithm:
        result = selected_algorithm(data)
    else:
        # Fallback to bubble_sort if selector returns None
        result = bubble_sort(data)

    return {
        "algorithm": selected_algorithm.__name__ if selected_algorithm else "bubble_sort",
        "input": data,
        "output": result
    }

def use_case_searching():
    """
    Demonstrates the creation and execution of a searching algorithm.

    This use case shows how to:
    1. Create a new searching algorithm (e.g., linear search).
    2. Select the algorithm for a given search problem.
    3. Execute the algorithm on sample data.

    Returns:
        dict: A dictionary containing the algorithm name, input data, search target, and result index.
    """
    # Example input data
    data = [10, 23, 45, 70, 11, 15]
    target = 70

    # Step 1: Create a linear search algorithm (stub function)
    linear_search = create_algorithm("linear_search")

    # Step 2: Select the best algorithm for searching (stub function)
    selected_algorithm = select_algorithm(problem_type="searching", data=data, target=target)

    # Step 3: Execute the selected algorithm
    if selected_algorithm:
        result = selected_algorithm(data, target)
    else:
        # Fallback to linear_search if selector returns None
        result = linear_search(data, target)

    return {
        "algorithm": selected_algorithm.__name__ if selected_algorithm else "linear_search",
        "input": data,
        "target": target,
        "result_index": result
    }

def use_case_custom_algorithm():
    """
    Demonstrates how to define and use a custom algorithm within the framework.

    This use case shows how to:
    1. Define a custom algorithm as a Python function.
    2. Register or use the algorithm directly.
    3. Execute the algorithm on sample data.

    Returns:
        dict: A dictionary containing the algorithm name, input data, and output.
    """
    # Step 1: Define a custom algorithm (e.g., sum of squares)
    def sum_of_squares(data):
        """
        Computes the sum of squares of a list of numbers.

        Args:
            data (list): List of numerical values.

        Returns:
            int or float: Sum of squares of the input values.
        """
        return sum(x ** 2 for x in data)

    # Example input data
    data = [1, 2, 3, 4]

    # Step 2: (Optional) Register the algorithm in the framework (not implemented here)

    # Step 3: Execute the custom algorithm
    result = sum_of_squares(data)

    return {
        "algorithm": "sum_of_squares",
        "input": data,
        "output": result
    }

# Additional use cases can be added below following the same structure.
# Each use case should be self-contained and demonstrate a practical scenario
# for algorithm creation, selection, or execution within the Wumbo framework.

if __name__ == "__main__":
    # Example: Run all use cases and print results for demonstration/testing
    print("Sorting Use Case:", use_case_sorting())
    print("Searching Use Case:", use_case_searching())
    print("Custom Algorithm Use Case:", use_case_custom_algorithm())
