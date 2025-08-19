"""
Utility classes for process execution, sandboxing, and data serialization.
"""

import subprocess
import os
import tempfile
import json
import logging
from typing import Any, Dict, Optional
from .runtime import ExecutionEnvironment, SerializationConfig

class ProcessExecutionMixin:
    """Mixin providing process-based execution utilities."""

    def execute_process(self,
                        command: list,
                        input_data: Optional[str] = None,
                        timeout: int = 300,
                        cwd: Optional[str] = None,
                        env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute a process with proper error handling and resource management."""
        try:
            process_env = os.environ.copy()
            if env:
                process_env.update(env)

            process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, cwd=cwd, env=process_env
            )

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
        if self.config.sandbox_enabled:
            self.temp_dir = tempfile.mkdtemp()
            self.original_cwd = os.getcwd()
            os.chdir(self.temp_dir)
            self._set_resource_limits()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.config.sandbox_enabled and self.original_cwd:
            os.chdir(self.original_cwd)
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _set_resource_limits(self):
        try:
            import resource
            if self.config.resource_limits and "max_memory_mb" in self.config.resource_limits:
                max_memory = self.config.resource_limits["max_memory_mb"] * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
            if self.config.resource_limits and "max_cpu_seconds" in self.config.resource_limits:
                max_cpu = self.config.resource_limits["max_cpu_seconds"]
                resource.setrlimit(resource.RLIMIT_CPU, (max_cpu, max_cpu))
        except ImportError:
            pass
        except Exception as e:
            logging.warning(f"Failed to set resource limits: {e}")


class DataSerializer:
    """Universal data serializer for multi-language communication."""

    def __init__(self, config: SerializationConfig):
        self.config = config

    def serialize(self, data: Any) -> str:
        if self.config.format == "json":
            return json.dumps(data, default=self._json_default, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported serialization format: {self.config.format}")

    def deserialize(self, data: str) -> Any:
        if self.config.format == "json":
            return json.loads(data)
        else:
            raise ValueError(f"Unsupported deserialization format: {self.config.format}")

    def _json_default(self, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, '_asdict'):
            return obj._asdict()
        else:
            return str(obj)
