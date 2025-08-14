"""
🌀 Wumbo Framework - JavaScript/Node.js Language Interface

This module provides JavaScript/Node.js language support for the Wumbo framework,
enabling templates to be written in JavaScript and executed via Node.js runtime.
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


class JavaScriptInterface(LanguageInterface, ProcessExecutionMixin):
    """
    JavaScript/Node.js language interface for executing JavaScript templates.

    This interface provides JavaScript execution with security features,
    npm package management, and seamless integration with the Wumbo framework.
    """

    def __init__(self, runtime: LanguageRuntime, serialization: SerializationConfig):
        super().__init__(runtime, serialization)
        self.serializer = DataSerializer(serialization)
        self._node_path = self._detect_node_executable()
        self._npm_path = self._detect_npm_executable()

    def validate_code(self, code: str) -> bool:
        """
        Validate JavaScript code syntax using Node.js syntax check.

        Args:
            code: JavaScript code to validate

        Returns:
            True if code is syntactically valid, False otherwise
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                result = subprocess.run(
                    [self._node_path, '--check', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.returncode == 0
            finally:
                os.unlink(temp_file)
        except Exception as e:
            self.logger.error(f"JavaScript validation error: {e}")
            return False

    def prepare_execution(self, code: str, context: ExecutionContext) -> str:
        """
        Prepare JavaScript code for execution by wrapping it with framework utilities.

        Args:
            code: JavaScript template code
            context: Execution context with input data and metadata

        Returns:
            Prepared JavaScript code ready for execution
        """
        # Create wumbo utilities for JavaScript
        wumbo_utils = self._get_wumbo_utilities()

        # Prepare input data serialization
        input_data = self._prepare_context_data(context)

        # Create execution wrapper
        wrapper = self._create_execution_wrapper(code, input_data, wumbo_utils)

        return wrapper

    def execute_template(self, prepared_code: str, context: ExecutionContext) -> ExecutionResult:
        """
        Execute prepared JavaScript code and return results.

        Args:
            prepared_code: Prepared JavaScript code
            context: Execution context

        Returns:
            ExecutionResult with output data and metadata
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(prepared_code)
                temp_file = f.name

            try:
                # Execute with security sandbox if enabled
                if hasattr(context, 'execution_environment') and context.execution_environment.sandbox_enabled:
                    with SecuritySandbox() as sandbox:
                        result = self._execute_node_script(temp_file, context)
                else:
                    result = self._execute_node_script(temp_file, context)

                return result
            finally:
                os.unlink(temp_file)

        except Exception as e:
            self.logger.error(f"JavaScript execution error: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                output=None,
                execution_time=0.0,
                metadata={'language': 'javascript', 'error_type': type(e).__name__}
            )

    def serialize_input(self, data: Any) -> str:
        """Serialize input data for JavaScript consumption."""
        return json.dumps(data, ensure_ascii=False, indent=2)

    def deserialize_output(self, data: str) -> Any:
        """Deserialize JavaScript output data."""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data

    def get_supported_features(self) -> List[str]:
        """Get list of supported JavaScript/Node.js features."""
        return [
            'async_await',
            'promises',
            'es6_modules',
            'npm_packages',
            'file_system',
            'network_requests',
            'json_processing',
            'regular_expressions',
            'error_handling'
        ]

    def _detect_node_executable(self) -> str:
        """Detect Node.js executable path."""
        if self.runtime.interpreter_path:
            return self.runtime.interpreter_path

        # Try common Node.js executable names
        for node_cmd in ['node', 'nodejs']:
            try:
                result = subprocess.run([node_cmd, '--version'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return node_cmd
            except FileNotFoundError:
                continue

        raise RuntimeError("Node.js executable not found. Please install Node.js or specify interpreter_path.")

    def _detect_npm_executable(self) -> str:
        """Detect npm executable path."""
        for npm_cmd in ['npm', 'yarn', 'pnpm']:
            try:
                result = subprocess.run([npm_cmd, '--version'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return npm_cmd
            except FileNotFoundError:
                continue

        return 'npm'  # Default fallback

    def _execute_node_script(self, script_path: str, context: ExecutionContext) -> ExecutionResult:
        """Execute Node.js script and capture results."""
        import time

        start_time = time.time()

        try:
            # Build command
            cmd = [self._node_path] + self.runtime.additional_args + [script_path]

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
                        'language': 'javascript',
                        'node_version': self._get_node_version(),
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
                        'language': 'javascript',
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
                metadata={'language': 'javascript', 'error_type': type(e).__name__}
            )

    def _get_node_version(self) -> str:
        """Get Node.js version information."""
        try:
            result = subprocess.run([self._node_path, '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "unknown"

    def _create_execution_wrapper(self, code: str, input_data: Dict[str, Any],
                                  wumbo_utils: str) -> str:
        """Create JavaScript execution wrapper with Wumbo utilities."""

        wrapper = f"""
// Wumbo Framework JavaScript Template Execution Wrapper
// Generated automatically - do not modify

{wumbo_utils}

// Input data from Wumbo context
const wumboInput = {json.dumps(input_data, indent=2)};
const wumboArgs = wumboInput.args || [];
const wumboKwargs = wumboInput.kwargs || {{}};
const wumboContext = wumboInput.context || {{}};

// Wumbo utilities available in template
const wumbo = {{
    input: wumboInput,
    args: wumboArgs,
    kwargs: wumboKwargs,
    context: wumboContext,
    log: (message, level = 'info') => {{
        console.error(`[WUMBO_LOG:${{level.toUpperCase()}}] ${{JSON.stringify(message)}}`);
    }},
    error: (message) => {{
        throw new Error(`Wumbo Template Error: ${{message}}`);
    }},
    success: (result) => {{
        console.log(JSON.stringify({{
            __wumbo_result__: true,
            data: result,
            type: typeof result
        }}));
    }}
}};

// Template execution wrapper
async function executeTemplate() {{
    try {{
        // User template code
        {code}

        // If no explicit success call, assume last expression is result
        if (typeof result !== 'undefined') {{
            wumbo.success(result);
        }}
    }} catch (error) {{
        console.error(JSON.stringify({{
            __wumbo_error__: true,
            message: error.message,
            stack: error.stack,
            name: error.name
        }}));
        process.exit(1);
    }}
}}

// Execute template
executeTemplate().catch(error => {{
    console.error(JSON.stringify({{
        __wumbo_error__: true,
        message: error.message,
        stack: error.stack,
        name: error.name
    }}));
    process.exit(1);
}});
"""

        return wrapper

    def _get_wumbo_utilities(self) -> str:
        """Get JavaScript utility functions for Wumbo templates."""
        return """
// Wumbo JavaScript Utilities
// Provides helper functions and compatibility layer

// Utility functions
function wumboMap(array, func) {
    return array.map(func);
}

function wumboFilter(array, func) {
    return array.filter(func);
}

function wumboReduce(array, func, initial) {
    return array.reduce(func, initial);
}

function wumboFetch(url, options = {}) {
    // Basic fetch implementation for Node.js
    const https = require('https');
    const http = require('http');
    const urlModule = require('url');

    return new Promise((resolve, reject) => {
        const parsedUrl = urlModule.parse(url);
        const client = parsedUrl.protocol === 'https:' ? https : http;

        const req = client.request({
            hostname: parsedUrl.hostname,
            port: parsedUrl.port,
            path: parsedUrl.path,
            method: options.method || 'GET',
            headers: options.headers || {}
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                resolve({
                    status: res.statusCode,
                    statusText: res.statusMessage,
                    text: () => Promise.resolve(data),
                    json: () => Promise.resolve(JSON.parse(data))
                });
            });
        });

        req.on('error', reject);

        if (options.body) {
            req.write(options.body);
        }

        req.end();
    });
}

