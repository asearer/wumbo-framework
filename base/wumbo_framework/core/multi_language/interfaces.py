"""
Language interface abstractions for Wumbo Framework multi-language support.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Type
import logging
from .runtime import LanguageRuntime, SerializationConfig

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
        """Validate template code syntax without executing it."""
        pass

    @abstractmethod
    def prepare_execution(self, code: str, input_data: Any, context: "ExecutionContext") -> Dict[str, Any]:
        """Prepare code and data for execution in the target language."""
        pass

    @abstractmethod
    def execute_template(self, prepared_execution: Dict[str, Any]) -> Any:
        """Execute the prepared template code."""
        pass

    @abstractmethod
    def serialize_input(self, data: Any) -> str:
        """Serialize input data for the target language."""
        pass

    @abstractmethod
    def deserialize_output(self, data: str) -> Any:
        """Deserialize output data from the target language."""
        pass

    def get_supported_features(self) -> List[str]:
        """Get list of supported features for this language interface."""
        return ["basic_execution", "data_serialization"]

    def cleanup(self):
        """Cleanup resources after template execution."""
        pass
