"""
🌀 Wumbo Framework - Multi-Language Support System

This module provides comprehensive multi-language template support for the Wumbo framework,
enabling templates to be written in various programming languages and executed uniformly.

Supported Languages:
- Python: Full native support with security sandboxing
- JavaScript: Node.js execution with npm package support
- TypeScript: Compiled execution with type checking
- Go: Compiled execution with module support
- Shell: Bash/Zsh scripting with utility functions

Features:
- Unified template interface across all languages
- Security sandboxing and resource limits
- Cross-language data serialization
- Runtime detection and validation
- Extensible architecture for adding new languages
"""

import logging
from typing import Dict, List, Optional, Type, Any
from ..core import (
    LanguageInterface,
    LanguageInterfaceRegistry,
    LanguageRuntime,
    SerializationConfig,
    SupportedLanguage,
    MultiLanguageTemplate,
    ExecutionEnvironment,
    SecuritySandbox,
    DataSerializer,
    ProcessExecutionMixin,
    create_multi_language_template,
    list_supported_languages,
    is_language_supported,
    language_interface
)

# Import all language interfaces
from .python_interface import PythonInterface, create_python_template
from .javascript_interface import JavaScriptInterface, create_javascript_template
from .typescript_interface import TypeScriptInterface, create_typescript_template
from .go_interface import GoInterface, create_go_template
from .shell_interface import ShellInterface, create_shell_template

# Logger for multi-language system
logger = logging.getLogger(__name__)

# Registry for quick access
_interfaces_registry = LanguageInterfaceRegistry


def initialize_language_support():
    """
    Initialize all language interfaces and register them with the framework.

    This function automatically detects available language runtimes and
    registers corresponding interfaces. It's called during framework initialization.
    """
    logger.info("Initializing Wumbo multi-language support...")

    # Register all available language interfaces
    interfaces_to_register = [
        (SupportedLanguage.PYTHON, PythonInterface),
        (SupportedLanguage.JAVASCRIPT, JavaScriptInterface),
        (SupportedLanguage.TYPESCRIPT, TypeScriptInterface),
        (SupportedLanguage.GO, GoInterface),
        (SupportedLanguage.SHELL, ShellInterface),
    ]

    registered_count = 0
    for language, interface_class in interfaces_to_register:
        try:
            LanguageInterfaceRegistry.register_interface(language, interface_class)
            registered_count += 1
            logger.debug(f"Registered {language.value} language interface")
        except Exception as e:
            logger.warning(f"Failed to register {language.value} interface: {e}")

    logger.info(f"Multi-language support initialized with {registered_count} languages")

    # Log available languages
    available_languages = get_available_languages()
    if available_languages:
        logger.info(f"Available language runtimes: {', '.join(available_languages)}")
    else:
        logger.warning("No language runtimes detected")


def get_available_languages() -> List[str]:
    """
    Get list of languages with available runtimes on the system.

    Returns:
        List of language names that have working runtimes

    Example:
        >>> available = get_available_languages()
        >>> print(f"Can execute templates in: {', '.join(available)}")
    """
    available = []

    # Check each registered language for runtime availability
    for language in LanguageInterfaceRegistry.list_supported_languages():
        try:
            # Create a default runtime configuration
            runtime = create_default_runtime(language)
            serialization = SerializationConfig()

            # Try to create interface (this will detect the runtime)
            interface_class = LanguageInterfaceRegistry.get_interface(language, runtime, serialization)

            # If we got here, the runtime is available
            available.append(language.value)

        except Exception as e:
            logger.debug(f"{language.value} runtime not available: {e}")
            continue

    return available


