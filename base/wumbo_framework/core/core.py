"""
🌀 Wumbo Framework - Multi-Language Core System

This module provides the core abstractions for multi-language template support,
enabling templates to be written in different programming languages while
maintaining a unified interface and execution model.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Type, Callable
from dataclasses import dataclass
from enum import Enum
import json
import subprocess
import tempfile
import os
from pathlib import Path
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

from ..core.base import BaseTemplate, TemplateMetadata, TemplateType, ExecutionContext, ExecutionResult


class SupportedLanguage(Enum):
    """Enumeration of supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    C = "c"
    PHP = "php"
    RUBY = "ruby"
    KOTLIN = "kotlin"
    SCALA = "scala"
    R = "r"
    JULIA = "julia"
    LUA = "lua"
    PERL = "perl"
    SHELL = "shell"
    POWERSHELL = "powershell"


@dataclass
class LanguageRuntime:
    """Configuration for a specific language runtime."""
    language: SupportedLanguage
    interpreter_path: str
    version: str
    additional_args: List[str]
    environment_vars: Dict[str, str]
    working_directory: Optional[str] = None
    timeout: int = 300  # 5 minutes default
    max_memory_mb: int = 1024  # 1GB default


@dataclass
class ExecutionEnvironment:
    """Environment configuration for template execution."""
    runtime: LanguageRuntime
    sandbox_enabled: bool = True
    network_access: bool = False
    file_system_access: bool = False
    allowed_imports: List[str] = None
    resource_limits: Dict[str, Any] = None


@dataclass
class SerializationConfig:
    """Configuration for data serialization between languages."""
    format: str = "json"  # json, msgpack, protobuf, avro
    encoding: str = "utf-8"
    compression: Optional[str] = None  # gzip, lzma, bz2
    custom_serializers: Dict[Type, Callable] = None


class LanguageInterface(ABC):
    """
    Abstract interface for language-specific template execution.

    Each supported language must implement this interface to provide
    standardized execution capabilities within the Wumbo framework.
    """

    def __init__(self, runtime: LanguageRuntime, serialization: SerializationConfig):
        self.runtime = runtime
        self.serialization = serialization
        self.logger = logging.getLogger(f"wumbo.lang.{runtime.language.value}")

    @abstractmethod
    def validate_code(self, code: str) -> bool:
        """
        Validate template code syntax without executing it.

        Args:
            code: Source code to validate

        Returns:
            True if code is syntactically valid
        """
        pass

    @abstractmethod
    def prepare_execution(self, code: str, input_data: Any, context: ExecutionContext) -> Dict[str, Any]:
        """
        Prepare code and data for execution in the target language.

        Args:
            code: Source code to execute
            input_data: Input data to pass to the template
            context: Execution context

        Returns:
            Dictionary with prepared execution parameters
        """
        pass

    @abstractmethod
    def execute_template(self, prepared_execution: Dict[str, Any]) -> Any:
        """
        Execute the prepared template code.

        Args:
            prepared_execution: Prepared execution parameters

        Returns:
            Execution result
        """
        pass

    @abstractmethod
    def serialize_input(self, data: Any) -> str:
        """
        Serialize input data for the target language.

        Args:
            data: Python data to serialize

        Returns:
            Serialized data string
        """
        pass

    @abstractmethod
    def deserialize_output(self, data: str) -> Any:
        """
        Deserialize output data from the target language.

        Args:
            data: Serialized data string

        Returns:
            Deserialized Python data
        """
        pass

    def get_supported_features(self) -> List[str]:
        """Get list of supported features for this language interface."""
        return ["basic_execution", "data_serialization"]

    def cleanup(self):
        """Cleanup resources after template execution."""
        pass


