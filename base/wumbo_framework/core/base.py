"""
🌀 Wumbo Framework - Core Base Classes

This module defines the foundational interfaces and base classes for the Wumbo
template framework. It provides the architecture for creating modular, extensible,
and composable templates for any kind of task.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
import logging
import inspect
from functools import wraps

# Type definitions
T = TypeVar('T')
ProcessorFunc = Callable[[Any], Any]
ValidatorFunc = Callable[[Any], bool]
TransformFunc = Callable[[List[Any]], Any]


class TemplateType(Enum):
    """Enumeration of built-in template types."""
    DATA_PROCESSOR = "data_processor"
    API_CLIENT = "api_client"
    WORKFLOW = "workflow"
    TRANSFORMER = "transformer"
    VALIDATOR = "validator"
    AGGREGATOR = "aggregator"
    PIPELINE = "pipeline"
    CUSTOM = "custom"


class ExecutionMode(Enum):
    """Execution modes for templates."""
    SYNC = "synchronous"
    ASYNC = "asynchronous"
    BATCH = "batch"
    STREAMING = "streaming"


@dataclass
class TemplateMetadata:
    """Metadata for template registration and discovery."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    template_type: TemplateType = TemplateType.CUSTOM
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    supports_async: bool = False
    supports_streaming: bool = False


@dataclass
class ExecutionContext:
    """Context object passed through template execution."""
    template_name: str
    execution_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    logger: Optional[logging.Logger] = None

    def __post_init__(self):
        if self.logger is None:
            self.logger = logging.getLogger(f"wumbo.{self.template_name}")


@dataclass
class ExecutionResult:
    """Result object returned from template execution."""
    data: Any
    success: bool = True
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    context: Optional[ExecutionContext] = None


class BaseTemplate(ABC, Generic[T]):
    """
    Abstract base class for all Wumbo templates.

    This class defines the core interface that all templates must implement,
    providing a consistent API for template execution and management.
    """

    def __init__(self, **config):
        """
        Initialize the template with configuration.

        Args:
            **config: Template-specific configuration parameters
        """
        self.config = config
        self.metadata = self._get_metadata()
        self.logger = logging.getLogger(f"wumbo.{self.metadata.name}")
        self._validate_config()

    @abstractmethod
    def _get_metadata(self) -> TemplateMetadata:
        """Return metadata for this template."""
        pass

    @abstractmethod
    def _execute_core(self, *args, context: ExecutionContext, **kwargs) -> T:
        """
        Core execution logic for the template.

        Args:
            *args: Positional arguments
            context: Execution context
            **kwargs: Keyword arguments

        Returns:
            Result of template execution
        """
        pass

    def _validate_config(self):
        """Validate template configuration. Override in subclasses."""
        pass

    def _preprocess(self, *args, context: ExecutionContext, **kwargs) -> tuple:
        """
        Preprocessing hook. Override in subclasses.

        Args:
            *args: Input arguments
            context: Execution context
            **kwargs: Keyword arguments

        Returns:
            Preprocessed arguments tuple
        """
        return args

    def _postprocess(self, result: T, context: ExecutionContext) -> T:
        """
        Postprocessing hook. Override in subclasses.

        Args:
            result: Result from core execution
            context: Execution context

        Returns:
            Postprocessed result
        """
        return result

    def execute(self, *args, context: Optional[ExecutionContext] = None, **kwargs) -> ExecutionResult:
        """
        Execute the template with given arguments.

        Args:
            *args: Positional arguments
            context: Optional execution context
            **kwargs: Keyword arguments

        Returns:
            ExecutionResult containing the result and metadata
        """
        import time
        import uuid

        # Create context if not provided
        if context is None:
            context = ExecutionContext(
                template_name=self.metadata.name,
                execution_id=str(uuid.uuid4()),
                config=self.config.copy()
            )

        start_time = time.time()

        try:
            # Log execution start
            context.logger.debug(f"Starting execution: {context.execution_id}")
            context.logger.debug(f"Args: {args}")
            context.logger.debug(f"Kwargs: {kwargs}")

            # Preprocessing
            preprocessed_args = self._preprocess(*args, context=context, **kwargs)

            # Core execution
            result = self._execute_core(*preprocessed_args, context=context, **kwargs)

            # Postprocessing
            final_result = self._postprocess(result, context)

            execution_time = time.time() - start_time

            context.logger.debug(f"Execution completed in {execution_time:.4f}s")

            return ExecutionResult(
                data=final_result,
                success=True,
                metadata={"execution_time": execution_time},
                execution_time=execution_time,
                context=context
            )

        except Exception as e:
            execution_time = time.time() - start_time
            context.logger.error(f"Execution failed: {e}")

            return ExecutionResult(
                data=None,
                success=False,
                error=e,
                metadata={"execution_time": execution_time, "error_type": type(e).__name__},
                execution_time=execution_time,
                context=context
            )

    def __call__(self, *args, **kwargs) -> Any:
        """Make template callable like a function."""
        result = self.execute(*args, **kwargs)
        if not result.success:
            raise result.error
        return result.data

    def compose(self, other: 'BaseTemplate') -> 'CompositeTemplate':
        """
        Compose this template with another template.

        Args:
            other: Another template to compose with

        Returns:
            CompositeTemplate that chains the two templates
        """
        return CompositeTemplate([self, other])


