"""
🌀 Wumbo Framework - Universal Template System
===============================================

The Wumbo Framework is a modular, extensible system for creating templates
that can handle any kind of task. Think of it as a Swiss Army knife for
Python functions, but organized as a complete framework.

Key Features:
- Modular template architecture
- Plugin system for extensibility
- Built-in template registry
- Composition and chaining capabilities
- Async and batch processing support
- Comprehensive error handling and logging

Quick Start:
-----------

1. Use the classic wumbo function (backward compatible):
   ```python
   from wumbo_framework import wumbo
   result = wumbo(1, 2, 3, operation=lambda x: x ** 2)
   ```

2. Use specific template types:
   ```python
   from wumbo_framework import create_data_processor, create_api_client

   processor = create_data_processor(operation=lambda x: x.upper())
   result = processor("hello", "world")
   ```

3. Use the template registry:
   ```python
   from wumbo_framework import get_template, list_templates

   wumbo = get_template("classic_wumbo")
   available = list_templates()
   ```

4. Create custom templates:
   ```python
   from wumbo_framework import BaseTemplate, template, register_template

   @template("my_template")
   class MyTemplate(BaseTemplate):
       # ... implementation
   ```

Architecture Overview:
---------------------

Core Components:
- BaseTemplate: Abstract base class for all templates
- TemplateRegistry: Central registry for template management
- ExecutionContext: Context object for template execution
- Built-in Templates: Pre-built templates for common use cases

Template Types:
- DataProcessorTemplate: Data transformation and processing
- APIClientTemplate: HTTP API client with retries
- ValidationTemplate: Data validation with custom validators
- AggregatorTemplate: Data aggregation and grouping
- BatchProcessorTemplate: Batch processing with optional parallelism
- TransformTemplate: Map and filter operations
- WorkflowTemplate: Multi-step workflows with conditions
- ClassicWumboTemplate: The original wumbo function

Framework Structure:
- core/: Core framework classes and interfaces
- templates/: Built-in template implementations
- plugins/: Plugin system for extensibility
- utils/: Utility functions and helpers
"""

__version__ = "2.0.0"
__author__ = "Wumbo Development Team"
__email__ = "dev@wumbo.dev"

# Core imports
from .core.base import (
    BaseTemplate,
    TemplateMetadata,
    TemplateType,
    ExecutionMode,
    ExecutionContext,
    ExecutionResult,
    CompositeTemplate,
    template,
    TemplateError,
    TemplateConfigError,
    TemplateExecutionError,
    TemplateRegistrationError
)

from .core.registry import (
    TemplateRegistry,
    get_registry,
    register_template,
    get_template,
    list_templates,
    search_templates,
    auto_register
)

# Built-in templates
from .templates.builtins import (
    DataProcessorTemplate,
    APIClientTemplate,
    ValidationTemplate,
    AggregatorTemplate,
    BatchProcessorTemplate,
    TransformTemplate,
    WorkflowTemplate,
    create_data_processor,
    create_api_client,
    create_validator,
    create_aggregator,
    create_batch_processor,
    create_transformer,
    create_workflow
)

# Classic wumbo template
from .templates.classic import (
    ClassicWumboTemplate,
    create_classic_wumbo,
    wumbo  # The classic function for backward compatibility
)

# Multi-language support
from .languages import (
    create_template as create_multi_language_template,
    python_template,
    javascript_template,
    typescript_template,
    go_template,
    shell_template,
    get_available_languages,
    get_language_info,
    get_multi_language_info,
    validate_template_code,
    SupportedLanguage,
    MultiLanguageTemplate
)

# Initialize framework
def _initialize_framework():
    """Initialize the framework with built-in templates and multi-language support."""
    registry = get_registry()

    # Register built-in templates
    try:
        registry.register(DataProcessorTemplate, "data_processor", ["processor", "dp"])
        registry.register(APIClientTemplate, "api_client", ["api", "client"])
        registry.register(ValidationTemplate, "validator", ["validate", "check"])
        registry.register(AggregatorTemplate, "aggregator", ["agg", "aggregate"])
        registry.register(BatchProcessorTemplate, "batch_processor", ["batch", "bp"])
        registry.register(TransformTemplate, "transformer", ["transform", "map_filter"])
        registry.register(WorkflowTemplate, "workflow", ["wf", "pipeline"])
        # ClassicWumboTemplate is auto-registered via decorator

        # Register multi-language template
        registry.register(MultiLanguageTemplate, "multi_language", ["multilang", "ml"])

    except Exception as e:
        import logging
        logger = logging.getLogger("wumbo_framework")
        logger.warning(f"Failed to register some built-in templates: {e}")

    # Initialize multi-language support
    try:
        from . import languages
        # Multi-language support is auto-initialized on import
        logger = logging.getLogger("wumbo_framework")
        available_langs = get_available_languages()
        if available_langs:
            logger.info(f"Multi-language support enabled for: {', '.join(available_langs)}")
        else:
            logger.warning("No additional language runtimes detected beyond Python")
    except Exception as e:
        import logging
        logger = logging.getLogger("wumbo_framework")
        logger.warning(f"Failed to initialize multi-language support: {e}")

