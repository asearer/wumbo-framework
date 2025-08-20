from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any

class TemplateType(Enum):
    SINGLE_LANGUAGE = "single_language"
    MULTI_LANGUAGE = "multi_language"

@dataclass
class TemplateMetadata:
    name: str
    version: str
    description: Optional[str] = None
    type: TemplateType = TemplateType.SINGLE_LANGUAGE

class BaseTemplate:
    """
    Base class for all templates.
    """
    def __init__(self, metadata: TemplateMetadata, content: str):
        self.metadata = metadata
        self.content = content

    def render(self, context: Dict[str, Any]) -> str:
        """
        Render the template with the given context.
        Override in subclasses for language-specific behavior.
        """
        return self.content.format(**context)


class ExecutionContext:
    pass


class ExecutionResult:
    pass