class CompositeTemplate(BaseTemplate):
    """Template that chains multiple templates together."""

    def __init__(self, templates: List[BaseTemplate], **config):
        """
        Initialize composite template.

        Args:
            templates: List of templates to chain
            **config: Configuration for composite template
        """
        self.templates = templates
        super().__init__(**config)

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name=f"composite_{len(self.templates)}_templates",
            description=f"Composite of {len(self.templates)} templates",
            template_type=TemplateType.PIPELINE
        )

    def _execute_core(self, *args, context: ExecutionContext, **kwargs) -> Any:
        """Execute templates in sequence."""
        current_input = args

        for i, template in enumerate(self.templates):
            context.logger.debug(f"Executing template {i+1}/{len(self.templates)}: {template.metadata.name}")

            if isinstance(current_input, tuple):
                result = template(*current_input, context=context, **kwargs)
            else:
                result = template(current_input, context=context, **kwargs)

            # Prepare input for next template
            if i < len(self.templates) - 1:
                current_input = (result,) if not isinstance(result, tuple) else result

        return result


class TemplateDecorator:
    """Decorator for creating templates from functions."""

    def __init__(self,
                 name: str,
                 template_type: TemplateType = TemplateType.CUSTOM,
                 description: str = "",
                 **metadata_kwargs):
        """
        Initialize template decorator.

        Args:
            name: Name of the template
            template_type: Type of template
            description: Template description
            **metadata_kwargs: Additional metadata
        """
        self.name = name
        self.template_type = template_type
        self.description = description
        self.metadata_kwargs = metadata_kwargs

    def __call__(self, func: Callable) -> BaseTemplate:
        """Convert function to template."""

        class FunctionTemplate(BaseTemplate):
            def __init__(self, **config):
                self.func = func
                super().__init__(**config)

            def _get_metadata(self) -> TemplateMetadata:
                return TemplateMetadata(
                    name=self.name,
                    description=self.description or func.__doc__ or "",
                    template_type=self.template_type,
                    **self.metadata_kwargs
                )

            def _execute_core(self, *args, context: ExecutionContext, **kwargs):
                # Check if function accepts context
                sig = inspect.signature(self.func)
                if 'context' in sig.parameters:
                    return self.func(*args, context=context, **kwargs)
                else:
                    return self.func(*args, **kwargs)

        return FunctionTemplate


# Convenience decorator function
def template(name: str,
            template_type: TemplateType = TemplateType.CUSTOM,
            description: str = "",
            **metadata_kwargs):
    """
    Decorator to convert a function into a Wumbo template.

    Args:
        name: Name of the template
        template_type: Type of template
        description: Template description
        **metadata_kwargs: Additional metadata

    Returns:
        Template decorator
    """
    return TemplateDecorator(name, template_type, description, **metadata_kwargs)


class TemplateError(Exception):
    """Base exception for template-related errors."""
    pass


class TemplateConfigError(TemplateError):
    """Exception raised for template configuration errors."""
    pass


class TemplateExecutionError(TemplateError):
    """Exception raised during template execution."""
    pass


class TemplateRegistrationError(TemplateError):
    """Exception raised during template registration."""
    pass