class MultiLanguageTemplate(BaseTemplate):
    """
    Template that can execute code written in different programming languages.

    This template acts as a bridge between the Wumbo framework and external
    language runtimes, providing a unified interface while maintaining
    language-specific capabilities.
    """

    def __init__(self,
                 code: str,
                 language: SupportedLanguage,
                 runtime_config: Optional[LanguageRuntime] = None,
                 serialization_config: Optional[SerializationConfig] = None,
                 execution_env: Optional[ExecutionEnvironment] = None,
                 **config):
        """
        Initialize multi-language template.

        Args:
            code: Source code in the specified language
            language: Programming language of the code
            runtime_config: Language runtime configuration
            serialization_config: Data serialization configuration
            execution_env: Execution environment configuration
            **config: Additional template configuration
        """
        self.code = code
        self.language = language
        self.runtime_config = runtime_config or self._get_default_runtime(language)
        self.serialization_config = serialization_config or SerializationConfig()
        self.execution_env = execution_env or ExecutionEnvironment(self.runtime_config)

        # Get language interface
        self.language_interface = LanguageInterfaceRegistry.get_interface(
            language, self.runtime_config, self.serialization_config
        )

        super().__init__(**config)

        # Validate code during initialization
        if not self.language_interface.validate_code(self.code):
            raise ValueError(f"Invalid {language.value} code provided")

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name=f"multi_lang_{self.language.value}_template",
            description=f"Multi-language template executing {self.language.value} code",
            template_type=TemplateType.CUSTOM,
            version="1.0.0",
            tags=["multi-language", self.language.value, "polyglot"],
            supports_async=False,
            supports_streaming=False
        )

    def _get_default_runtime(self, language: SupportedLanguage) -> LanguageRuntime:
        """Get default runtime configuration for a language."""
        runtime_configs = {
            SupportedLanguage.PYTHON: LanguageRuntime(
                language=language,
                interpreter_path="python3",
                version="3.9+",
                additional_args=[],
                environment_vars={}
            ),
            SupportedLanguage.JAVASCRIPT: LanguageRuntime(
                language=language,
                interpreter_path="node",
                version="16+",
                additional_args=[],
                environment_vars={}
            ),
            SupportedLanguage.JAVA: LanguageRuntime(
                language=language,
                interpreter_path="java",
                version="11+",
                additional_args=["-cp", "."],
                environment_vars={}
            ),
            SupportedLanguage.GO: LanguageRuntime(
                language=language,
                interpreter_path="go",
                version="1.18+",
                additional_args=["run"],
                environment_vars={}
            ),
            SupportedLanguage.RUST: LanguageRuntime(
                language=language,
                interpreter_path="rustc",
                version="1.60+",
                additional_args=["--edition", "2021"],
                environment_vars={}
            ),
        }

        return runtime_configs.get(language, LanguageRuntime(
            language=language,
            interpreter_path=language.value,
            version="latest",
            additional_args=[],
            environment_vars={}
        ))

    def _execute_core(self, *args, context: ExecutionContext, **kwargs) -> Any:
        """Execute the multi-language template."""
        try:
            # Prepare input data
            input_data = {
                "args": args,
                "kwargs": kwargs,
                "context": {
                    "execution_id": context.execution_id,
                    "template_name": context.template_name,
                    "metadata": context.metadata
                }
            }

            # Prepare execution
            prepared = self.language_interface.prepare_execution(
                self.code, input_data, context
            )

            # Execute template
            context.logger.debug(f"Executing {self.language.value} template")
            result = self.language_interface.execute_template(prepared)

            return result

        except Exception as e:
            context.logger.error(f"Multi-language template execution failed: {e}")
            raise
        finally:
            # Cleanup resources
            self.language_interface.cleanup()


class LanguageInterfaceRegistry:
    """Registry for language interfaces."""

    _interfaces: Dict[SupportedLanguage, Type[LanguageInterface]] = {}
    _instances: Dict[str, LanguageInterface] = {}
    _lock = threading.Lock()

    @classmethod
    def register_interface(cls, language: SupportedLanguage, interface_class: Type[LanguageInterface]):
        """Register a language interface."""
        with cls._lock:
            cls._interfaces[language] = interface_class

    @classmethod
    def get_interface(cls,
                     language: SupportedLanguage,
                     runtime: LanguageRuntime,
                     serialization: SerializationConfig) -> LanguageInterface:
        """Get or create a language interface instance."""
        cache_key = f"{language.value}_{hash(str(runtime))}_{hash(str(serialization))}"

        with cls._lock:
            if cache_key not in cls._instances:
                if language not in cls._interfaces:
                    raise ValueError(f"No interface registered for language: {language.value}")

                interface_class = cls._interfaces[language]
                cls._instances[cache_key] = interface_class(runtime, serialization)

            return cls._instances[cache_key]

    @classmethod
    def list_supported_languages(cls) -> List[SupportedLanguage]:
        """List all supported languages."""
        return list(cls._interfaces.keys())

    @classmethod
    def is_language_supported(cls, language: SupportedLanguage) -> bool:
        """Check if a language is supported."""
        return language in cls._interfaces


