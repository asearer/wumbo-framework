"""
Registry for language interfaces in Wumbo Framework.
"""

import threading
from typing import Type, Dict, List
from .runtime import SupportedLanguage
from .interfaces import LanguageInterface

class LanguageInterfaceRegistry:
    """Registry for language interfaces."""

    _interfaces: Dict[SupportedLanguage, Type[LanguageInterface]] = {}
    _instances: Dict[str, LanguageInterface] = {}
    _lock = threading.Lock()

    @classmethod
    def register_interface(cls, language: SupportedLanguage, interface_class: Type[LanguageInterface]):
        """Register a language interface."""
        with cls._lock:
            cls._interfaces[language] = interface_class

    @classmethod
    def get_interface(cls, language: SupportedLanguage, runtime: "LanguageRuntime", serialization: "SerializationConfig") -> LanguageInterface:
        """Get or create a language interface instance."""
        cache_key = f"{language.value}_{hash(str(runtime))}_{hash(str(serialization))}"

        with cls._lock:
            if cache_key not in cls._instances:
                if language not in cls._interfaces:
                    raise ValueError(f"No interface registered for language: {language.value}")
                interface_class = cls._interfaces[language]
                cls._instances[cache_key] = interface_class(runtime, serialization)
            return cls._instances[cache_key]

    @classmethod
    def list_supported_languages(cls) -> List[SupportedLanguage]:
        """List all supported languages."""
        return list(cls._interfaces.keys())

    @classmethod
    def is_language_supported(cls, language: SupportedLanguage) -> bool:
        """Check if a language is supported."""
        return language in cls._interfaces
