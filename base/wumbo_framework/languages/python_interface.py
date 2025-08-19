"""
🌀 Wumbo Framework - Python Language Interface

This module provides the Python language interface implementation,
enabling Python templates to be executed within the multi-language
framework with enhanced capabilities and security features.
"""

import ast
import sys
import io
import contextlib
import traceback
import types
import importlib
import inspect
from typing import Any, Dict, List, Optional, Set
import json
import logging

from ..core import (
    LanguageInterface, SupportedLanguage, LanguageRuntime,
    SerializationConfig, ExecutionEnvironment, SecuritySandbox,
    DataSerializer, ProcessExecutionMixin, language_interface
)
from ..core.base import ExecutionContext


@language_interface(SupportedLanguage.PYTHON)
class PythonInterface(LanguageInterface, ProcessExecutionMixin):
    """
    Python language interface for executing Python templates.

    This interface provides enhanced Python execution with security features,
    import restrictions, and seamless integration with the Wumbo framework.
    """

    def __init__(self, runtime: LanguageRuntime, serialization: SerializationConfig):
        super().__init__(runtime, serialization)
        self.serializer = DataSerializer(serialization)
        self.allowed_imports = set()
        self.restricted_imports = {
            'os', 'sys', 'subprocess', 'importlib', 'exec', 'eval',
            'open', '__import__', '__builtins__', 'compile'
        }
        self.safe_builtins = self._create_safe_builtins()

    def validate_code(self, code: str) -> bool:
        """
        Validate Python code syntax and security.

        Args:
            code: Python source code to validate

        Returns:
            True if code is valid and safe
        """
        try:
            # Parse AST to check syntax
            tree = ast.parse(code)

            # Security validation
            validator = PythonSecurityValidator(self.restricted_imports)
            validator.visit(tree)

            if validator.violations:
                self.logger.warning(f"Security violations found: {validator.violations}")
                return False

            return True

        except SyntaxError as e:
            self.logger.error(f"Syntax error in Python code: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Code validation failed: {e}")
            return False

    def prepare_execution(self, code: str, input_data: Any, context: ExecutionContext) -> Dict[str, Any]:
        """
        Prepare Python code and data for execution.

        Args:
            code: Python source code
            input_data: Input data for the template
            context: Execution context

        Returns:
            Dictionary with prepared execution parameters
        """
        # Create execution wrapper
        wrapper_code = self._create_execution_wrapper(code)

        # Prepare globals with restricted builtins
        execution_globals = {
            '__builtins__': self.safe_builtins,
            '__name__': '__wumbo_template__',
            '__doc__': None,
            '__package__': None,
        }

        # Add Wumbo utilities
        execution_globals.update(self._get_wumbo_utilities())

        # Prepare locals with input data
        execution_locals = {
            'wumbo_input': input_data,
            'wumbo_context': self._prepare_context_data(context),
            'wumbo_result': None
        }

        return {
            'code': wrapper_code,
            'globals': execution_globals,
            'locals': execution_locals,
            'input_data': input_data,
            'context': context
        }

    def execute_template(self, prepared_execution: Dict[str, Any]) -> Any:
        """
        Execute the prepared Python template.

        Args:
            prepared_execution: Prepared execution parameters

        Returns:
            Template execution result
        """
        code = prepared_execution['code']
        exec_globals = prepared_execution['globals']
        exec_locals = prepared_execution['locals']
        context = prepared_execution['context']

        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            # Redirect output
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Execute code in sandbox
            with SecuritySandbox(ExecutionEnvironment(self.runtime, sandbox_enabled=True)):
                exec(code, exec_globals, exec_locals)

            # Get result
            result = exec_locals.get('wumbo_result')

            # Capture output
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()

            if stdout_output:
                context.logger.debug(f"Template stdout: {stdout_output}")
            if stderr_output:
                context.logger.warning(f"Template stderr: {stderr_output}")

            # If no explicit result, return the input transformed
            if result is None:
                result = exec_locals.get('wumbo_input')

            return result

        except Exception as e:
            # Capture any error output
            error_output = stderr_capture.getvalue()
            if error_output:
                context.logger.error(f"Template error output: {error_output}")

            # Re-raise with more context
            raise RuntimeError(f"Python template execution failed: {e}\n{traceback.format_exc()}")

        finally:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def serialize_input(self, data: Any) -> str:
        """Serialize input data for Python execution."""
        return self.serializer.serialize(data)

    def deserialize_output(self, data: str) -> Any:
        """Deserialize output data from Python execution."""
        return self.serializer.deserialize(data)

    def get_supported_features(self) -> List[str]:
        """Get supported features for Python interface."""
        return [
            "basic_execution",
            "data_serialization",
            "security_sandbox",
            "import_restrictions",
            "output_capture",
            "ast_validation",
            "inline_execution",
            "context_integration"
        ]

    def _create_execution_wrapper(self, user_code: str) -> str:
        """
        Create execution wrapper around user code.

        Args:
            user_code: User's Python code

        Returns:
            Wrapped code ready for execution
        """
        wrapper = f'''
# Wumbo Python Template Execution Wrapper
import json

# Extract input data
args = wumbo_input.get('args', ())
kwargs = wumbo_input.get('kwargs', {{}})
context = wumbo_input.get('context', {{}})

# Define helper functions
def wumbo_log(message, level='info'):
    """Log message to template context."""
    print(f"[{{level.upper()}}] {{message}}")

def wumbo_set_result(result):
    """Set the template result."""
    global wumbo_result
    wumbo_result = result

# User code execution
try:
    # User's template code
{self._indent_code(user_code, 4)}

    # If no explicit result was set, try to return processed args
    if wumbo_result is None:
        if 'process' in locals() and callable(locals()['process']):
            wumbo_result = locals()['process'](*args, **kwargs)
        elif 'main' in locals() and callable(locals()['main']):
            wumbo_result = locals()['main'](*args, **kwargs)
        elif 'execute' in locals() and callable(locals()['execute']):
            wumbo_result = locals()['execute'](*args, **kwargs)
        else:
            # Return processed args if available
            wumbo_result = list(args)

except Exception as e:
    wumbo_log(f"Template execution error: {{e}}", 'error')
    raise
'''
        return wrapper

    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code by specified number of spaces."""
        indent = ' ' * spaces
        return '\n'.join(indent + line for line in code.split('\n'))

    def _create_safe_builtins(self) -> Dict[str, Any]:
        """Create safe builtins dictionary for sandboxed execution."""
        # Start with safe built-in functions
        safe_builtins = {
            # Safe data types and functions
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'classmethod', 'complex', 'dict', 'dir', 'divmod',
            'enumerate', 'filter', 'float', 'format', 'frozenset', 'getattr',
            'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance', 'issubclass',
            'iter', 'len', 'list', 'map', 'max', 'min', 'next', 'object',
            'oct', 'ord', 'pow', 'property', 'range', 'repr', 'reversed',
            'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod',
            'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip',
            # Safe exceptions
            'ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException',
            'BlockingIOError', 'BrokenPipeError', 'BufferError', 'BytesWarning',
            'ChildProcessError', 'ConnectionAbortedError', 'ConnectionError',
            'ConnectionRefusedError', 'ConnectionResetError', 'DeprecationWarning',
            'EOFError', 'Ellipsis', 'EnvironmentError', 'Exception', 'False',
            'FileExistsError', 'FileNotFoundError', 'FloatingPointError',
            'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError',
            'ImportWarning', 'IndentationError', 'IndexError', 'InterruptedError',
            'IsADirectoryError', 'KeyError', 'KeyboardInterrupt', 'LookupError',
            'MemoryError', 'NameError', 'None', 'NotADirectoryError',
            'NotImplemented', 'NotImplementedError', 'OSError', 'OverflowError',
            'PendingDeprecationWarning', 'PermissionError', 'ProcessLookupError',
            'RecursionError', 'ReferenceError', 'ResourceWarning', 'RuntimeError',
            'RuntimeWarning', 'StopAsyncIteration', 'StopIteration', 'SyntaxError',
            'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError', 'TimeoutError',
            'True', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError',
            'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError',
            'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning',
            'WindowsError', 'ZeroDivisionError'
        }

        # Get actual builtin objects
        actual_builtins = {}
        for name in safe_builtins:
            if hasattr(__builtins__, name):
                actual_builtins[name] = getattr(__builtins__, name)

        # Add print function (captured)
        actual_builtins['print'] = print

        return actual_builtins

    def _get_wumbo_utilities(self) -> Dict[str, Any]:
        """Get Wumbo utility functions for template execution."""
        import math
        import random
        import string
        import re
        import datetime
        import json

        return {
            # Safe standard library modules
            'math': math,
            'random': random,
            'string': string,
            're': re,
            'datetime': datetime,
            'json': json,

            # Wumbo utilities
            'wumbo_version': '2.0.0',
            'wumbo_safe_eval': self._safe_eval,
            'wumbo_type_check': self._type_check,
            'wumbo_serialize': self.serializer.serialize,
            'wumbo_deserialize': self.serializer.deserialize,
        }

    def _prepare_context_data(self, context: ExecutionContext) -> Dict[str, Any]:
        """Prepare context data for template execution."""
        return {
            'execution_id': context.execution_id,
            'template_name': context.template_name,
            'metadata': dict(context.metadata),
            'config': dict(context.config),
        }

    def _safe_eval(self, expression: str, allowed_names: Optional[Set[str]] = None) -> Any:
        """Safely evaluate a Python expression."""
        if allowed_names is None:
            allowed_names = set()

        try:
            # Parse the expression
            tree = ast.parse(expression, mode='eval')

            # Validate the AST
            validator = ExpressionValidator(allowed_names)
            validator.visit(tree)

            if validator.violations:
                raise ValueError(f"Unsafe expression: {validator.violations}")

            # Evaluate with restricted builtins
            return eval(compile(tree, '<wumbo_safe_eval>', 'eval'),
                       {'__builtins__': self.safe_builtins})

        except Exception as e:
            raise ValueError(f"Expression evaluation failed: {e}")

    def _type_check(self, value: Any, expected_type: Any) -> bool:
        """Check if value matches expected type."""
        try:
            if hasattr(expected_type, '__origin__'):  # Generic types
                return isinstance(value, expected_type.__origin__)
            else:
                return isinstance(value, expected_type)
        except Exception:
            return False


class PythonSecurityValidator(ast.NodeVisitor):
    """AST visitor for validating Python code security."""

    def __init__(self, restricted_imports: Set[str]):
        self.restricted_imports = restricted_imports
        self.violations = []

    def visit_Import(self, node):
        """Check import statements."""
        for alias in node.names:
            if alias.name in self.restricted_imports:
                self.violations.append(f"Restricted import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Check from-import statements."""
        if node.module in self.restricted_imports:
            self.violations.append(f"Restricted import: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        """Check function calls."""
        # Check for dangerous function calls
        if isinstance(node.func, ast.Name):
            if node.func.id in {'eval', 'exec', 'compile', '__import__'}:
                self.violations.append(f"Restricted function call: {node.func.id}")

        # Check for attribute access on restricted modules
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id in self.restricted_imports:
                    self.violations.append(f"Restricted module access: {node.func.value.id}")

        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Check attribute access."""
        if isinstance(node.value, ast.Name):
            # Check access to restricted attributes
            if node.value.id in self.restricted_imports:
                self.violations.append(f"Restricted module access: {node.value.id}")

            # Check access to dangerous attributes
            if node.attr in {'__globals__', '__locals__', '__builtins__', '__import__'}:
                self.violations.append(f"Restricted attribute access: {node.attr}")

        self.generic_visit(node)


class ExpressionValidator(ast.NodeVisitor):
    """Validator for safe expression evaluation."""

    def __init__(self, allowed_names: Set[str]):
        self.allowed_names = allowed_names
        self.violations = []

    def visit_Name(self, node):
        """Check name access."""
        if node.id not in self.allowed_names and not node.id.startswith('wumbo_'):
            # Allow built-in constants
            if node.id not in {'True', 'False', 'None'}:
                self.violations.append(f"Unauthorized name access: {node.id}")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Check attribute access."""
        if isinstance(node.value, ast.Name):
            if node.attr.startswith('_'):
                self.violations.append(f"Private attribute access: {node.attr}")
        self.generic_visit(node)

    def visit_Call(self, node):
        """Check function calls."""
        if isinstance(node.func, ast.Name):
            if node.func.id not in self.allowed_names:
                self.violations.append(f"Unauthorized function call: {node.func.id}")
        self.generic_visit(node)


# Enhanced Python template creation
def create_python_template(code: str,
                         allowed_imports: Optional[List[str]] = None,
                         sandbox_enabled: bool = True,
                         **config) -> 'MultiLanguageTemplate':
    """
    Create a Python template with enhanced security features.

    Args:
        code: Python source code
        allowed_imports: List of allowed import modules
        sandbox_enabled: Whether to enable security sandbox
        **config: Additional configuration

    Returns:
        Configured Python template

    Example:
        >>> template = create_python_template('''
        ... def process(*args):
        ...     return [x * 2 for x in args if isinstance(x, (int, float))]
        ... ''')
        >>> result = template(1, 2, 3, "skip", 4.5)
        >>> # Result: [2, 4, 6, 9.0]
    """
    from .core import create_multi_language_template, SupportedLanguage

    # Configure Python runtime with enhanced security
    runtime_config = config.get('runtime_config')
    if runtime_config and allowed_imports:
        runtime_config.environment_vars['WUMBO_ALLOWED_IMPORTS'] = ','.join(allowed_imports)

    # Configure execution environment
    execution_env = config.get('execution_env')
    if execution_env is None:
        from .core import ExecutionEnvironment, LanguageRuntime
        execution_env = ExecutionEnvironment(
            runtime=runtime_config or LanguageRuntime(
                language=SupportedLanguage.PYTHON,
                interpreter_path="python3",
                version="3.9+",
                additional_args=[],
                environment_vars={}
            ),
            sandbox_enabled=sandbox_enabled,
            network_access=False,
            file_system_access=False
        )

    return create_multi_language_template(
        code=code,
        language=SupportedLanguage.PYTHON,
        execution_env=execution_env,
        **config
    )