def create_default_runtime(language: SupportedLanguage, **overrides) -> LanguageRuntime:
    """
    Create a default runtime configuration for a language.

    Args:
        language: The programming language
        **overrides: Configuration overrides

    Returns:
        LanguageRuntime configured with defaults for the language
    """
    defaults = {
        SupportedLanguage.PYTHON: {
            'interpreter_path': 'python3',
            'version': 'latest',
            'additional_args': ['-u'],  # Unbuffered output
            'environment_vars': {'PYTHONPATH': '.'},
            'timeout': 300,
            'max_memory_mb': 1024
        },
        SupportedLanguage.JAVASCRIPT: {
            'interpreter_path': 'node',
            'version': 'latest',
            'additional_args': [],
            'environment_vars': {'NODE_ENV': 'production'},
            'timeout': 300,
            'max_memory_mb': 1024
        },
        SupportedLanguage.TYPESCRIPT: {
            'interpreter_path': 'node',
            'version': 'latest',
            'additional_args': [],
            'environment_vars': {'NODE_ENV': 'production'},
            'timeout': 300,
            'max_memory_mb': 1024
        },
        SupportedLanguage.GO: {
            'interpreter_path': 'go',
            'version': 'latest',
            'additional_args': [],
            'environment_vars': {'GO111MODULE': 'on'},
            'timeout': 300,
            'max_memory_mb': 1024
        },
        SupportedLanguage.SHELL: {
            'interpreter_path': 'bash',
            'version': 'latest',
            'additional_args': [],
            'environment_vars': {},
            'timeout': 300,
            'max_memory_mb': 512
        }
    }

    config = defaults.get(language, {})
    config.update(overrides)

    return LanguageRuntime(
        language=language,
        interpreter_path=config.get('interpreter_path', ''),
        version=config.get('version', 'latest'),
        additional_args=config.get('additional_args', []),
        environment_vars=config.get('environment_vars', {}),
        working_directory=config.get('working_directory'),
        timeout=config.get('timeout', 300),
        max_memory_mb=config.get('max_memory_mb', 1024)
    )


def create_template(language: str, code: str, **config) -> MultiLanguageTemplate:
    """
    Create a multi-language template with the specified language and code.

    Args:
        language: Programming language name (e.g., 'python', 'javascript')
        code: Template code in the specified language
        **config: Additional configuration options

    Returns:
        MultiLanguageTemplate instance ready for execution

    Example:
        >>> # Python template
        >>> py_template = create_template('python', '''
        ... result = [x * 2 for x in wumbo_args]
        ... wumbo_success(result)
        ... ''')
        >>>
        >>> # JavaScript template
        >>> js_template = create_template('javascript', '''
        ... const result = wumboArgs.map(x => x * 2);
        ... wumbo.success(result);
        ... ''')
        >>>
        >>> # Both templates do the same thing
        >>> print(py_template(1, 2, 3))  # [2, 4, 6]
        >>> print(js_template(1, 2, 3))  # [2, 4, 6]
    """
    # Convert string to enum
    try:
        lang_enum = SupportedLanguage(language.lower())
    except ValueError:
        raise ValueError(f"Unsupported language: {language}. "
                        f"Supported languages: {', '.join([l.value for l in SupportedLanguage])}")

    # Create runtime configuration
    runtime = create_default_runtime(lang_enum, **config)

    # Create serialization configuration
    serialization = SerializationConfig(
        format=config.get('serialization_format', 'json'),
        encoding=config.get('serialization_encoding', 'utf-8'),
        compression=config.get('serialization_compression'),
        custom_serializers=config.get('custom_serializers')
    )

    return MultiLanguageTemplate(
        code=code,
        language=lang_enum,
        runtime=runtime,
        serialization=serialization,
        name=config.get('name', f'{language}_template'),
        description=config.get('description', f'Template written in {language}'),
        metadata=config.get('metadata', {})
    )


