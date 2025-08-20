"""
Wumbo Framework - Shell Scripting Language Interface

This module provides shell scripting language support for the Wumbo framework,
enabling templates to be written in shell script and executed via system shell.
"""

import json
import os
import tempfile
import subprocess
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from ..core import (
    LanguageInterface, LanguageRuntime, SerializationConfig, SupportedLanguage,
    ProcessExecutionMixin, DataSerializer, SecuritySandbox
)
from ..core.base import ExecutionContext, ExecutionResult


class ShellInterface(LanguageInterface, ProcessExecutionMixin):
    """
    Shell scripting language interface for executing shell script templates.

    This interface provides shell script execution with security features,
    environment management, and seamless integration with the Wumbo framework.
    """

    def __init__(self, runtime: LanguageRuntime, serialization: SerializationConfig):
        super().__init__(runtime, serialization)
        self.serializer = DataSerializer(serialization)
        self._shell_path = self._detect_shell_executable()

    def validate_code(self, code: str) -> bool:
        """
        Validate shell script syntax using shell -n option.

        Args:
            code: Shell script code to validate

        Returns:
            True if code is syntactically valid, False otherwise
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Use shell -n to check syntax without executing
                result = subprocess.run(
                    [self._shell_path, '-n', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.returncode == 0
            finally:
                os.unlink(temp_file)
        except Exception as e:
            self.logger.error(f"Shell validation error: {e}")
            return False

    def prepare_execution(self, code: str, context: ExecutionContext) -> str:
        """
        Prepare shell script code for execution by wrapping it with framework utilities.

        Args:
            code: Shell script template code
            context: Execution context with input data and metadata

        Returns:
            Prepared shell script code ready for execution
        """
        # Prepare input data serialization
        input_data = self._prepare_context_data(context)

        # Create execution wrapper with shell utilities
        wrapper = self._create_execution_wrapper(code, input_data)

        return wrapper

    def execute_template(self, prepared_code: str, context: ExecutionContext) -> ExecutionResult:
        """
        Execute prepared shell script code.

        Args:
            prepared_code: Prepared shell script code
            context: Execution context

        Returns:
            ExecutionResult with output data and metadata
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(prepared_code)
                temp_file = f.name

            # Make script executable
            os.chmod(temp_file, 0o755)

            try:
                # Execute with security sandbox if enabled
                if hasattr(context, 'execution_environment') and context.execution_environment.sandbox_enabled:
                    with SecuritySandbox() as sandbox:
                        result = self._execute_shell_script(temp_file, context)
                else:
                    result = self._execute_shell_script(temp_file, context)

                return result
            finally:
                os.unlink(temp_file)

        except Exception as e:
            self.logger.error(f"Shell execution error: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                output=None,
                execution_time=0.0,
                metadata={'language': 'shell', 'error_type': type(e).__name__}
            )

    def serialize_input(self, data: Any) -> str:
        """Serialize input data for shell consumption."""
        return json.dumps(data, ensure_ascii=False, indent=2)

    def deserialize_output(self, data: str) -> Any:
        """Deserialize shell output data."""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data

    def get_supported_features(self) -> List[str]:
        """Get list of supported shell scripting features."""
        return [
            'environment_variables',
            'file_system',
            'process_execution',
            'pipes_and_redirection',
            'pattern_matching',
            'regular_expressions',
            'error_handling',
            'functions',
            'loops_and_conditionals',
            'command_substitution'
        ]

    def _detect_shell_executable(self) -> str:
        """Detect shell executable path."""
        if self.runtime.interpreter_path:
            return self.runtime.interpreter_path

        # Try common shell executables in order of preference
        for shell_cmd in ['bash', 'zsh', 'sh', 'dash']:
            try:
                result = subprocess.run([shell_cmd, '--version'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return shell_cmd
            except FileNotFoundError:
                continue

        # Fallback to system shell
        return os.environ.get('SHELL', '/bin/sh')

    def _execute_shell_script(self, script_path: str, context: ExecutionContext) -> ExecutionResult:
        """Execute shell script and capture results."""
        import time

        start_time = time.time()

        try:
            # Build command
            cmd = [self._shell_path] + self.runtime.additional_args + [script_path]

            # Set up environment
            env = os.environ.copy()
            env.update(self.runtime.environment_vars)

            # Execute process
            result = self.execute_process(
                cmd,
                timeout=self.runtime.timeout,
                cwd=self.runtime.working_directory,
                env=env
            )

            execution_time = time.time() - start_time

            if result['returncode'] == 0:
                # Try to deserialize output
                try:
                    output_data = self.deserialize_output(result['stdout'])
                except:
                    output_data = result['stdout']

                return ExecutionResult(
                    success=True,
                    output=output_data,
                    execution_time=execution_time,
                    metadata={
                        'language': 'shell',
                        'shell_version': self._get_shell_version(),
                        'stderr': result['stderr'] if result['stderr'] else None
                    }
                )
            else:
                return ExecutionResult(
                    success=False,
                    error=result['stderr'] or f"Process exited with code {result['returncode']}",
                    output=None,
                    execution_time=execution_time,
                    metadata={
                        'language': 'shell',
                        'returncode': result['returncode'],
                        'stdout': result['stdout'] if result['stdout'] else None
                    }
                )

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                error=str(e),
                output=None,
                execution_time=execution_time,
                metadata={'language': 'shell', 'error_type': type(e).__name__}
            )

    def _get_shell_version(self) -> str:
        """Get shell version information."""
        try:
            # Try different version commands based on shell type
            shell_name = os.path.basename(self._shell_path)

            if shell_name in ['bash']:
                result = subprocess.run([self._shell_path, '--version'],
                                      capture_output=True, text=True)
            elif shell_name in ['zsh']:
                result = subprocess.run([self._shell_path, '--version'],
                                      capture_output=True, text=True)
            else:
                # Generic approach
                result = subprocess.run([self._shell_path, '--version'],
                                      capture_output=True, text=True)

            if result.returncode == 0:
                return result.stdout.split('\n')[0].strip()
        except:
            pass
        return "unknown"

    def _create_execution_wrapper(self, code: str, input_data: Dict[str, Any]) -> str:
        """Create shell script execution wrapper with Wumbo utilities."""

        input_json = json.dumps(input_data, indent=2).replace('"', '\\"')

        wrapper = f'''#!/bin/bash

# Wumbo Framework Shell Script Template Execution Wrapper
# Generated automatically - do not modify

set -e  # Exit on error

# Wumbo utilities
wumbo_log() {{
    local message="$1"
    local level="${{2:-info}}"
    echo "[WUMBO_LOG:$(echo "$level" | tr '[:lower:]' '[:upper:]')] $message" >&2
}}

wumbo_error() {{
    local message="$1"
    local error_json="{\\"__wumbo_error__\\": true, \\"message\\": \\"Wumbo Template Error: $message\\", \\"name\\": \\"WumboTemplateError\\"}"
    echo "$error_json" >&2
    exit 1
}}

wumbo_success() {{
    local result="$1"
    local result_type="${{2:-string}}"
    local success_json="{\\"__wumbo_result__\\": true, \\"data\\": \\"$result\\", \\"type\\": \\"$result_type\\"}"
    echo "$success_json"
}}

# Parse input data (simplified JSON parsing for shell)
WUMBO_INPUT='{input_json}'

# Extract arguments using jq if available, or basic string manipulation
if command -v jq >/dev/null 2>&1; then
    WUMBO_ARGS=($(echo "$WUMBO_INPUT" | jq -r '.args[]? // empty'))
    WUMBO_TEMPLATE_NAME=$(echo "$WUMBO_INPUT" | jq -r '.context.template_name // "unknown"')
    WUMBO_EXECUTION_ID=$(echo "$WUMBO_INPUT" | jq -r '.context.execution_id // "unknown"')
else
    # Basic fallback parsing (limited functionality)
    wumbo_log "jq not available, using basic parsing" "warn"
    WUMBO_ARGS=()
    WUMBO_TEMPLATE_NAME="unknown"
    WUMBO_EXECUTION_ID="unknown"
fi

# Make arguments available as individual variables
if [ "${{#WUMBO_ARGS[@]}}" -gt 0 ]; then
    ARG1="${{WUMBO_ARGS[0]:-}}"
    ARG2="${{WUMBO_ARGS[1]:-}}"
    ARG3="${{WUMBO_ARGS[2]:-}}"
    ARG4="${{WUMBO_ARGS[3]:-}}"
    ARG5="${{WUMBO_ARGS[4]:-}}"
fi

# Utility functions
wumbo_map() {{
    local func="$1"
    shift
    local args=("$@")

    for arg in "${{args[@]}}"; do
        eval "$func \\"$arg\\""
    done
}}

wumbo_filter() {{
    local condition="$1"
    shift
    local args=("$@")

    for arg in "${{args[@]}}"; do
        if eval "$condition \\"$arg\\""; then
            echo "$arg"
        fi
    done
}}

wumbo_join() {{
    local delimiter="$1"
    shift
    local args=("$@")

    local result=""
    for arg in "${{args[@]}}"; do
        if [ -n "$result" ]; then
            result="$result$delimiter$arg"
        else
            result="$arg"
        fi
    done
    echo "$result"
}}

# Error handling
trap 'wumbo_error "Script terminated unexpectedly at line $LINENO"' ERR

# User template code
{code}

# If result variable exists and no explicit success call was made, output it
if [ -n "${{result:-}}" ]; then
    wumbo_success "$result"
fi
'''

        return wrapper

    def _prepare_context_data(self, context: ExecutionContext) -> Dict[str, Any]:
        """Prepare context data for shell consumption."""
        return {
            'args': [str(arg) for arg in context.args] if context.args else [],
            'kwargs': {str(k): str(v) for k, v in context.kwargs.items()} if context.kwargs else {},
            'context': {
                'template_name': getattr(context, 'template_name', 'unknown'),
                'execution_id': getattr(context, 'execution_id', 'unknown'),
                'metadata': getattr(context, 'metadata', {})
            }
        }


# Factory function for creating shell script templates
def create_shell_template(code: str, **config) -> 'MultiLanguageTemplate':
    """
    Create a shell script template with the given code.

    Args:
        code: Shell script template code
        **config: Additional configuration options

    Returns:
        MultiLanguageTemplate instance configured for shell scripting

    Example:
        >>> template = create_shell_template('''
        ... result=""
        ... for arg in "${WUMBO_ARGS[@]}"; do
        ...     result="$result $(($arg * 2))"
        ... done
        ... wumbo_success "$result"
        ... ''')
        >>> result = template(1, 2, 3)
    """
    from .core import MultiLanguageTemplate, LanguageRuntime

    # Create default runtime configuration
    runtime = LanguageRuntime(
        language=SupportedLanguage.SHELL,
        interpreter_path=config.get('shell_path', ''),
        version=config.get('shell_version', 'latest'),
        additional_args=config.get('shell_args', []),
        environment_vars=config.get('env_vars', {}),
        working_directory=config.get('working_dir'),
        timeout=config.get('timeout', 300),
        max_memory_mb=config.get('max_memory_mb', 1024)
    )

    return MultiLanguageTemplate(
        code=code,
        language=SupportedLanguage.SHELL,
        runtime=runtime,
        **{k: v for k, v in config.items() if k not in [
            'shell_path', 'shell_version', 'shell_args', 'env_vars',
            'working_dir', 'timeout', 'max_memory_mb'
        ]}
    )
