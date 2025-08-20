"""
Wumbo Framework - TypeScript Language Interface

This module provides TypeScript language support for the Wumbo framework,
enabling templates to be written in TypeScript and executed via Node.js runtime
with TypeScript compilation.
"""

import json
import os
import tempfile
import subprocess
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from wumbo_framework.core import (
    LanguageInterface, LanguageRuntime, SerializationConfig, SupportedLanguage,
    ProcessExecutionMixin, DataSerializer, SecuritySandbox
)
from wumbo_framework.core.base import ExecutionContext, ExecutionResult



class TypeScriptInterface(LanguageInterface, ProcessExecutionMixin):
    """
    TypeScript language interface for executing TypeScript templates.

    This interface provides TypeScript compilation and execution with security features,
    npm package management, and seamless integration with the Wumbo framework.
    """

    def __init__(self, runtime: LanguageRuntime, serialization: SerializationConfig):
        super().__init__(runtime, serialization)
        self.serializer = DataSerializer(serialization)
        self._node_path = self._detect_node_executable()
        self._tsc_path = self._detect_tsc_executable()
        self._ts_node_path = self._detect_ts_node_executable()

    def validate_code(self, code: str) -> bool:
        """
        Validate TypeScript code syntax using TypeScript compiler.

        Args:
            code: TypeScript code to validate

        Returns:
            True if code is syntactically valid, False otherwise
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Use TypeScript compiler to check syntax
                result = subprocess.run(
                    [self._tsc_path, '--noEmit', '--strict', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                return result.returncode == 0
            finally:
                os.unlink(temp_file)
        except Exception as e:
            self.logger.error(f"TypeScript validation error: {e}")
            return False

    def prepare_execution(self, code: str, context: ExecutionContext) -> str:
        """
        Prepare TypeScript code for execution by wrapping it with framework utilities.

        Args:
            code: TypeScript template code
            context: Execution context with input data and metadata

        Returns:
            Prepared TypeScript code ready for compilation and execution
        """
        # Create wumbo utilities for TypeScript
        wumbo_utils = self._get_wumbo_utilities()

        # Prepare input data serialization
        input_data = self._prepare_context_data(context)

        # Create execution wrapper with TypeScript types
        wrapper = self._create_execution_wrapper(code, input_data, wumbo_utils)

        return wrapper

    def execute_template(self, prepared_code: str, context: ExecutionContext) -> ExecutionResult:
        """
        Execute prepared TypeScript code by compiling and running it.

        Args:
            prepared_code: Prepared TypeScript code
            context: Execution context

        Returns:
            ExecutionResult with output data and metadata
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
                f.write(prepared_code)
                temp_file = f.name

            try:
                # Execute with security sandbox if enabled
                if hasattr(context, 'execution_environment') and context.execution_environment.sandbox_enabled:
                    with SecuritySandbox() as sandbox:
                        result = self._execute_typescript_script(temp_file, context)
                else:
                    result = self._execute_typescript_script(temp_file, context)

                return result
            finally:
                os.unlink(temp_file)

        except Exception as e:
            self.logger.error(f"TypeScript execution error: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                output=None,
                execution_time=0.0,
                metadata={'language': 'typescript', 'error_type': type(e).__name__}
            )

    def serialize_input(self, data: Any) -> str:
        """Serialize input data for TypeScript consumption."""
        return json.dumps(data, ensure_ascii=False, indent=2)

    def deserialize_output(self, data: str) -> Any:
        """Deserialize TypeScript output data."""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data

    def get_supported_features(self) -> List[str]:
        """Get list of supported TypeScript features."""
        return [
            'static_typing',
            'async_await',
            'promises',
            'es6_modules',
            'npm_packages',
            'file_system',
            'network_requests',
            'json_processing',
            'regular_expressions',
            'error_handling',
            'generics',
            'interfaces',
            'classes',
            'decorators'
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

    def _detect_tsc_executable(self) -> str:
        """Detect TypeScript compiler executable path."""
        for tsc_cmd in ['tsc', 'npx tsc']:
            try:
                result = subprocess.run(tsc_cmd.split() + ['--version'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return tsc_cmd
            except FileNotFoundError:
                continue

        raise RuntimeError("TypeScript compiler not found. Please install TypeScript (npm install -g typescript).")

    def _detect_ts_node_executable(self) -> str:
        """Detect ts-node executable path."""
        for ts_node_cmd in ['ts-node', 'npx ts-node']:
            try:
                result = subprocess.run(ts_node_cmd.split() + ['--version'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return ts_node_cmd
            except FileNotFoundError:
                continue

        # If ts-node not available, return empty string to fall back to tsc + node
        return ''

    def _execute_typescript_script(self, script_path: str, context: ExecutionContext) -> ExecutionResult:
        """Execute TypeScript script by compiling or using ts-node."""
        import time

        start_time = time.time()

        try:
            # Try to use ts-node for direct execution if available
            if self._ts_node_path:
                result = self._execute_with_ts_node(script_path, context)
            else:
                # Fall back to compile + execute
                result = self._execute_with_tsc_compile(script_path, context)

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
                        'language': 'typescript',
                        'compiler_version': self._get_tsc_version(),
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
                        'language': 'typescript',
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
                metadata={'language': 'typescript', 'error_type': type(e).__name__}
            )

    def _execute_with_ts_node(self, script_path: str, context: ExecutionContext) -> Dict[str, Any]:
        """Execute TypeScript script using ts-node."""
        # Build command
        cmd = self._ts_node_path.split() + self.runtime.additional_args + [script_path]

        # Set up environment
        env = os.environ.copy()
        env.update(self.runtime.environment_vars)

        # Execute process
        return self.execute_process(
            cmd,
            timeout=self.runtime.timeout,
            cwd=self.runtime.working_directory,
            env=env
        )

    def _execute_with_tsc_compile(self, script_path: str, context: ExecutionContext) -> Dict[str, Any]:
        """Execute TypeScript script by compiling first then running with Node.js."""
        # Compile TypeScript to JavaScript
        js_path = script_path.replace('.ts', '.js')

        try:
            compile_result = subprocess.run(
                [self._tsc_path, '--target', 'ES2020', '--module', 'CommonJS', script_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if compile_result.returncode != 0:
                return {
                    'returncode': compile_result.returncode,
                    'stdout': '',
                    'stderr': f"TypeScript compilation error: {compile_result.stderr}"
                }

            # Execute compiled JavaScript
            cmd = [self._node_path] + self.runtime.additional_args + [js_path]

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

            return result

        finally:
            # Clean up compiled JavaScript file
            if os.path.exists(js_path):
                os.unlink(js_path)

    def _get_tsc_version(self) -> str:
        """Get TypeScript compiler version information."""
        try:
            result = subprocess.run(self._tsc_path.split() + ['--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "unknown"

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
        """Create TypeScript execution wrapper with Wumbo utilities and types."""

        wrapper = f"""
// Wumbo Framework TypeScript Template Execution Wrapper
// Generated automatically - do not modify

{wumbo_utils}

// Input data from Wumbo context
const wumboInput: WumboInput = {json.dumps(input_data, indent=2)};
const wumboArgs: any[] = wumboInput.args || [];
const wumboKwargs: Record<string, any> = wumboInput.kwargs || {{}};
const wumboContext: WumboContext = wumboInput.context || {{}};

// Wumbo utilities available in template
const wumbo: WumboAPI = {{
    input: wumboInput,
    args: wumboArgs,
    kwargs: wumboKwargs,
    context: wumboContext,
    log: (message: any, level: LogLevel = 'info'): void => {{
        console.error(`[WUMBO_LOG:${{level.toUpperCase()}}] ${{JSON.stringify(message)}}`);
    }},
    error: (message: string): never => {{
        throw new Error(`Wumbo Template Error: ${{message}}`);
    }},
    success: (result: any): void => {{
        console.log(JSON.stringify({{
            __wumbo_result__: true,
            data: result,
            type: typeof result
        }}));
    }}
}};

// Template execution wrapper
async function executeTemplate(): Promise<void> {{
    try {{
        // User template code
        {code}

        // If no explicit success call, assume last expression is result
        if (typeof result !== 'undefined') {{
            wumbo.success(result);
        }}
    }} catch (error: any) {{
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
executeTemplate().catch((error: any) => {{
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
        """Get TypeScript utility functions and type definitions for Wumbo templates."""
        return """
// Wumbo TypeScript Utilities and Type Definitions
// Provides helper functions, types, and compatibility layer

// Type definitions
type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface WumboContext {
    template_name: string;
    execution_id: string;
    metadata: Record<string, any>;
}

interface WumboInput {
    args: any[];
    kwargs: Record<string, any>;
    context: WumboContext;
}

interface WumboAPI {
    input: WumboInput;
    args: any[];
    kwargs: Record<string, any>;
    context: WumboContext;
    log: (message: any, level?: LogLevel) => void;
    error: (message: string) => never;
    success: (result: any) => void;
}

// Utility functions
function wumboMap<T, U>(array: T[], func: (item: T, index: number) => U): U[] {
    return array.map(func);
}

function wumboFilter<T>(array: T[], func: (item: T, index: number) => boolean): T[] {
    return array.filter(func);
}

function wumboReduce<T, U>(array: T[], func: (acc: U, item: T, index: number) => U, initial: U): U {
    return array.reduce(func, initial);
}

async function wumboFetch(url: string, options: any = {}): Promise<any> {
    // Basic fetch implementation for Node.js with types
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
        }, (res: any) => {
            let data = '';
            res.on('data', (chunk: any) => data += chunk);
            res.on('end', () => {
                resolve({
                    status: res.statusCode,
                    statusText: res.statusMessage,
                    text: (): Promise<string> => Promise.resolve(data),
                    json: (): Promise<any> => Promise.resolve(JSON.parse(data))
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
declare global {
    function wumboMap<T, U>(array: T[], func: (item: T, index: number) => U): U[];
    function wumboFilter<T>(array: T[], func: (item: T, index: number) => boolean): T[];
    function wumboReduce<T, U>(array: T[], func: (acc: U, item: T, index: number) => U, initial: U): U;
    function wumboFetch(url: string, options?: any): Promise<any>;
}

(global as any).wumboMap = wumboMap;
(global as any).wumboFilter = wumboFilter;
(global as any).wumboReduce = wumboReduce;
(global as any).wumboFetch = wumboFetch;
"""

    def _prepare_context_data(self, context: ExecutionContext) -> Dict[str, Any]:
        """Prepare context data for TypeScript consumption."""
        return {
            'args': list(context.args) if context.args else [],
            'kwargs': dict(context.kwargs) if context.kwargs else {},
            'context': {
                'template_name': getattr(context, 'template_name', 'unknown'),
                'execution_id': getattr(context, 'execution_id', 'unknown'),
                'metadata': getattr(context, 'metadata', {})
            }
        }


# Factory function for creating TypeScript templates
def create_typescript_template(code: str, **config) -> 'MultiLanguageTemplate':
    """
    Create a TypeScript template with the given code.

    Args:
        code: TypeScript template code
        **config: Additional configuration options

    Returns:
        MultiLanguageTemplate instance configured for TypeScript

    Example:
        >>> template = create_typescript_template('''
        ... const result: number[] = wumboArgs.map((x: number) => x * 2);
        ... wumbo.success(result);
        ... ''')
        >>> result = template(1, 2, 3)
    """
    from ..core import MultiLanguageTemplate, LanguageRuntime

    # Create default runtime configuration
    runtime = LanguageRuntime(
        language=SupportedLanguage.TYPESCRIPT,
        interpreter_path=config.get('node_path', ''),
        version=config.get('typescript_version', 'latest'),
        additional_args=config.get('ts_args', []),
        environment_vars=config.get('env_vars', {}),
        working_directory=config.get('working_dir'),
        timeout=config.get('timeout', 300),
        max_memory_mb=config.get('max_memory_mb', 1024)
    )

    return MultiLanguageTemplate(
        code=code,
        language=SupportedLanguage.TYPESCRIPT,
        runtime=runtime,
        **{k: v for k, v in config.items() if k not in [
            'node_path', 'typescript_version', 'ts_args', 'env_vars',
            'working_dir', 'timeout', 'max_memory_mb'
        ]}
    )
