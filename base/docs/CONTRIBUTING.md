# 🌀 Contributing to Wumbo Framework

Welcome to the Wumbo Framework community! We're excited that you want to contribute to making the most versatile and extensible template system even better.

## 🎯 Table of Contents

- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Style and Standards](#code-style-and-standards)
- [Testing Requirements](#testing-requirements)
- [Submitting Contributions](#submitting-contributions)
- [Community Guidelines](#community-guidelines)
- [Recognition Program](#recognition-program)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.6+ (recommended: Python 3.9+)
- Git
- Basic understanding of Python programming
- Familiarity with object-oriented programming concepts

---

## 🛠️ Development Environment Setup

### Option 1: Local Development (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/wumbo/wumbo-framework.git
cd wumbo-framework

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install development dependencies
pip install -e ".[dev]"

# 5. Install pre-commit hooks
pre-commit install

# 6. Run tests to verify setup
python -m pytest tests/
python test_framework.py
```

### Option 2: Docker Development Environment

```bash
# Build development container
docker build -t wumbo-dev -f Dockerfile.dev .

# Run development container
docker run -it --rm -v $(pwd):/workspace wumbo-dev bash

# Inside container, run tests
python -m pytest tests/
```

### Option 3: GitHub Codespaces

Click the "Code" button on GitHub and select "Open with Codespaces" for a fully configured cloud development environment.

### Development Dependencies

The framework uses the following development tools:

```bash
# Core testing
pytest>=6.2.0
pytest-cov>=2.12.0
pytest-mock>=3.6.0
pytest-asyncio>=0.15.0

# Code quality
black>=21.0.0           # Code formatting
isort>=5.9.0            # Import sorting
flake8>=3.9.0           # Linting
mypy>=0.900             # Type checking
pre-commit>=2.15.0      # Git hooks

# Documentation
sphinx>=4.0.0
sphinx-rtd-theme>=0.5.0
mkdocs>=1.2.0

# Performance testing
pytest-benchmark>=3.4.0

# Optional dependencies for specific templates
requests>=2.25.0        # For APIClientTemplate
numpy>=1.20.0          # For mathematical templates
pandas>=1.3.0          # For data processing templates
```

---

## 📋 Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

#### 🔧 **Core Framework**
- Bug fixes in core components
- Performance optimizations
- New core features (ExecutionContext, Registry, etc.)
- Architecture improvements

#### 📦 **Built-in Templates**
- New template types for common use cases
- Improvements to existing templates
- Template performance optimizations
- Better error handling in templates

#### 🔌 **Plugin System**
- Plugin loading improvements
- New plugin interfaces
- Plugin documentation and examples

#### 🛠️ **Utilities and Helpers**
- New utility functions
- Performance improvements
- Cross-platform compatibility fixes

#### 📚 **Documentation**
- API documentation improvements
- Tutorial and example additions
- Translation to other languages
- Video tutorials and guides

#### 🧪 **Testing**
- New test cases
- Performance benchmarks
- Integration tests
- Edge case testing

### Contribution Process

1. **Check existing issues** - Look for related issues or feature requests
2. **Create an issue** - If none exists, create one describing your contribution
3. **Discuss approach** - Get feedback on your proposed solution
4. **Fork and develop** - Create your implementation
5. **Test thoroughly** - Ensure all tests pass
6. **Submit pull request** - Follow our PR template
7. **Code review** - Address feedback from maintainers
8. **Merge** - Your contribution becomes part of the framework!

---

## 🎨 Code Style and Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

```python
# Line length: 88 characters (Black default)
# Imports: isort configuration
# Quotes: Double quotes for strings
# Type hints: Required for all public APIs

# Example of good style:
from typing import Any, Dict, List, Optional, Union
from wumbo_framework.core.base import BaseTemplate, TemplateMetadata


class ExampleTemplate(BaseTemplate[List[str]]):
    """
    Example template demonstrating code style.

    This template processes string inputs and returns a list of processed strings.
    It demonstrates proper docstring format, type hints, and code organization.

    Args:
        processor_func: Function to apply to each string input
        fail_silently: Whether to ignore processing errors
        **config: Additional configuration parameters
    """

    def __init__(
        self,
        processor_func: Optional[Callable[[str], str]] = None,
        fail_silently: bool = True,
        **config: Any
    ) -> None:
        self.processor_func = processor_func or str.upper
        self.fail_silently = fail_silently
        super().__init__(**config)

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="example_template",
            description="Example template for demonstration",
            template_type=TemplateType.CUSTOM,
            version="1.0.0",
            tags=["example", "demo"],
            author="Your Name"
        )

    def _execute_core(
        self,
        *args: str,
        context: ExecutionContext,
        **kwargs: Any
    ) -> List[str]:
        results = []

        for arg in args:
            try:
                processed = self.processor_func(arg)
                results.append(processed)
            except Exception as e:
                context.logger.warning(f"Processing failed for {arg}: {e}")
                if self.fail_silently:
                    results.append(arg)  # Return original on error
                else:
                    raise

        return results
```

### Automated Code Formatting

We use automated tools to maintain consistent code style:

```bash
# Format code with Black
black wumbo_framework/ tests/

# Sort imports with isort
isort wumbo_framework/ tests/

# Check code style with flake8
flake8 wumbo_framework/ tests/

# Type checking with mypy
mypy wumbo_framework/
```

### Git Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(templates): add StreamProcessorTemplate for real-time processing
fix(registry): resolve thread safety issue in template registration
docs(readme): update installation instructions for Python 3.9+
test(core): add comprehensive tests for ExecutionContext
```

---

## 🧪 Testing Requirements

### Test Categories

#### Unit Tests
```python
# test_example_template.py
import pytest
from wumbo_framework import BaseTemplate
from your_module import ExampleTemplate


class TestExampleTemplate:
    def test_basic_functionality(self):
        template = ExampleTemplate()
        result = template("hello", "world")
        assert result == ["HELLO", "WORLD"]

    def test_error_handling(self):
        def failing_processor(x):
            raise ValueError("Test error")

        template = ExampleTemplate(
            processor_func=failing_processor,
            fail_silently=True
        )
        result = template("test")
        assert result == ["test"]  # Returns original on error

    def test_metadata(self):
        template = ExampleTemplate()
        metadata = template.metadata
        assert metadata.name == "example_template"
        assert "example" in metadata.tags
```

#### Integration Tests
```python
def test_template_composition():
    """Test template composition and pipeline execution."""
    template1 = ExampleTemplate(processor_func=str.upper)
    template2 = ExampleTemplate(processor_func=lambda x: f"[{x}]")

    pipeline = compose_templates(template1, template2)
    result = pipeline("hello")

    assert result == ["[HELLO]"]
```

#### Performance Tests
```python
def test_performance_benchmark(benchmark):
    """Benchmark template execution performance."""
    template = ExampleTemplate()
    data = ["test"] * 1000

    result = benchmark(template, *data)
    assert len(result) == 1000
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wumbo_framework --cov-report=html

# Run specific test file
pytest tests/test_example_template.py

# Run performance benchmarks
pytest --benchmark-only

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v
```

### Test Requirements

- **Coverage**: Minimum 85% code coverage for new code
- **Performance**: No significant performance regressions
- **Compatibility**: Tests must pass on Python 3.6+
- **Documentation**: All public APIs must have docstring tests

---

## 📝 Submitting Contributions

### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines

3. **Run tests and linting**:
   ```bash
   # Run all tests
   python -m pytest tests/
   python test_framework.py

   # Check code style
   black --check wumbo_framework/ tests/
   flake8 wumbo_framework/ tests/
   mypy wumbo_framework/
   ```

4. **Update documentation** if needed

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat(templates): add new ExampleTemplate"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** using our template

### Pull Request Template

When creating a PR, please include:

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated documentation

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Related Issues
Closes #123
```

### Review Process

1. **Automated checks** run (tests, linting, security)
2. **Maintainer review** - Code quality and design review
3. **Community feedback** - Other contributors may provide input
4. **Address feedback** - Make requested changes
5. **Final approval** - Maintainer approves the PR
6. **Merge** - Your contribution is merged!

---

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- **Be respectful** - Treat everyone with respect and kindness
- **Be collaborative** - Work together towards common goals
- **Be patient** - Help newcomers learn and grow
- **Be constructive** - Provide helpful feedback and suggestions
- **Be inclusive** - Welcome people of all backgrounds and skill levels

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and community discussion
- **Discord Server** - Real-time community chat
- **Stack Overflow** - Technical questions (tag: wumbo-framework)
- **Twitter** - Updates and announcements (@WumboFramework)

### Getting Help

If you need help:

1. **Check documentation** - README, API docs, examples
2. **Search existing issues** - Your question might already be answered
3. **Ask in discussions** - Community members are happy to help
4. **Join Discord** - Real-time help from the community

---

## 🏆 Recognition Program

### Contributor Levels

#### 🌱 **Newcomer**
- First contribution merged
- Welcome package and mentorship
- Special contributor badge

#### 🌿 **Regular Contributor**
- 5+ contributions merged
- Voting rights on feature proposals
- Early access to beta releases

#### 🌳 **Core Contributor**
- 25+ contributions merged
- Repository write access
- Participate in architecture decisions

#### 🌟 **Maintainer**
- Significant ongoing contributions
- Leadership in community building
- Full repository permissions

### Recognition Rewards

- **Contributor Spotlight** - Monthly featured contributors
- **Conference Speaking** - Opportunities to present at conferences
- **Swag Store Access** - Exclusive Wumbo merchandise
- **Annual Contributors Summit** - Invitation to annual meetup
- **Professional References** - LinkedIn recommendations from maintainers

### Hall of Fame

We maintain a hall of fame recognizing significant contributions:

- **Template Creators** - Authors of widely-used templates
- **Performance Champions** - Contributors who significantly improve performance
- **Documentation Heroes** - Major documentation contributors
- **Bug Hunters** - Contributors who find and fix critical issues
- **Community Builders** - Those who help grow and nurture the community

---

## 🚀 Onboarding Checklist

For new contributors:

### First Week
- [ ] Set up development environment
- [ ] Read contributing guidelines
- [ ] Join community Discord server
- [ ] Pick a "good first issue" to work on
- [ ] Introduce yourself in discussions

### First Month
- [ ] Submit first pull request
- [ ] Participate in code review process
- [ ] Help answer questions in discussions
- [ ] Write or improve documentation
- [ ] Attend community meeting

### Ongoing
- [ ] Regularly contribute code or documentation
- [ ] Mentor new contributors
- [ ] Propose new features or improvements
- [ ] Share the framework with others
- [ ] Participate in community events

---

## 🔧 Development Tips

### Debugging Templates

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use execution context for debugging
def debug_template(*args, context=None, **kwargs):
    if context:
        context.logger.debug(f"Processing {len(args)} items")
        context.logger.debug(f"Args: {args}")
        context.logger.debug(f"Kwargs: {kwargs}")

    # Your template logic here
    return processed_results
```

### Testing Performance

```python
import time
from wumbo_framework.utils.helpers import Timer

# Time template execution
with Timer("template_execution") as timer:
    result = template.execute(large_dataset)

print(f"Execution took {timer.elapsed:.3f} seconds")
```

### Memory Profiling

```python
import tracemalloc

# Profile memory usage
tracemalloc.start()

# Your template execution
result = template.execute(data)

# Get memory statistics
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

---

## 🎯 Roadmap Contributions

Want to contribute to future features? Check our [ROADMAP.md](ROADMAP.md) for:

- **Phase 1**: Performance & Reliability improvements
- **Phase 2**: AI-enhanced templates
- **Phase 3**: Cloud-native architecture
- **Phase 4**: Advanced analytics
- **Phase 5**: Community marketplace
