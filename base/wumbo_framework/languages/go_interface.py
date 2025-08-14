"""
🌀 Wumbo Framework - Go Language Interface

This module provides Go language support for the Wumbo framework,
enabling templates to be written in Go and executed via Go runtime.
"""

import json
import os
import tempfile
import subprocess
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from .core import (
    LanguageInterface, LanguageRuntime, SerializationConfig, SupportedLanguage,
    ProcessExecutionMixin, DataSerializer, SecuritySandbox
)
from ..core.base import ExecutionContext, ExecutionResult


class GoInterface(LanguageInterface, ProcessExecutionMixin):
    """
    Go language interface for executing Go templates.

    This interface provides Go compilation and execution with security features,
    module management, and seamless integration with the Wumbo framework.
    """

    def __init__(self, runtime: LanguageRuntime, serialization: SerializationConfig):
        super().__init__(runtime, serialization)
        self.serializer = DataSerializer(serialization)
        self._go_path = self._detect_go_executable()

    def validate_code(self, code: str) -> bool:
        """
        Validate Go code syntax using Go compiler.

        Args:
            code: Go code to validate

        Returns:
            True if code is syntactically valid, False otherwise
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a temporary Go module
                main_file = os.path.join(temp_dir, "main.go")
                with open(main_file, 'w') as f:
                    f.write(code)

                # Initialize go module
                subprocess.run([self._go_path, 'mod', 'init', 'wumbo-temp'],
                             cwd=temp_dir, capture_output=True, text=True)

                # Try to build without executing
                result = subprocess.run(
                    [self._go_path, 'build', '-o', '/dev/null', '.'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Go validation error: {e}")
            return False

    def prepare_execution(self, code: str, context: ExecutionContext) -> str:
        """
        Prepare Go code for execution by wrapping it with framework utilities.

        Args:
            code: Go template code
            context: Execution context with input data and metadata

        Returns:
            Prepared Go code ready for compilation and execution
        """
        # Prepare input data serialization
        input_data = self._prepare_context_data(context)

        # Create execution wrapper with Go imports and utilities
        wrapper = self._create_execution_wrapper(code, input_data)

        return wrapper

    def execute_template(self, prepared_code: str, context: ExecutionContext) -> ExecutionResult:
        """
        Execute prepared Go code by compiling and running it.

        Args:
            prepared_code: Prepared Go code
            context: Execution context

        Returns:
            ExecutionResult with output data and metadata
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write Go code to file
                main_file = os.path.join(temp_dir, "main.go")
                with open(main_file, 'w') as f:
                    f.write(prepared_code)

                # Initialize go module
                subprocess.run([self._go_path, 'mod', 'init', 'wumbo-template'],
                             cwd=temp_dir, capture_output=True, text=True)

                # Execute with security sandbox if enabled
                if hasattr(context, 'execution_environment') and context.execution_environment.sandbox_enabled:
                    with SecuritySandbox() as sandbox:
                        result = self._execute_go_script(temp_dir, context)
                else:
                    result = self._execute_go_script(temp_dir, context)

                return result

        except Exception as e:
            self.logger.error(f"Go execution error: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                output=None,
                execution_time=0.0,
                metadata={'language': 'go', 'error_type': type(e).__name__}
            )

    def serialize_input(self, data: Any) -> str:
        """Serialize input data for Go consumption."""
        return json.dumps(data, ensure_ascii=False, indent=2)

    def deserialize_output(self, data: str) -> Any:
        """Deserialize Go output data."""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data

    def get_supported_features(self) -> List[str]:
        """Get list of supported Go features."""
        return [
            'static_typing',
            'goroutines',
            'channels',
            'interfaces',
            'structs',
            'methods',
            'packages',
            'modules',
            'file_system',
            'network_requests',
            'json_processing',
            'regular_expressions',
            'error_handling',
            'reflection',
            'generics'
        ]

    def _detect_go_executable(self) -> str:
        """Detect Go executable path."""
        if self.runtime.interpreter_path:
            return self.runtime.interpreter_path

        # Try to find go executable
        try:
            result = subprocess.run(['go', 'version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return 'go'
        except FileNotFoundError:
            pass

        raise RuntimeError("Go executable not found. Please install Go or specify interpreter_path.")

    def _execute_go_script(self, project_dir: str, context: ExecutionContext) -> ExecutionResult:
        """Execute Go script by running go run."""
        import time

        start_time = time.time()

        try:
            # Build command
            cmd = [self._go_path, 'run'] + self.runtime.additional_args + ['.']

            # Set up environment
            env = os.environ.copy()
            env.update(self.runtime.environment_vars)

            # Execute process
            result = self.execute_process(
                cmd,
                timeout=self.runtime.timeout,
                cwd=project_dir,
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
                        'language': 'go',
                        'go_version': self._get_go_version(),
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
                        'language': 'go',
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
                metadata={'language': 'go', 'error_type': type(e).__name__}
            )

    def _get_go_version(self) -> str:
        """Get Go version information."""
        try:
            result = subprocess.run([self._go_path, 'version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "unknown"

    def _create_execution_wrapper(self, code: str, input_data: Dict[str, Any]) -> str:
        """Create Go execution wrapper with Wumbo utilities."""

        input_json = json.dumps(input_data, indent=2)

        wrapper = f'''package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"reflect"
)

// Wumbo Framework Go Template Execution Wrapper
// Generated automatically - do not modify

// WumboContext represents the execution context
type WumboContext struct {{
	TemplateName string                 `json:"template_name"`
	ExecutionID  string                 `json:"execution_id"`
	Metadata     map[string]interface{{}} `json:"metadata"`
}}

// WumboInput represents input data from Wumbo framework
type WumboInput struct {{
	Args    []interface{{}}            `json:"args"`
	Kwargs  map[string]interface{{}}   `json:"kwargs"`
	Context WumboContext             `json:"context"`
}}

// WumboAPI provides utilities for template execution
type WumboAPI struct {{
	Input   WumboInput
	Args    []interface{{}}
	Kwargs  map[string]interface{{}}
	Context WumboContext
}}

// Log writes a log message
func (w *WumboAPI) Log(message interface{{}}, level ...string) {{
	logLevel := "info"
	if len(level) > 0 {{
		logLevel = level[0]
	}}

	msgJSON, _ := json.Marshal(message)
	fmt.Fprintf(os.Stderr, "[WUMBO_LOG:%s] %s\\n",
		map[string]string{{"info": "INFO", "warn": "WARN", "error": "ERROR", "debug": "DEBUG"}}[logLevel],
		string(msgJSON))
}}

// Error raises an error and exits
func (w *WumboAPI) Error(message string) {{
	errorResult := map[string]interface{{}}{{
		"__wumbo_error__": true,
		"message":         fmt.Sprintf("Wumbo Template Error: %s", message),
		"name":            "WumboTemplateError",
	}}

	errorJSON, _ := json.Marshal(errorResult)
	fmt.Fprintln(os.Stderr, string(errorJSON))
	os.Exit(1)
}}

// Success outputs the result and exits successfully
func (w *WumboAPI) Success(result interface{{}}) {{
	successResult := map[string]interface{{}}{{
		"__wumbo_result__": true,
		"data":             result,
		"type":             reflect.TypeOf(result).String(),
	}}

	resultJSON, _ := json.Marshal(successResult)
	fmt.Println(string(resultJSON))
}}

// Utility functions
func WumboMap(slice []interface{{}}, fn func(interface{{}}, int) interface{{}}) []interface{{}} {{
	result := make([]interface{{}}, len(slice))
	for i, v := range slice {{
		result[i] = fn(v, i)
	}}
	return result
}}

func WumboFilter(slice []interface{{}}, fn func(interface{{}}, int) bool) []interface{{}} {{
	var result []interface{{}}
	for i, v := range slice {{
		if fn(v, i) {{
			result = append(result, v)
		}}
	}}
	return result
}}

func WumboReduce(slice []interface{{}}, fn func(interface{{}}, interface{{}}, int) interface{{}}, initial interface{{}}) interface{{}} {{
	acc := initial
	for i, v := range slice {{
		acc = fn(acc, v, i)
	}}
	return acc
}}

// Global variables for template use
var wumboInput WumboInput
var wumboArgs []interface{{}}
var wumboKwargs map[string]interface{{}}
var wumboContext WumboContext
var wumbo *WumboAPI

func init() {{
	// Parse input data
	inputJSON := `{input_json}`
	if err := json.Unmarshal([]byte(inputJSON), &wumboInput); err != nil {{
		log.Fatalf("Failed to parse input data: %v", err)
	}}

	wumboArgs = wumboInput.Args
	wumboKwargs = wumboInput.Kwargs
	wumboContext = wumboInput.Context

	wumbo = &WumboAPI{{
		Input:   wumboInput,
		Args:    wumboArgs,
		Kwargs:  wumboKwargs,
		Context: wumboContext,
	}}
}}

func main() {{
	defer func() {{
		if r := recover(); r != nil {{
			errorResult := map[string]interface{{}}{{
				"__wumbo_error__": true,
				"message":         fmt.Sprintf("Panic: %v", r),
				"name":            "WumboRuntimeError",
			}}

			errorJSON, _ := json.Marshal(errorResult)
			fmt.Fprintln(os.Stderr, string(errorJSON))
			os.Exit(1)
		}}
	}}()

	// User template code
{self._indent_code(code, "	")}

	// If result variable exists, output it
	// Note: This is a simplification - in real Go, we'd need more sophisticated handling
}}
'''

        return wrapper

    def _indent_code(self, code: str, indent: str) -> str:
        """Indent code lines."""
        return '\n'.join(indent + line if line.strip() else line for line in code.split('\n'))

    def _prepare_context_data(self, context: ExecutionContext) -> Dict[str, Any]:
        """Prepare context data for Go consumption."""
        return {
            'args': list(context.args) if context.args else [],
            'kwargs': dict(context.kwargs) if context.kwargs else {},
            'context': {
                'template_name': getattr(context, 'template_name', 'unknown'),
                'execution_id': getattr(context, 'execution_id', 'unknown'),
                'metadata': getattr(context, 'metadata', {})
            }
        }


# Factory function for creating Go templates
def create_go_template(code: str, **config) -> 'MultiLanguageTemplate':
    """
    Create a Go template with the given code.

    Args:
        code: Go template code
        **config: Additional configuration options

    Returns:
        MultiLanguageTemplate instance configured for Go

    Example:
        >>> template = create_go_template('''
        ... result := make([]int, len(wumboArgs))
        ... for i, arg := range wumboArgs {
        ...     if num, ok := arg.(float64); ok {
        ...         result[i] = int(num) * 2
        ...     }
        ... }
        ... wumbo.Success(result)
        ... ''')
        >>> result = template(1, 2, 3)
    """
    from .core import MultiLanguageTemplate, LanguageRuntime

    # Create default runtime configuration
    runtime = LanguageRuntime(
        language=SupportedLanguage.GO,
        interpreter_path=config.get('go_path', ''),
        version=config.get('go_version', 'latest'),
        additional_args=config.get('go_args', []),
        environment_vars=config.get('env_vars', {}),
        working_directory=config.get('working_dir'),
        timeout=config.get('timeout', 300),
        max_memory_mb=config.get('max_memory_mb', 1024)
    )

    return MultiLanguageTemplate(
        code=code,
        language=SupportedLanguage.GO,
        runtime=runtime,
        **{k: v for k, v in config.items() if k not in [
            'go_path', 'go_version', 'go_args', 'env_vars',
            'working_dir', 'timeout', 'max_memory_mb'
        ]}
    )
