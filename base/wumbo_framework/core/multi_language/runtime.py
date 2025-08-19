"""
Runtime and serialization configurations for Wumbo Framework multi-language templates.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Callable, Type
from enum import Enum

class SupportedLanguage(Enum):
    """Enumeration of supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    # Add other languages as needed

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
    resource_limits: Dict[str, any] = None

@dataclass
class SerializationConfig:
    """Configuration for data serialization between languages."""
    format: str = "json"
    encoding: str = "utf-8"
    compression: Optional[str] = None
    custom_serializers: Dict[Type, Callable] = None
