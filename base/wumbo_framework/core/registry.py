"""
🌀 Wumbo Framework - Template Registry

This module provides the template registry system for managing, discovering,
and organizing templates within the Wumbo framework. It supports dynamic
template loading, categorization, and plugin architecture.
"""

import importlib
import inspect
import pkgutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type, Any, Callable, Set
from collections import defaultdict
import logging
from threading import Lock

from .base import (
    BaseTemplate, TemplateMetadata, TemplateType, TemplateError,
    TemplateRegistrationError
)


class TemplateRegistry:
    """
    Central registry for all Wumbo templates.

    The registry manages template discovery, registration, and retrieval.
    It supports both static registration and dynamic loading of templates
    from plugins and external modules.
    """

    _instance: Optional['TemplateRegistry'] = None
    _lock = Lock()

    def __init__(self):
        """Initialize the template registry."""
        if TemplateRegistry._instance is not None:
            raise RuntimeError("TemplateRegistry is a singleton. Use get_instance().")

        self._templates: Dict[str, Type[BaseTemplate]] = {}
        self._metadata: Dict[str, TemplateMetadata] = {}
        self._categories: Dict[TemplateType, Set[str]] = defaultdict(set)
        self._aliases: Dict[str, str] = {}
        self._plugin_paths: List[Path] = []
        self._loaded_plugins: Set[str] = set()
        self.logger = logging.getLogger("wumbo.registry")

    @classmethod
    def get_instance(cls) -> 'TemplateRegistry':
        """Get the singleton instance of the template registry."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def register(self,
                template_class: Type[BaseTemplate],
                name: Optional[str] = None,
                aliases: Optional[List[str]] = None,
                override: bool = False) -> None:
        """
        Register a template class with the registry.

        Args:
            template_class: The template class to register
            name: Optional custom name for the template
            aliases: Optional list of aliases for the template
            override: Whether to override existing template

        Raises:
            TemplateRegistrationError: If registration fails
        """
        try:
            # Get metadata from template
            temp_instance = template_class()
            metadata = temp_instance.metadata

            # Use provided name or default to metadata name
            template_name = name or metadata.name

            # Check if template already exists
            if template_name in self._templates and not override:
                raise TemplateRegistrationError(
                    f"Template '{template_name}' already registered. "
                    f"Use override=True to replace it."
                )

            # Validate template class
            if not issubclass(template_class, BaseTemplate):
                raise TemplateRegistrationError(
                    f"Template class must inherit from BaseTemplate"
                )

            # Register template
            self._templates[template_name] = template_class
            self._metadata[template_name] = metadata
            self._categories[metadata.template_type].add(template_name)

            # Register aliases
            if aliases:
                for alias in aliases:
                    if alias in self._aliases and not override:
                        raise TemplateRegistrationError(
                            f"Alias '{alias}' already exists for template "
                            f"'{self._aliases[alias]}'"
                        )
                    self._aliases[alias] = template_name

            self.logger.info(f"Registered template: {template_name}")

        except Exception as e:
            raise TemplateRegistrationError(f"Failed to register template: {e}")

    def unregister(self, name: str) -> bool:
        """
        Unregister a template from the registry.

        Args:
            name: Name of template to unregister

        Returns:
            True if template was unregistered, False if not found
        """
        if name not in self._templates:
            return False

        # Get metadata before removal
        metadata = self._metadata[name]

        # Remove from all data structures
        del self._templates[name]
        del self._metadata[name]
        self._categories[metadata.template_type].discard(name)

        # Remove aliases pointing to this template
        aliases_to_remove = [
            alias for alias, template_name in self._aliases.items()
            if template_name == name
        ]
        for alias in aliases_to_remove:
            del self._aliases[alias]

        self.logger.info(f"Unregistered template: {name}")
        return True

    def get(self, name: str, **config) -> BaseTemplate:
        """
        Get a template instance by name.

        Args:
            name: Name or alias of the template
            **config: Configuration to pass to template

        Returns:
            Configured template instance

        Raises:
            TemplateRegistrationError: If template not found
        """
        # Resolve alias if necessary
        actual_name = self._aliases.get(name, name)

        if actual_name not in self._templates:
            raise TemplateRegistrationError(f"Template '{name}' not found")

        template_class = self._templates[actual_name]
        return template_class(**config)

    def get_class(self, name: str) -> Type[BaseTemplate]:
        """
        Get a template class by name.

        Args:
            name: Name or alias of the template

        Returns:
            Template class

        Raises:
            TemplateRegistrationError: If template not found
        """
        actual_name = self._aliases.get(name, name)

        if actual_name not in self._templates:
            raise TemplateRegistrationError(f"Template '{name}' not found")

        return self._templates[actual_name]

    def list_templates(self,
                      template_type: Optional[TemplateType] = None,
                      include_metadata: bool = False) -> List[str]:
        """
        List all registered templates.

        Args:
            template_type: Optional filter by template type
            include_metadata: Whether to return metadata dict instead of names

        Returns:
            List of template names or metadata dicts
        """
        if template_type:
            names = list(self._categories.get(template_type, set()))
        else:
            names = list(self._templates.keys())

        if include_metadata:
            return [
                {
                    'name': name,
                    'metadata': self._metadata[name],
                    'aliases': [alias for alias, target in self._aliases.items() if target == name]
                }
                for name in names
            ]

        return sorted(names)

    def search(self,
               query: str,
               search_in: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for templates by query string.

        Args:
            query: Search query
            search_in: List of fields to search in ['name', 'description', 'tags']

        Returns:
            List of matching template info dictionaries
        """
        if search_in is None:
            search_in = ['name', 'description', 'tags']

        query_lower = query.lower()
        results = []

        for name, metadata in self._metadata.items():
            match_score = 0

            # Check name match
            if 'name' in search_in and query_lower in name.lower():
                match_score += 10

            # Check description match
            if 'description' in search_in and query_lower in metadata.description.lower():
                match_score += 5

            # Check tags match
            if 'tags' in search_in:
                for tag in metadata.tags:
                    if query_lower in tag.lower():
                        match_score += 3

            # Check aliases
            aliases = [alias for alias, target in self._aliases.items() if target == name]
            for alias in aliases:
                if query_lower in alias.lower():
                    match_score += 8

            if match_score > 0:
                results.append({
                    'name': name,
                    'metadata': metadata,
                    'aliases': aliases,
                    'score': match_score
                })

        # Sort by match score descending
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def add_plugin_path(self, path: Path) -> None:
        """
        Add a path to search for template plugins.

        Args:
            path: Path to plugin directory
        """
        path = Path(path).resolve()
        if path not in self._plugin_paths:
            self._plugin_paths.append(path)
            self.logger.info(f"Added plugin path: {path}")

    def discover_templates(self, module_name: str) -> int:
        """
        Discover and register templates from a module.

        Args:
            module_name: Name of module to search

        Returns:
            Number of templates discovered and registered
        """
        try:
            module = importlib.import_module(module_name)
            count = 0

            # Search for BaseTemplate subclasses in the module
            for name in dir(module):
                obj = getattr(module, name)

                if (inspect.isclass(obj) and
                    issubclass(obj, BaseTemplate) and
                    obj is not BaseTemplate):

                    try:
                        self.register(obj)
                        count += 1
                    except TemplateRegistrationError as e:
                        self.logger.warning(f"Failed to register {name}: {e}")

            self.logger.info(f"Discovered {count} templates from {module_name}")
            return count

        except ImportError as e:
            self.logger.error(f"Failed to import module {module_name}: {e}")
            return 0

    def load_plugins(self) -> int:
        """
        Load templates from all registered plugin paths.

        Returns:
            Total number of templates loaded
        """
        total_loaded = 0

        for plugin_path in self._plugin_paths:
            if not plugin_path.exists():
                self.logger.warning(f"Plugin path does not exist: {plugin_path}")
                continue

            # Add to sys.path temporarily
            str_path = str(plugin_path)
            if str_path not in sys.path:
                sys.path.insert(0, str_path)

            try:
                # Discover Python modules in the path
                for finder, module_name, ispkg in pkgutil.iter_modules([str_path]):
                    if module_name not in self._loaded_plugins:
                        loaded = self.discover_templates(module_name)
                        total_loaded += loaded
                        self._loaded_plugins.add(module_name)

            except Exception as e:
                self.logger.error(f"Error loading plugins from {plugin_path}: {e}")

            finally:
                # Remove from sys.path
                if str_path in sys.path:
                    sys.path.remove(str_path)

        self.logger.info(f"Loaded {total_loaded} templates from plugins")
        return total_loaded

    def clear(self) -> None:
        """Clear all registered templates."""
        self._templates.clear()
        self._metadata.clear()
        self._categories.clear()
        self._aliases.clear()
        self._loaded_plugins.clear()
        self.logger.info("Cleared all registered templates")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with registry statistics
        """
        return {
            'total_templates': len(self._templates),
            'templates_by_type': {
                template_type.value: len(names)
                for template_type, names in self._categories.items()
            },
            'total_aliases': len(self._aliases),
            'plugin_paths': len(self._plugin_paths),
            'loaded_plugins': len(self._loaded_plugins)
        }

    def validate_registry(self) -> Dict[str, List[str]]:
        """
        Validate the registry for inconsistencies.

        Returns:
            Dictionary with validation results
        """
        issues = {
            'missing_metadata': [],
            'invalid_aliases': [],
            'duplicate_names': [],
            'orphaned_categories': []
        }

        # Check for missing metadata
        for name in self._templates:
            if name not in self._metadata:
                issues['missing_metadata'].append(name)

        # Check for invalid aliases
        for alias, target in self._aliases.items():
            if target not in self._templates:
                issues['invalid_aliases'].append(f"{alias} -> {target}")

        # Check for orphaned categories
        all_template_names = set(self._templates.keys())
        for template_type, names in self._categories.items():
            for name in names:
                if name not in all_template_names:
                    issues['orphaned_categories'].append(f"{template_type.value}: {name}")

        return issues


# Convenience functions for global registry access
_registry = None

def get_registry() -> TemplateRegistry:
    """Get the global template registry instance."""
    global _registry
    if _registry is None:
        _registry = TemplateRegistry.get_instance()
    return _registry


def register_template(template_class: Type[BaseTemplate],
                     name: Optional[str] = None,
                     aliases: Optional[List[str]] = None,
                     override: bool = False) -> None:
    """Register a template with the global registry."""
    get_registry().register(template_class, name, aliases, override)


def get_template(name: str, **config) -> BaseTemplate:
    """Get a template instance from the global registry."""
    return get_registry().get(name, **config)


def list_templates(template_type: Optional[TemplateType] = None) -> List[str]:
    """List all templates in the global registry."""
    return get_registry().list_templates(template_type)


def search_templates(query: str) -> List[Dict[str, Any]]:
    """Search for templates in the global registry."""
    return get_registry().search(query)


# Decorator for automatic registration
def auto_register(name: Optional[str] = None,
                 aliases: Optional[List[str]] = None,
                 override: bool = False):
    """
    Decorator to automatically register a template class.

    Args:
        name: Optional custom name for the template
        aliases: Optional list of aliases
        override: Whether to override existing template
    """
    def decorator(template_class: Type[BaseTemplate]) -> Type[BaseTemplate]:
        register_template(template_class, name, aliases, override)
        return template_class

    return decorator
