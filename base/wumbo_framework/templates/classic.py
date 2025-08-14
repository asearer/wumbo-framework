"""
🌀 Wumbo Framework - Classic Wumbo Template

This module provides the classic wumbo function as a specialized template
within the framework. This is the original universal function template
that started it all, now integrated into the modular framework.
"""

from typing import Any, Dict, List, Optional, Callable
from ..core.base import BaseTemplate, TemplateMetadata, TemplateType, ExecutionContext
from ..core.registry import auto_register


@auto_register(name="classic_wumbo", aliases=["wumbo", "classic", "universal"])
class ClassicWumboTemplate(BaseTemplate):
    """
    The classic wumbo template - a universal, highly adaptable function template.

    This template serves as a flexible base for a wide variety of Python use cases:
    - Data transformation
    - Functional mapping
    - ETL-like workflows
    - Lightweight pipelines
    - Rapid prototyping
    """

    def __init__(self,
                 preprocess: Optional[Callable] = None,
                 operation: Optional[Callable] = None,
                 postprocess: Optional[Callable] = None,
                 fail_silently: bool = True,
                 as_dict: bool = False,
                 as_single: bool = False,
                 verbose: bool = True,
                 **config):
        """
        Initialize the classic wumbo template.

        Args:
            preprocess: A function to apply to each input before the main operation
            operation: A core function applied to each preprocessed input
            postprocess: A function applied to the list of results after the main operation
            fail_silently: If True, errors during processing are caught and replaced with None
            as_dict: If True, returns results as a dictionary of form {"item_i": result}
            as_single: If True and only one result, return it as a single item, not a list
            verbose: If True, prints execution logs (classic wumbo behavior)
            **config: Additional configuration parameters
        """
        self.preprocess_func = preprocess
        self.operation_func = operation
        self.postprocess_func = postprocess
        self.fail_silently = fail_silently
        self.as_dict = as_dict
        self.as_single = as_single
        self.verbose = verbose
        super().__init__(**config)

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="classic_wumbo",
            version="1.0.0",
            description="The original universal function template - Swiss Army knife for Python functions",
            author="Wumbo Development Team",
            template_type=TemplateType.DATA_PROCESSOR,
            tags=["universal", "data", "processing", "transformation", "classic", "swiss-army-knife"],
            supports_async=False,
            supports_streaming=False
        )

    def _validate_config(self):
        """Validate the template configuration."""
        if self.preprocess_func and not callable(self.preprocess_func):
            raise ValueError("preprocess must be callable")
        if self.operation_func and not callable(self.operation_func):
            raise ValueError("operation must be callable")
        if self.postprocess_func and not callable(self.postprocess_func):
            raise ValueError("postprocess must be callable")

    def _preprocess(self, *args, context: ExecutionContext, **kwargs):
        """Apply preprocessing to input arguments."""
        if self.verbose:
            print("🌀 Wumbo initiated...")
            print("Args received:", args)
            print("Kwargs received:", kwargs)

        if self.preprocess_func:
            preprocessed_args = tuple(self.preprocess_func(arg) for arg in args)
            if self.verbose:
                print("Preprocessed Args:", preprocessed_args)
            return preprocessed_args

        return args

    def _execute_core(self, *args, context: ExecutionContext, **kwargs) -> List[Any]:
        """Execute the main operation logic."""
        results = []

        for arg in args:
            try:
                # Use custom operation if provided, otherwise passthrough
                if self.operation_func and callable(self.operation_func):
                    result = self.operation_func(arg)
                else:
                    result = arg  # Default passthrough behavior
                results.append(result)

            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Error processing {arg}: {e}")

                if self.fail_silently:
                    results.append(None)
                else:
                    raise  # Re-raise exception if fail_silently is False

        return results

    def _postprocess(self, result: List[Any], context: ExecutionContext) -> Any:
        """Apply postprocessing to the results."""
        # Apply postprocessing function if provided
        if self.postprocess_func:
            result = self.postprocess_func(result)

        # Apply output formatting
        if self.as_dict:
            # Return results as a dictionary
            return {f"item_{i}": val for i, val in enumerate(result)}

        if self.as_single and len(result) == 1:
            # Return single item if only one exists
            return result[0]

        # Default return: list of results
        return result


# Convenience factory function
def create_classic_wumbo(preprocess: Optional[Callable] = None,
                        operation: Optional[Callable] = None,
                        postprocess: Optional[Callable] = None,
                        fail_silently: bool = True,
                        as_dict: bool = False,
                        as_single: bool = False,
                        verbose: bool = True,
                        **config) -> ClassicWumboTemplate:
    """
    Create a classic wumbo template instance.

    Args:
        preprocess: Function to apply to each input before main operation
        operation: Core function to apply to each preprocessed input
        postprocess: Function to apply to the final result list
        fail_silently: If True, errors are caught and replaced with None
        as_dict: If True, returns results as a dictionary
        as_single: If True and only one result, returns the item instead of a list
        verbose: If True, prints execution logs
        **config: Additional configuration

    Returns:
        Configured ClassicWumboTemplate instance

    Examples:
        >>> # Basic usage
        >>> wumbo = create_classic_wumbo()
        >>> wumbo(1, 2, 3)
        [1, 2, 3]

        >>> # With operations
        >>> wumbo = create_classic_wumbo(operation=lambda x: x ** 2)
        >>> wumbo(2, 4, 6)
        [4, 16, 36]

        >>> # Full pipeline
        >>> wumbo = create_classic_wumbo(
        ...     preprocess=str.upper,
        ...     operation=lambda x: f"[{x}]",
        ...     postprocess=lambda results: " | ".join(results)
        ... )
        >>> wumbo("hello", "world")
        "[HELLO] | [WORLD]"
    """
    return ClassicWumboTemplate(
        preprocess=preprocess,
        operation=operation,
        postprocess=postprocess,
        fail_silently=fail_silently,
        as_dict=as_dict,
        as_single=as_single,
        verbose=verbose,
        **config
    )


# Convenience function that matches the original wumbo API
def wumbo(*args, **kwargs):
    """
    Classic wumbo function - maintains backward compatibility with original API.

    This function creates a ClassicWumboTemplate instance and executes it immediately,
    providing the same interface as the original wumbo function while leveraging
    the full framework infrastructure.

    Args:
        *args: Positional arguments to process
        **kwargs: Keyword arguments for configuration and processing functions

    Returns:
        Processed results according to configuration

    Examples:
        >>> # Basic usage
        >>> wumbo(1, 2, 3)
        [1, 2, 3]

        >>> # Apply a function
        >>> wumbo(2, 4, 6, operation=lambda x: x ** 2)
        [4, 16, 36]

        >>> # Preprocess and postprocess
        >>> wumbo("hello", "world",
        ...       preprocess=str.upper,
        ...       operation=lambda x: f"[{x}]",
        ...       postprocess=lambda results: " | ".join(results))
        "[HELLO] | [WORLD]"
    """
    # Extract template configuration from kwargs
    template_kwargs = {
        'preprocess': kwargs.pop('preprocess', None),
        'operation': kwargs.pop('operation', None),
        'postprocess': kwargs.pop('postprocess', None),
        'fail_silently': kwargs.pop('fail_silently', True),
        'as_dict': kwargs.pop('as_dict', False),
        'as_single': kwargs.pop('as_single', False),
        'verbose': kwargs.pop('verbose', True)
    }

    # Create template instance
    template = create_classic_wumbo(**template_kwargs)

    # Execute and return result
    result = template.execute(*args, **kwargs)

    if not result.success:
        raise result.error

    return result.data
