
"""
structure_creator.py

This module provides utilities and templates for generating and managing data structures
within the Wumbo framework. It is designed to help users programmatically create, customize,
and extend common and advanced data structures for use in algorithms, pipelines, or educational tools.



-------------------------------------------------------------------------------

Module Overview:
----------------
- Factory functions for standard data structures (e.g., Stack, Queue, LinkedList, Tree, Graph).
- Utilities for dynamic data structure generation based on user specifications.
- Extensible base classes for custom data structure creation.
- Example usage and extension points.

-------------------------------------------------------------------------------

Usage Example:
--------------
>>> from structure_creator import create_stack, create_queue
>>> stack = create_stack()
>>> stack.push(10)
>>> stack.pop()
10

>>> queue = create_queue()
>>> queue.enqueue(5)
>>> queue.dequeue()
5

-------------------------------------------------------------------------------
"""

from typing import Any, Optional, List, Dict, Callable

# =========================
# Stack Implementation
# =========================

class Stack:
    """
    A simple stack (LIFO) data structure.

    Methods:
        push(item): Add an item to the top of the stack.
        pop(): Remove and return the top item from the stack.
        peek(): Return the top item without removing it.
        is_empty(): Check if the stack is empty.
        size(): Return the number of items in the stack.
    """
    def __init__(self):
        self._items: List[Any] = []

    def push(self, item: Any) -> None:
        """Add an item to the top of the stack."""
        self._items.append(item)

    def pop(self) -> Any:
        """Remove and return the top item from the stack. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> Any:
        """Return the top item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Check if the stack is empty."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the number of items in the stack."""
        return len(self._items)

def create_stack() -> Stack:
    """
    Factory function to create a new Stack instance.

    Returns:
        Stack: A new stack object.
    """
    return Stack()

# =========================
# Queue Implementation
# =========================

class Queue:
    """
    A simple queue (FIFO) data structure.

    Methods:
        enqueue(item): Add an item to the end of the queue.
        dequeue(): Remove and return the front item from the queue.
        peek(): Return the front item without removing it.
        is_empty(): Check if the queue is empty.
        size(): Return the number of items in the queue.
    """
    def __init__(self):
        self._items: List[Any] = []

    def enqueue(self, item: Any) -> None:
        """Add an item to the end of the queue."""
        self._items.append(item)

    def dequeue(self) -> Any:
        """Remove and return the front item from the queue. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._items.pop(0)

    def peek(self) -> Any:
        """Return the front item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._items[0]

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the number of items in the queue."""
        return len(self._items)

def create_queue() -> Queue:
    """
    Factory function to create a new Queue instance.

    Returns:
        Queue: A new queue object.
    """
    return Queue()

# =========================
# Linked List Implementation
# =========================

class LinkedListNode:
    """
    Node for singly linked list.

    Attributes:
        value: The value stored in the node.
        next: Reference to the next node in the list.
    """
    def __init__(self, value: Any):
        self.value = value
        self.next: Optional['LinkedListNode'] = None

class LinkedList:
    """
    A simple singly linked list data structure.

    Methods:
        append(value): Add a value to the end of the list.
        prepend(value): Add a value to the start of the list.
        find(value): Find the first node with the given value.
        delete(value): Delete the first node with the given value.
        to_list(): Convert the linked list to a Python list.
    """
    def __init__(self):
        self.head: Optional[LinkedListNode] = None

    def append(self, value: Any) -> None:
        """Add a value to the end of the list."""
        new_node = LinkedListNode(value)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def prepend(self, value: Any) -> None:
        """Add a value to the start of the list."""
        new_node = LinkedListNode(value)
        new_node.next = self.head
        self.head = new_node

    def find(self, value: Any) -> Optional[LinkedListNode]:
        """Find the first node with the given value."""
        current = self.head
        while current:
            if current.value == value:
                return current
            current = current.next
        return None

    def delete(self, value: Any) -> bool:
        """Delete the first node with the given value. Returns True if deleted."""
        current = self.head
        prev = None
        while current:
            if current.value == value:
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                return True
            prev = current
            current = current.next
        return False

    def to_list(self) -> List[Any]:
        """Convert the linked list to a Python list."""
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result

def create_linked_list() -> LinkedList:
    """
    Factory function to create a new LinkedList instance.

    Returns:
        LinkedList: A new linked list object.
    """
    return LinkedList()

# =========================
# Extension Points
# =========================

# You can add more data structures here, such as Trees, Graphs, Heaps, etc.
# For advanced use, consider using abstract base classes or protocols for interface consistency.

# =========================
# Dynamic Data Structure Generator (Example)
# =========================

def create_custom_structure(
    base_class: type,
    methods: Dict[str, Callable]
) -> Any:
    """
    Dynamically create a new data structure class with custom methods.

    Args:
        base_class (type): The base class to inherit from (e.g., object, Stack).
        methods (dict): Dictionary of method names to function implementations.

    Returns:
        type: A new class with the specified methods.

    Example:
        def double_push(self, item):
            self.push(item)
            self.push(item)
        DoubleStack = create_custom_structure(Stack, {'double_push': double_push})
        ds = DoubleStack()
        ds.double_push(5)
    """
    return type('CustomStructure', (base_class,), methods)

# =========================
# Example Usage (for testing)
# =========================

if __name__ == "__main__":
    # Stack example
    stack = create_stack()
    stack.push(1)
    stack.push(2)
    print("Stack pop:", stack.pop())  # Output: 2

    # Queue example
    queue = create_queue()
    queue.enqueue('a')
    queue.enqueue('b')
    print("Queue dequeue:", queue.dequeue())  # Output: 'a'

    # LinkedList example
    ll = create_linked_list()
    ll.append(10)
    ll.prepend(5)
    print("LinkedList to list:", ll.to_list())  # Output: [5, 10]

    # Custom structure example
    def double_push(self, item):
        self.push(item)
        self.push(item)
    DoubleStack = create_custom_structure(Stack, {'double_push': double_push})
    ds = DoubleStack()
    ds.double_push(7)
    print("DoubleStack pop:", ds.pop())  # Output: 7
