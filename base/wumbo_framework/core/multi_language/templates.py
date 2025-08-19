"""
Multi-language template executor for Wumbo Framework.
"""

from typing import Any, Dict, Optional
from .interfaces import LanguageInterface
from .runtime import LanguageRuntime, SerializationConfig, ExecutionEnvironment, SupportedLanguage
from .registry import LanguageInterfaceRegistry
from .utils import ProcessExecutionMixin, DataSerializer, SecuritySandbox

class ExecutionContext:
    """Context for template execution."""
    def __init__(self, env: ExecutionEnvironment):
        self.env = env

class ExecutionResult:
    """Result of executing a multi-language template."""
    def __init__(self, success: bool, output: Any, error: Optional[str] = None):
        self.success = success
        self.output = output
        self.error = error

class MultiLanguageTemplate(ProcessExecutionMixin):
    """Core multi-language template executor."""

    def __init__(self,
                 code: str,
                 language: SupportedLanguage,
                 runtime: LanguageRuntime,
                 serialization: SerializationConfig):
        self.code = code
        self.language = language
        self.runtime = runtime
        self.serialization = serialization
        self.serializer = DataSerializer(serialization)
        self.interface: LanguageInterface = LanguageInterfaceRegistry.get_interface(
            language, runtime, serialization
        )

    def execute(self, input_data: Any, context: Optional[ExecutionContext] = None) -> ExecutionResult:
        """Execute the template with given input data and context."""
        try:
            ctx = context or ExecutionContext(ExecutionEnvironment(self.runtime))
            prepared = self.interface.prepare_execution(self.code, input_data, ctx)
            with SecuritySandbox(ctx.env):
                raw_result = self.interface.execute_template(prepared)
            deserialized = self.interface.deserialize_output(
                self.serializer.serialize(raw_result)
            )
            return ExecutionResult(success=True, output=deserialized)
        except Exception as e:
            return ExecutionResult(success=False, output=None, error=str(e))
