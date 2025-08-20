
"""
use_cases.py

This module provides example use cases for various data structures.
It is intended to demonstrate how the data structure wizard's generated or selected
structures can be applied to real-world problems. Each use case is presented as a
function or class with detailed docstrings and comments explaining the scenario,
the choice of data structure, and the implementation details.


"""

# Example 1: Using a Stack for Expression Evaluation

def evaluate_postfix_expression(expression):
    """
    Evaluates a postfix (Reverse Polish Notation) mathematical expression using a stack.

    Args:
        expression (str): The postfix expression, with tokens separated by spaces.
                          Example: "3 4 + 2 * 7 /"

    Returns:
        float: The result of the evaluated expression.

    Use Case:
        Stacks are ideal for evaluating postfix expressions because they allow
        for efficient last-in, first-out (LIFO) management of operands.

    Example:
        >>> evaluate_postfix_expression("3 4 + 2 * 7 /")
        2.0
    """
    stack = []
    tokens = expression.split()
    for token in tokens:
        if token.isdigit():
            stack.append(float(token))
        else:
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                stack.append(a / b)
            else:
                raise ValueError(f"Unknown operator: {token}")
    return stack.pop() if stack else None

# Example 2: Using a Queue for Task Scheduling

from collections import deque

def schedule_tasks(tasks):
    """
    Simulates a simple task scheduler using a queue (FIFO).

    Args:
        tasks (list of str): List of task names to be scheduled.

    Returns:
        list of str: The order in which tasks are executed.

    Use Case:
        Queues are commonly used in scheduling scenarios where tasks must be
        processed in the order they arrive (first-in, first-out).

    Example:
        >>> schedule_tasks(['task1', 'task2', 'task3'])
        ['task1', 'task2', 'task3']
    """
    queue = deque(tasks)
    execution_order = []
    while queue:
        current_task = queue.popleft()
        # Simulate task execution
        execution_order.append(current_task)
    return execution_order

# Example 3: Using a Hash Map for Fast Lookup

def count_word_frequencies(text):
    """
    Counts the frequency of each word in a given text using a hash map (dictionary).

    Args:
        text (str): Input text.

    Returns:
        dict: Mapping from word to its frequency.

    Use Case:
        Hash maps (dictionaries) provide O(1) average-case lookup and update times,
        making them ideal for frequency counting and other associative array tasks.

    Example:
        >>> count_word_frequencies("hello world hello")
        {'hello': 2, 'world': 1}
    """
    freq = {}
    for word in text.split():
        freq[word] = freq.get(word, 0) + 1
    return freq

# Example 4: Using a Binary Search Tree for Sorted Data

class TreeNode:
    """
    Node for a simple binary search tree (BST).
    """
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

def insert_bst(root, value):
    """
    Inserts a value into the BST.

    Args:
        root (TreeNode): The root of the BST.
        value (any): The value to insert.

    Returns:
        TreeNode: The root of the BST after insertion.
    """
    if root is None:
        return TreeNode(value)
    if value < root.value:
        root.left = insert_bst(root.left, value)
    else:
        root.right = insert_bst(root.right, value)
    return root

def inorder_traversal(root):
    """
    Performs an in-order traversal of the BST.

    Args:
        root (TreeNode): The root of the BST.

    Returns:
        list: Sorted list of values in the BST.
    """
    if root is None:
        return []
    return inorder_traversal(root.left) + [root.value] + inorder_traversal(root.right)

# Example 5: Using a Graph for Pathfinding

def build_graph(edges):
    """
    Builds an adjacency list representation of a graph.

    Args:
        edges (list of tuple): Each tuple is (from_node, to_node).

    Returns:
        dict: Adjacency list of the graph.
    """
    graph = {}
    for src, dst in edges:
        if src not in graph:
            graph[src] = []
        graph[src].append(dst)
    return graph

def bfs_shortest_path(graph, start, goal):
    """
    Finds the shortest path between start and goal nodes using BFS.

    Args:
        graph (dict): Adjacency list of the graph.
        start (any): Starting node.
        goal (any): Goal node.

    Returns:
        list: The shortest path from start to goal, or [] if no path exists.

    Use Case:
        Graphs are essential for representing networks, and BFS is a classic
        algorithm for finding shortest paths in unweighted graphs.

    Example:
        >>> g = build_graph([('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D')])
        >>> bfs_shortest_path(g, 'A', 'D')
        ['A', 'B', 'D']
    """
    from collections import deque
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in graph.get(node, []):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    return []

# Additional use cases can be added below following the same pattern:
# - Describe the scenario and why the data structure is appropriate.
# - Provide a function or class with detailed docstrings and comments.
