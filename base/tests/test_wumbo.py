import unittest
import json
from wumbo import wumbo


class TestWumbo(unittest.TestCase):
    """Comprehensive tests for the wumbo function."""

    def test_basic_passthrough(self):
        """Test basic passthrough behavior with no operations."""
        result = wumbo(1, 2, 3)
        self.assertEqual(result, [1, 2, 3])

    def test_single_argument(self):
        """Test with a single argument."""
        result = wumbo("hello")
        self.assertEqual(result, ["hello"])

    def test_no_arguments(self):
        """Test with no arguments."""
        result = wumbo()
        self.assertEqual(result, [])

    def test_operation_function(self):
        """Test applying a custom operation function."""
        result = wumbo(2, 4, 6, operation=lambda x: x ** 2)
        self.assertEqual(result, [4, 16, 36])

    def test_preprocess_function(self):
        """Test preprocessing with a function."""
        result = wumbo("hello", "world", preprocess=str.upper)
        self.assertEqual(result, ["HELLO", "WORLD"])

    def test_preprocess_and_operation(self):
        """Test combining preprocess and operation."""
        result = wumbo("hello", "world",
                      preprocess=str.upper,
                      operation=lambda x: f"[{x}]")
        self.assertEqual(result, ["[HELLO]", "[WORLD]"])

    def test_postprocess_function(self):
        """Test postprocessing with a function."""
        result = wumbo(1, 2, 3, postprocess=lambda results: sum(results))
        self.assertEqual(result, 6)

    def test_full_pipeline(self):
        """Test the full preprocessing -> operation -> postprocessing pipeline."""
        result = wumbo("hello", "world",
                      preprocess=str.upper,
                      operation=lambda x: f"[{x}]",
                      postprocess=lambda results: " | ".join(results))
        self.assertEqual(result, "[HELLO] | [WORLD]")

    def test_as_dict_output(self):
        """Test returning results as a dictionary."""
        result = wumbo(100, 200, as_dict=True)
        expected = {'item_0': 100, 'item_1': 200}
        self.assertEqual(result, expected)

    def test_as_single_output(self):
        """Test returning single result as a non-list."""
        result = wumbo(42, as_single=True)
        self.assertEqual(result, 42)

    def test_as_single_multiple_items(self):
        """Test as_single with multiple items (should return list)."""
        result = wumbo(1, 2, 3, as_single=True)
        self.assertEqual(result, [1, 2, 3])

    def test_error_handling_fail_silently_true(self):
        """Test error handling with fail_silently=True (default)."""
        def error_operation(x):
            if x == "error":
                raise ValueError("Test error")
            return x.upper()

        result = wumbo("hello", "error", "world", operation=error_operation)
        self.assertEqual(result, ["HELLO", None, "WORLD"])

    def test_error_handling_fail_silently_false(self):
        """Test error handling with fail_silently=False."""
        def error_operation(x):
            if x == "error":
                raise ValueError("Test error")
            return x.upper()

        with self.assertRaises(ValueError):
            wumbo("hello", "error", "world",
                 operation=error_operation,
                 fail_silently=False)

    def test_json_transformation_example(self):
        """Test JSON transformation example from README."""
        json_str = '{"a": 1, "b": 2}'
        result = wumbo(json_str, operation=lambda x: json.loads(x))
        self.assertEqual(result, [{"a": 1, "b": 2}])

    def test_mathematical_operations_example(self):
        """Test mathematical operations example from README."""
        result = wumbo(3, 6, 9, operation=lambda x: x + 10)
        self.assertEqual(result, [13, 16, 19])

    def test_filtering_mapping_example(self):
        """Test filtering and mapping example from README."""
        result = wumbo("apple", "banana", "cherry",
                      preprocess=str.upper,
                      operation=lambda x: x if "A" in x else None,
                      postprocess=lambda r: list(filter(None, r)))
        self.assertEqual(result, ["APPLE", "BANANA"])

    def test_mixed_data_types(self):
        """Test with mixed data types."""
        result = wumbo(1, "hello", [1, 2, 3], {"key": "value"})
        expected = [1, "hello", [1, 2, 3], {"key": "value"}]
        self.assertEqual(result, expected)

    def test_callable_objects(self):
        """Test with callable objects as arguments."""
        def sample_func():
            return "I'm a function"

        result = wumbo(sample_func, operation=lambda f: f() if callable(f) else f)
        self.assertEqual(result, ["I'm a function"])

    def test_complex_postprocessing(self):
        """Test complex postprocessing scenarios."""
        result = wumbo(1, 2, 3, 4, 5,
                      operation=lambda x: x ** 2,
                      postprocess=lambda results: {
                          'values': results,
                          'sum': sum(results),
                          'count': len(results),
                          'average': sum(results) / len(results)
                      })

        expected = {
            'values': [1, 4, 9, 16, 25],
            'sum': 55,
            'count': 5,
            'average': 11.0
        }
        self.assertEqual(result, expected)

    def test_nested_function_operations(self):
        """Test nested function operations."""
        def double(x):
            return x * 2

        def add_ten(x):
            return x + 10

        def compose_operations(x):
            return add_ten(double(x))

        result = wumbo(1, 2, 3, operation=compose_operations)
        self.assertEqual(result, [12, 14, 16])

    def test_empty_string_handling(self):
        """Test handling of empty strings."""
        result = wumbo("", "hello", "", operation=lambda x: f"'{x}'")
        self.assertEqual(result, ["''", "'hello'", "''"])

    def test_none_values(self):
        """Test handling of None values."""
        result = wumbo(None, "hello", None, operation=lambda x: str(x))
        self.assertEqual(result, ["None", "hello", "None"])


if __name__ == '__main__':
    # Capture print output during tests
    import sys
    import io
    from contextlib import redirect_stdout

    # Run tests with minimal output
    unittest.main(verbosity=2, buffer=True)
