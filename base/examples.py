#!/usr/bin/env python3
"""
🌀 wumbo Examples

This file demonstrates various usage patterns for the wumbo function.
Run this script to see wumbo in action with different scenarios.
"""

import json
import math
from wumbo import wumbo


def separator(title):
    """Print a formatted separator for examples."""
    print(f"\n{'='*50}")
    print(f"🔥 {title}")
    print('='*50)


def example_basic_usage():
    """Demonstrate basic wumbo usage."""
    separator("Basic Usage")

    print("Simple passthrough:")
    result = wumbo(1, 2, 3)
    print(f"wumbo(1, 2, 3) = {result}")

    print("\nSingle argument:")
    result = wumbo("hello world")
    print(f"wumbo('hello world') = {result}")

    print("\nEmpty call:")
    result = wumbo()
    print(f"wumbo() = {result}")


def example_operations():
    """Demonstrate operation functions."""
    separator("Operation Functions")

    print("Mathematical operations:")
    result = wumbo(2, 4, 6, operation=lambda x: x ** 2)
    print(f"Square numbers: {result}")

    result = wumbo(3, 6, 9, operation=lambda x: x + 10)
    print(f"Add 10: {result}")

    print("\nString operations:")
    result = wumbo("hello", "world", operation=str.upper)
    print(f"Uppercase: {result}")

    result = wumbo("python", "is", "awesome", operation=lambda x: f"[{x}]")
    print(f"Bracket wrap: {result}")


def example_preprocessing():
    """Demonstrate preprocessing."""
    separator("Preprocessing")

    print("String preprocessing:")
    result = wumbo("hello", "WORLD", "PyThOn",
                  preprocess=str.lower,
                  operation=lambda x: x.capitalize())
    print(f"Normalize case: {result}")

    print("\nNumeric preprocessing:")
    result = wumbo("10", "20", "30.5",
                  preprocess=float,
                  operation=lambda x: x / 2)
    print(f"Convert and halve: {result}")


def example_postprocessing():
    """Demonstrate postprocessing."""
    separator("Postprocessing")

    print("Join results:")
    result = wumbo("hello", "beautiful", "world",
                  preprocess=str.upper,
                  operation=lambda x: f"[{x}]",
                  postprocess=lambda results: " | ".join(results))
    print(f"Joined output: {result}")

    print("\nAggregate results:")
    result = wumbo(1, 2, 3, 4, 5,
                  operation=lambda x: x ** 2,
                  postprocess=lambda results: {
                      'values': results,
                      'sum': sum(results),
                      'max': max(results),
                      'min': min(results)
                  })
    print(f"Statistics: {result}")


def example_output_formats():
    """Demonstrate different output formats."""
    separator("Output Formats")

    print("Default list output:")
    result = wumbo(100, 200, 300)
    print(f"List: {result}")

    print("\nDictionary output:")
    result = wumbo(100, 200, 300, as_dict=True)
    print(f"Dict: {result}")

    print("\nSingle item output:")
    result = wumbo(42, as_single=True)
    print(f"Single: {result}")

    print("\nMultiple items with as_single (returns list):")
    result = wumbo(1, 2, 3, as_single=True)
    print(f"Multiple with as_single: {result}")


def example_error_handling():
    """Demonstrate error handling."""
    separator("Error Handling")

    def risky_operation(x):
        if x == "error":
            raise ValueError("Intentional error!")
        return x.upper()

    print("Fail silently (default):")
    result = wumbo("hello", "error", "world", operation=risky_operation)
    print(f"With error handling: {result}")

    print("\nFail loudly:")
    try:
        result = wumbo("hello", "error", "world",
                      operation=risky_operation,
                      fail_silently=False)
    except ValueError as e:
        print(f"Caught exception: {e}")