def get_language_info(language: str) -> Dict[str, Any]:
    """
    Get information about a specific language support.

    Args:
        language: Programming language name

    Returns:
        Dictionary with language information and capabilities

    Example:
        >>> info = get_language_info('python')
        >>> print(f"Features: {info['features']}")
        >>> print(f"Runtime available: {info['available']}")
    """
    try:
        lang_enum = SupportedLanguage(language.lower())
    except ValueError:
        raise ValueError(f"Unknown language: {language}")

    # Check if runtime is available
    available = language in get_available_languages()

    # Get interface class to query features
    features = []
    runtime_info = {}

    if available:
        try:
            runtime = create_default_runtime(lang_enum)
            serialization = SerializationConfig()
            interface = LanguageInterfaceRegistry.get_interface(lang_enum, runtime, serialization)
            features = interface.get_supported_features()

            # Get runtime version info
            if hasattr(interface, '_get_version'):
                runtime_info['version'] = interface._get_version()
        except Exception as e:
            logger.warning(f"Could not query {language} interface: {e}")

    return {
        'language': language,
        'enum_value': lang_enum.value,
        'available': available,
        'features': features,
        'runtime_info': runtime_info,
        'default_config': create_default_runtime(lang_enum).__dict__ if available else None
    }


def validate_template_code(language: str, code: str) -> bool:
    """
    Validate template code syntax without executing it.

    Args:
        language: Programming language name
        code: Template code to validate

    Returns:
        True if code is syntactically valid, False otherwise

    Example:
        >>> valid = validate_template_code('python', 'print("hello")')
        >>> print(f"Code is valid: {valid}")
    """
    try:
        lang_enum = SupportedLanguage(language.lower())
        runtime = create_default_runtime(lang_enum)
        serialization = SerializationConfig()

        interface = LanguageInterfaceRegistry.get_interface(lang_enum, runtime, serialization)
        return interface.validate_code(code)

    except Exception as e:
        logger.error(f"Validation error for {language}: {e}")
        return False


# Convenience factory functions for each language
def python_template(code: str, **config) -> MultiLanguageTemplate:
    """Create a Python template."""
    return create_template('python', code, **config)


def javascript_template(code: str, **config) -> MultiLanguageTemplate:
    """Create a JavaScript template."""
    return create_template('javascript', code, **config)


def typescript_template(code: str, **config) -> MultiLanguageTemplate:
    """Create a TypeScript template."""
    return create_template('typescript', code, **config)


def go_template(code: str, **config) -> MultiLanguageTemplate:
    """Create a Go template."""
    return create_template('go', code, **config)


def shell_template(code: str, **config) -> MultiLanguageTemplate:
    """Create a shell script template."""
    return create_template('shell', code, **config)


# Framework information
def get_multi_language_info() -> Dict[str, Any]:
    """
    Get comprehensive information about multi-language support.

    Returns:
        Dictionary with framework multi-language capabilities
    """
    return {
        'version': '2.0.0',
        'total_languages': len(SupportedLanguage),
        'registered_interfaces': len(LanguageInterfaceRegistry.list_supported_languages()),
        'available_languages': get_available_languages(),
        'supported_languages': [lang.value for lang in SupportedLanguage],
        'language_details': {
            lang.value: get_language_info(lang.value)
            for lang in SupportedLanguage
        }
    }


# Auto-initialize when module is imported
try:
    initialize_language_support()
except Exception as e:
    logger.error(f"Failed to initialize multi-language support: {e}")

# Export all public symbols
__all__ = [
    # Core classes
    'LanguageInterface',
    'LanguageInterfaceRegistry',
    'LanguageRuntime',
    'SerializationConfig',
    'SupportedLanguage',
    'MultiLanguageTemplate',
    'ExecutionEnvironment',
    'SecuritySandbox',
    'DataSerializer',
    'ProcessExecutionMixin',

    # Language interfaces
    'PythonInterface',
    'JavaScriptInterface',
    'TypeScriptInterface',
    'GoInterface',
    'ShellInterface',

    # Core functions
    'create_multi_language_template',
    'list_supported_languages',
    'is_language_supported',
    'language_interface',

    # Initialization and utilities
    'initialize_language_support',
    'get_available_languages',
    'create_default_runtime',
    'get_language_info',
    'get_multi_language_info',
    'validate_template_code',

    # Template creation functions
    'create_template',
    'python_template',
    'javascript_template',
    'typescript_template',
    'go_template',
    'shell_template',

    # Individual template factories
    'create_python_template',
    'create_javascript_template',
    'create_typescript_template',
    'create_go_template',
    'create_shell_template'
]