class ProcessExecutionMixin:
    """Mixin providing process-based execution utilities."""

    def execute_process(self,
                       command: List[str],
                       input_data: Optional[str] = None,
                       timeout: int = 300,
                       cwd: Optional[str] = None,
                       env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Execute a process with proper error handling and resource management.

        Args:
            command: Command and arguments to execute
            input_data: Data to send to stdin
            timeout: Execution timeout in seconds
            cwd: Working directory
            env: Environment variables

        Returns:
            Dictionary with execution results
        """
        try:
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)

            # Execute process
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                env=process_env
            )

            # Communicate with process
            stdout, stderr = process.communicate(input=input_data, timeout=timeout)

            return {
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "success": process.returncode == 0
            }

        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise RuntimeError(f"Process execution timed out after {timeout} seconds")
        except Exception as e:
            raise RuntimeError(f"Process execution failed: {e}")


class SecuritySandbox:
    """Security sandbox for executing untrusted code."""

    def __init__(self, config: ExecutionEnvironment):
        self.config = config
        self.temp_dir = None
        self.original_cwd = None

    def __enter__(self):
        """Enter sandbox environment."""
        if self.config.sandbox_enabled:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            self.original_cwd = os.getcwd()
            os.chdir(self.temp_dir)

            # Set resource limits (if supported)
            self._set_resource_limits()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit sandbox environment."""
        if self.config.sandbox_enabled and self.original_cwd:
            os.chdir(self.original_cwd)

            # Cleanup temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _set_resource_limits(self):
        """Set resource limits for sandboxed execution."""
        try:
            import resource

            # Set memory limit
            if self.config.resource_limits and "max_memory_mb" in self.config.resource_limits:
                max_memory = self.config.resource_limits["max_memory_mb"] * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))

            # Set CPU time limit
            if self.config.resource_limits and "max_cpu_seconds" in self.config.resource_limits:
                max_cpu = self.config.resource_limits["max_cpu_seconds"]
                resource.setrlimit(resource.RLIMIT_CPU, (max_cpu, max_cpu))

        except ImportError:
            # Resource module not available (e.g., on Windows)
            pass
        except Exception as e:
            logging.warning(f"Failed to set resource limits: {e}")


class DataSerializer:
    """Universal data serializer for multi-language communication."""

    def __init__(self, config: SerializationConfig):
        self.config = config

    def serialize(self, data: Any) -> str:
        """Serialize Python data for inter-language communication."""
        if self.config.format == "json":
            return json.dumps(data, default=self._json_default, ensure_ascii=False)
        elif self.config.format == "msgpack":
            import msgpack
            return msgpack.packb(data, default=self._msgpack_default).decode('latin-1')
        else:
            raise ValueError(f"Unsupported serialization format: {self.config.format}")

    def deserialize(self, data: str) -> Any:
        """Deserialize data from inter-language communication."""
        if self.config.format == "json":
            return json.loads(data)
        elif self.config.format == "msgpack":
            import msgpack
            return msgpack.unpackb(data.encode('latin-1'), raw=False)
        else:
            raise ValueError(f"Unsupported deserialization format: {self.config.format}")

    def _json_default(self, obj):
        """Default JSON serializer for complex objects."""
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, '_asdict'):
            return obj._asdict()
        else:
            return str(obj)

    def _msgpack_default(self, obj):
        """Default MessagePack serializer for complex objects."""
        return self._json_default(obj)


# Factory functions for creating multi-language templates
def create_multi_language_template(code: str,
                                 language: Union[str, SupportedLanguage],
                                 **config) -> MultiLanguageTemplate:
    """
    Factory function to create multi-language templates.

    Args:
        code: Source code in the specified language
        language: Programming language (string or enum)
        **config: Additional configuration

    Returns:
        Configured MultiLanguageTemplate instance

    Example:
        >>> js_template = create_multi_language_template(
        ...     code="function process(data) { return data.map(x => x * 2); }",
        ...     language="javascript"
        ... )
    """
    if isinstance(language, str):
        try:
            language = SupportedLanguage(language.lower())
        except ValueError:
            raise ValueError(f"Unsupported language: {language}")

    return MultiLanguageTemplate(code=code, language=language, **config)


def list_supported_languages() -> List[str]:
    """Get list of all supported programming languages."""
    return [lang.value for lang in LanguageInterfaceRegistry.list_supported_languages()]


def is_language_supported(language: Union[str, SupportedLanguage]) -> bool:
    """Check if a programming language is supported."""
    if isinstance(language, str):
        try:
            language = SupportedLanguage(language.lower())
        except ValueError:
            return False

    return LanguageInterfaceRegistry.is_language_supported(language)


# Decorator for registering language interfaces
def language_interface(language: Union[str, SupportedLanguage]):
    """Decorator to register language interfaces."""
    if isinstance(language, str):
        language = SupportedLanguage(language.lower())

    def decorator(cls: Type[LanguageInterface]) -> Type[LanguageInterface]:
        LanguageInterfaceRegistry.register_interface(language, cls)
        return cls

    return decorator