def example_json_processing():
    """Demonstrate JSON data processing."""
    separator("JSON Processing")

    json_data = ['{"name": "Alice", "age": 30}',
                 '{"name": "Bob", "age": 25}',
                 '{"name": "Charlie", "age": 35}']

    print("Parse JSON strings:")
    result = wumbo(*json_data, operation=json.loads)
    print(f"Parsed data: {result}")

    print("\nExtract names:")
    result = wumbo(*json_data,
                  operation=json.loads,
                  postprocess=lambda results: [person["name"] for person in results])
    print(f"Names: {result}")

    print("\nCalculate average age:")
    result = wumbo(*json_data,
                  operation=json.loads,
                  postprocess=lambda results: sum(person["age"] for person in results) / len(results))
    print(f"Average age: {result}")


def example_data_pipeline():
    """Demonstrate a data processing pipeline."""
    separator("Data Pipeline")

    # Raw CSV-like data
    csv_rows = ["Alice,30,Engineer", "Bob,25,Designer", "Charlie,35,Manager"]

    print("Process CSV data:")
    result = wumbo(*csv_rows,
                  # Parse CSV row
                  preprocess=lambda row: row.split(","),
                  # Create person object
                  operation=lambda fields: {
                      "name": fields[0],
                      "age": int(fields[1]),
                      "role": fields[2]
                  },
                  # Create summary
                  postprocess=lambda people: {
                      "count": len(people),
                      "people": people,
                      "avg_age": sum(p["age"] for p in people) / len(people),
                      "roles": list(set(p["role"] for p in people))
                  })

    print(f"Pipeline result: {json.dumps(result, indent=2)}")


def example_functional_composition():
    """Demonstrate functional programming patterns."""
    separator("Functional Composition")

    def multiply_by_2(x):
        return x * 2

    def add_10(x):
        return x + 10

    def to_string(x):
        return f"Result: {x}"

    print("Compose multiple operations:")
    result = wumbo(1, 2, 3, 4, 5,
                  operation=lambda x: to_string(add_10(multiply_by_2(x))))
    print(f"Composed operations: {result}")


def example_filtering():
    """Demonstrate filtering patterns."""
    separator("Filtering")

    words = ["apple", "banana", "apricot", "blueberry", "avocado", "cherry"]

    print("Filter words starting with 'a':")
    result = wumbo(*words,
                  operation=lambda x: x if x.startswith('a') else None,
                  postprocess=lambda results: list(filter(None, results)))
    print(f"A-words: {result}")

    print("Filter and transform:")
    result = wumbo(*words,
                  preprocess=str.upper,
                  operation=lambda x: f"✓ {x}" if len(x) <= 5 else None,
                  postprocess=lambda results: list(filter(None, results)))
    print(f"Short words: {result}")


def example_mathematical():
    """Demonstrate mathematical operations."""
    separator("Mathematical Operations")

    numbers = [1, 4, 9, 16, 25, 36]

    print("Square roots:")
    result = wumbo(*numbers, operation=math.sqrt)
    print(f"Square roots: {result}")

    print("Complex calculation:")
    result = wumbo(*numbers,
                  operation=lambda x: math.sqrt(x) * 2,
                  postprocess=lambda results: {
                      "values": [round(x, 2) for x in results],
                      "sum": round(sum(results), 2),
                      "product": round(math.prod(results), 2)
                  })
    print(f"Complex math: {result}")


def main():
    """Run all examples."""
    print("🌀 WUMBO EXAMPLES SHOWCASE")
    print("Demonstrating the versatility of the wumbo function")

    example_basic_usage()
    example_operations()
    example_preprocessing()
    example_postprocessing()
    example_output_formats()
    example_error_handling()
    example_json_processing()
    example_data_pipeline()
    example_functional_composition()
    example_filtering()
    example_mathematical()

    separator("Examples Complete!")
    print("🎉 All examples have been demonstrated!")
    print("Try modifying these examples or create your own wumbo patterns!")


if __name__ == "__main__":
    main()