// Make utilities available globally
global.wumboMap = wumboMap;
global.wumboFilter = wumboFilter;
global.wumboReduce = wumboReduce;
global.wumboFetch = wumboFetch;
"""

    def _prepare_context_data(self, context: ExecutionContext) -> Dict[str, Any]:
        """Prepare context data for JavaScript consumption."""
        return {
            'args': list(context.args) if context.args else [],
            'kwargs': dict(context.kwargs) if context.kwargs else {},
            'context': {
                'template_name': getattr(context, 'template_name', 'unknown'),
                'execution_id': getattr(context, 'execution_id', 'unknown'),
                'metadata': getattr(context, 'metadata', {})
            }
        }


# Factory function for creating JavaScript templates
def create_javascript_template(code: str, **config) -> 'MultiLanguageTemplate':
    """
    Create a JavaScript template with the given code.

    Args:
        code: JavaScript template code
        **config: Additional configuration options

    Returns:
        MultiLanguageTemplate instance configured for JavaScript

    Example:
        >>> template = create_javascript_template('''
        ... const result = wumboArgs.map(x => x * 2);
        ... wumbo.success(result);
        ... ''')
        >>> result = template(1, 2, 3)
    """
    from .core import MultiLanguageTemplate, LanguageRuntime

    # Create default runtime configuration
    runtime = LanguageRuntime(
        language=SupportedLanguage.JAVASCRIPT,
        interpreter_path=config.get('node_path', ''),
        version=config.get('node_version', 'latest'),
        additional_args=config.get('node_args', []),
        environment_vars=config.get('env_vars', {}),
        working_directory=config.get('working_dir'),
        timeout=config.get('timeout', 300),
        max_memory_mb=config.get('max_memory_mb', 1024)
    )

    return MultiLanguageTemplate(
        code=code,
        language=SupportedLanguage.JAVASCRIPT,
        runtime=runtime,
        **{k: v for k, v in config.items() if k not in [
            'node_path', 'node_version', 'node_args', 'env_vars',
            'working_dir', 'timeout', 'max_memory_mb'
        ]}
    )