# Initialize on import
_initialize_framework()

# Convenience functions for common operations
def create_template(template_type: str, **config) -> BaseTemplate:
    """
    Create a template instance by type name.

    Args:
        template_type: Name or alias of the template type
        **config: Configuration parameters for the template

    Returns:
        Configured template instance

    Example:
        >>> processor = create_template("data_processor", operation=lambda x: x * 2)
        >>> result = processor(1, 2, 3)
    """
    return get_template(template_type, **config)

def discover_templates(module_or_path: str) -> int:
    """
    Discover and register templates from a module or path.

    Args:
        module_or_path: Python module name or file system path

    Returns:
        Number of templates discovered and registered

    Example:
        >>> count = discover_templates("my_custom_templates")
        >>> print(f"Discovered {count} custom templates")
    """
    registry = get_registry()

    # If it's a path, add it as a plugin path and load plugins
    try:
        from pathlib import Path
        path = Path(module_or_path)
        if path.exists():
            registry.add_plugin_path(path)
            return registry.load_plugins()
    except:
        pass

    # Otherwise, treat as module name
    return registry.discover_templates(module_or_path)

def compose_templates(*templates) -> CompositeTemplate:
    """
    Compose multiple templates into a pipeline.

    Args:
        *templates: Template instances or names to compose

    Returns:
        CompositeTemplate that chains the templates

    Example:
        >>> step1 = create_template("transformer", map_func=str.upper)
        >>> step2 = create_template("data_processor", operation=lambda x: f"[{x}]")
        >>> pipeline = compose_templates(step1, step2)
        >>> result = pipeline("hello", "world")
    """
    template_instances = []

    for template in templates:
        if isinstance(template, str):
            # If string, get template from registry
            template_instances.append(get_template(template))
        elif isinstance(template, BaseTemplate):
            template_instances.append(template)
        else:
            raise ValueError(f"Invalid template type: {type(template)}")

    return CompositeTemplate(template_instances)

# Framework information
def get_framework_info() -> dict:
    """
    Get information about the framework.

    Returns:
        Dictionary with framework information
    """
    registry = get_registry()
    stats = registry.get_stats()

    # Get multi-language info
    try:
        multi_lang_info = get_multi_language_info()
    except:
        multi_lang_info = {"error": "Multi-language support not available"}

    return {
        "version": __version__,
        "author": __author__,
        "registry_stats": stats,
        "available_templates": list_templates(),
        "template_types": [t.value for t in TemplateType],
        "multi_language": multi_lang_info
    }

# Export all public symbols
__all__ = [
    # Core classes
    "BaseTemplate",
    "TemplateMetadata",
    "TemplateType",
    "ExecutionMode",
    "ExecutionContext",
    "ExecutionResult",
    "CompositeTemplate",
    "template",

    # Registry
    "TemplateRegistry",
    "get_registry",
    "register_template",
    "get_template",
    "list_templates",
    "search_templates",
    "auto_register",

    # Built-in templates
    "DataProcessorTemplate",
    "APIClientTemplate",
    "ValidationTemplate",
    "AggregatorTemplate",
    "BatchProcessorTemplate",
    "TransformTemplate",
    "WorkflowTemplate",
    "ClassicWumboTemplate",

    # Factory functions
    "create_data_processor",
    "create_api_client",
    "create_validator",
    "create_aggregator",
    "create_batch_processor",
    "create_transformer",
    "create_workflow",
    "create_classic_wumbo",

    # Classic function
    "wumbo",

    # Convenience functions
    "create_template",
    "discover_templates",
    "compose_templates",
    "get_framework_info",

    # Multi-language support
    "create_multi_language_template",
    "python_template",
    "javascript_template",
    "typescript_template",
    "go_template",
    "shell_template",
    "get_available_languages",
    "get_language_info",
    "get_multi_language_info",
    "validate_template_code",
    "SupportedLanguage",
    "MultiLanguageTemplate",

    # Exceptions
    "TemplateError",
    "TemplateConfigError",
    "TemplateExecutionError",
    "TemplateRegistrationError"
]
