"""
🌀 wumbo - A universal, highly adaptable Python function template

wumbo is a Swiss Army knife for Python functions, designed to serve as a flexible
foundation for nearly any task. Whether you're transforming data, executing dynamic
workflows, calling APIs, or prototyping pipelines — wumbo is your go-to tool.

Usage:
    from wumbo import wumbo

    # Basic usage
    result = wumbo(1, 2, 3)

    # With operations
    result = wumbo(2, 4, 6, operation=lambda x: x ** 2)

    # Full pipeline
    result = wumbo("hello", "world",
                  preprocess=str.upper,
                  operation=lambda x: f"[{x}]",
                  postprocess=lambda results: " | ".join(results))

For more examples and documentation, see the README.md file.
"""

from .wumbo import wumbo

__version__ = "1.0.0"
__author__ = "Wumbo Development Team"
__email__ = "dev@wumbo.dev"
__all__ = ["wumbo"]
