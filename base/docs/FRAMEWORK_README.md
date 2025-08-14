# 🌀 Wumbo Framework v2.0 - Universal Template System

**The ultimate modular, extensible framework for building templates that handle any kind of task.**

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework](https://img.shields.io/badge/framework-modular-green.svg)]()

---

## 🚀 What is Wumbo Framework?

Wumbo Framework is the evolution of the original wumbo function - transformed from a single universal function into a **complete modular framework** for building templates that can handle any kind of task imaginable.

Think of it as a **Swiss Army knife factory** - not just one tool, but a system for creating, managing, and composing an unlimited variety of specialized tools.

### 🎯 Key Features

- **🔧 Modular Architecture**: Build templates from reusable, composable components
- **📦 Built-in Templates**: Pre-built templates for common use cases
- **🔗 Template Composition**: Chain templates together to create complex pipelines  
- **📋 Registry System**: Discover, manage, and organize templates
- **🔌 Plugin Architecture**: Extend the framework with custom templates
- **⚡ Performance Monitoring**: Built-in execution context and timing
- **🔄 Backward Compatible**: Original wumbo function works exactly the same
- **🧩 Type Safe**: Full type hints and validation
- **📊 Real-world Ready**: Battle-tested patterns for production use

---

## 📦 Installation

```bash
# Install the framework
pip install wumbo-framework

# Or install in development mode
git clone https://github.com/wumbo/wumbo-framework.git
cd wumbo-framework
pip install -e .
```

---

## ⚡ Quick Start

### 1. Classic Wumbo (Backward Compatible)

```python
from wumbo_framework import wumbo

# Works exactly like the original!
result = wumbo(1, 2, 3, operation=lambda x: x ** 2)
# Output: [1, 4, 9]

# Full pipeline
result = wumbo("hello", "world",
              preprocess=str.upper,
              operation=lambda x: f"[{x}]",
              postprocess=lambda results: " | ".join(results))
# Output: "[HELLO] | [WORLD]"
```

### 2. Built-in Templates

```python
from wumbo_framework import create_data_processor, create_transformer

# Data processing template
processor = create_data_processor(
    preprocess=str.upper,
    operation=lambda x: f"✓ {x}",
    postprocess=lambda results: " | ".join(results)
)
result = processor("hello", "world")
# Output: "✓ HELLO | ✓ WORLD"

# Transform template with filtering and mapping
transformer = create_transformer(
    filter_func=lambda x: isinstance(x, int),
    map_func=lambda x: x ** 2
)
result = transformer(1, "hello", 2, 3, "world")
# Output: [1, 4, 9]
```

### 3. Template Composition

```python
from wumbo_framework import compose_templates

# Create a data processing pipeline
cleaner = create_transformer(filter_func=lambda x: isinstance(x, int))
processor = create_data_processor(operation=lambda x: x * 2)
aggregator = create_aggregator(aggregation_func=sum)

pipeline = compose_templates(cleaner, processor, aggregator)
result = pipeline(1, "invalid", 2, 3, "data", 4)
# Output: 20 (sum of [2, 4, 6, 8])
```

### 4. Registry System

```python
from wumbo_framework import get_template, list_templates, search_templates

# Get any template by name
template = get_template("classic_wumbo", operation=lambda x: x.upper())

# Discover available templates
templates = list_templates()
# Output: ['classic_wumbo', 'data_processor', 'api_client', ...]

# Search for specific templates
results = search_templates("data")
# Finds all templates related to data processing
```

---

## 🏗️ Framework Architecture

### Core Components

```
🌀 Wumbo Framework
├── 🔧 Core System
│   ├── BaseTemplate (Abstract base for all templates)
│   ├── TemplateRegistry (Central template management)
│   ├── ExecutionContext (Runtime context and logging)
│   └── CompositeTemplate (Template composition)
├── 📦 Built-in Templates
│   ├── DataProcessorTemplate (Universal data processing)
│   ├── APIClientTemplate (HTTP client with retries)
│   ├── ValidationTemplate (Data validation)
│   ├── AggregatorTemplate (Data aggregation)
│   ├── BatchProcessorTemplate (Batch processing)
│   ├── TransformTemplate (Map/filter operations)
│   ├── WorkflowTemplate (Multi-step workflows)
│   └── ClassicWumboTemplate (Original wumbo function)
├── 🔌 Plugin System
│   ├── Template Discovery
│   ├── Dynamic Loading
│   └── Extension Points
└── 🛠️ Utilities
    ├── Performance Monitoring
    ├── Error Handling
    └── Helper Functions
```

### Template Lifecycle

```
1. 📝 Definition     → Create template class or function
2. 📋 Registration   → Register with framework registry
3. 🔍 Discovery      → Find templates via registry
4. ⚙️  Instantiation → Create configured instances
5. 🚀 Execution      → Run with execution context
6. 📊 Monitoring     → Track performance and results
```

---

## 📚 Built-in Template Types

### 1. DataProcessorTemplate - Universal Data Processing
Perfect for the classic wumbo use case with preprocessing, operation, and postprocessing.

```python
processor = create_data_processor(
    preprocess=str.upper,           # Applied to each input
    operation=lambda x: f"[{x}]",   # Core transformation
    postprocess=lambda r: "|".join(r),  # Final processing
    as_dict=False,                  # Output format options
    fail_silently=True              # Error handling
)
```

### 2. APIClientTemplate - HTTP API Client
Built-in HTTP client with retries, error handling, and response processing.

```python
client = create_api_client(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"},
    timeout=30,
    retries=3
)
result = client("/users/123", method="GET")
```

### 3. ValidationTemplate - Data Validation
Validate data with custom validators and error collection.

```python
validators = [
    lambda x: isinstance(x, int),
    lambda x: x > 0,
    lambda x: x < 100
]
validator = create_validator(validators=validators)
results = validator(5, -2, 150, 25)
```

### 4. AggregatorTemplate - Data Aggregation
Aggregate data with optional grouping capabilities.

```python
# Simple aggregation
agg = create_aggregator(aggregation_func=sum)
result = agg(1, 2, 3, 4, 5)  # Output: 15

# Grouped aggregation  
grouped_agg = create_aggregator(
    aggregation_func=sum,
    group_by=lambda x: x % 2  # Group by even/odd
)
result = grouped_agg(1, 2, 3, 4, 5, 6)
# Output: {0: 12, 1: 9}  (even: 2+4+6, odd: 1+3+5)
```

### 5. BatchProcessorTemplate - Batch Processing
Process data in batches with optional parallel execution.

```python
processor = create_batch_processor(
    batch_size=3,
    processor_func=sum,
    parallel=True,
    max_workers=4
)
result = processor(1, 2, 3, 4, 5, 6, 7, 8, 9)
# Output: [6, 15, 24] (sum of each batch)
```

### 6. TransformTemplate - Map and Filter
Functional programming patterns for data transformation.

```python
transformer = create_transformer(
    filter_func=lambda x: isinstance(x, int),
    map_func=lambda x: x ** 2
)
result = transformer(1, "hello", 2, 3, "world")
# Output: [1, 4, 9]
```

### 7. WorkflowTemplate - Multi-Step Processing
Create workflows with conditional step execution.

```python
steps = [
    {"name": "clean", "func": lambda x: x.strip().lower()},
    {"name": "validate", "func": lambda x: x if len(x) > 3 else None},
    {"name": "format", "func": lambda x: f"✓ {x.title()}"}
]
workflow = create_workflow(steps=steps)
```

---

## 🎨 Creating Custom Templates

### Method 1: Class Inheritance

```python
from wumbo_framework import BaseTemplate, TemplateMetadata, TemplateType

class MyCustomTemplate(BaseTemplate):
    def __init__(self, custom_param="default", **config):
        self.custom_param = custom_param
        super().__init__(**config)
    
    def _get_metadata(self):
        return TemplateMetadata(
            name="my_custom_template",
            description="My custom template implementation",
            template_type=TemplateType.CUSTOM,
            version="1.0.0",
            tags=["custom", "example"]
        )
    
    def _execute_core(self, *args, context, **kwargs):
        # Your custom logic here
        return [f"{self.custom_param}:{arg}" for arg in args]

# Register and use
from wumbo_framework import register_template
register_template(MyCustomTemplate, "my_template")

template = get_template("my_template", custom_param="PREFIX")
result = template("hello", "world")
# Output: ["PREFIX:hello", "PREFIX:world"]
```

### Method 2: Function Decorator

```python
from wumbo_framework import template, TemplateType

@template("function_template", TemplateType.TRANSFORMER, "A function-based template")
def my_function_template(*args, context=None):
    """Transform inputs by doubling them."""
    return [arg * 2 for arg in args if isinstance(arg, (int, float))]

# Automatically creates and registers template class
template_instance = my_function_template()
result = template_instance(1, 2, 3, "skip", 4.5)
# Output: [2, 4, 6, 9.0]
```

### Method 3: Auto-Registration

```python
from wumbo_framework import auto_register

@auto_register("auto_template", aliases=["auto", "at"])
class AutoRegisteredTemplate(BaseTemplate):
    def _get_metadata(self):
        return TemplateMetadata(name="auto_template")
    
    def _execute_core(self, *args, context, **kwargs):
        return f"Processed {len(args)} items automatically"

# Immediately available in registry
result = get_template("auto")("a", "b", "c")
# Output: "Processed 3 items automatically"
```

---

## 🔗 Template Composition Patterns

### Sequential Pipeline
```python
step1 = create_transformer(filter_func=lambda x: x > 0)
step2 = create_data_processor(operation=lambda x: x ** 2)  
step3 = create_aggregator(aggregation_func=sum)

pipeline = compose_templates(step1, step2, step3)
```

### Conditional Workflow
```python
steps = [
    {"name": "process", "func": lambda x: x * 2},
    {"name": "bonus", "func": lambda x: x + 100, 
     "condition": lambda data, results: results["process"] > 50}
]
workflow = create_workflow(steps=steps)
```

### Parallel Processing
```python
batch_processor = create_batch_processor(
    batch_size=10,
    processor_func=my_processing_pipeline,
    parallel=True
)
```

---

## 📊 Real-World Examples

### Example 1: Data ETL Pipeline

```python
from wumbo_framework import compose_templates

# ETL pipeline for processing CSV-like data
csv_parser = create_transformer(
    filter_func=lambda row: len(row.split(',')) == 4,
    map_func=lambda row: dict(zip(['name', 'age', 'role', 'salary'], row.split(',')))
)

data_validator = create_validator(validators=[
    lambda person: person['age'].isdigit(),
    lambda person: person['salary'].isdigit(),
])

data_enhancer = create_data_processor(
    operation=lambda person: {
        **person,
        'age': int(person['age']),
        'salary': int(person['salary']),
        'age_group': 'senior' if int(person['age']) > 40 else 'junior'
    }
)

analytics = create_aggregator(
    aggregation_func=lambda people: {
        'total_employees': len(people),
        'average_salary': sum(p['salary'] for p in people) / len(people),
        'departments': list(set(p['role'] for p in people))
    }
)

etl_pipeline = compose_templates(csv_parser, data_enhancer, analytics)

# Process data
raw_data = [
    "John,30,Engineer,75000",
    "Jane,45,Manager,95000", 
    "Bob,25,Designer,55000"
]

result = etl_pipeline(*raw_data)
```

### Example 2: API Data Processing

```python
# Multi-step API data processing
api_client = create_api_client(
    base_url="https://api.service.com",
    headers={"Authorization": "Bearer token"}
)

response_processor = create_data_processor(
    operation=lambda response: response.get('data', []),
    postprocess=lambda items: [item for sublist in items for item in sublist]  # Flatten
)

data_transformer = create_transformer(
    filter_func=lambda item: item.get('status') == 'active',
    map_func=lambda item: {
        'id': item['id'],
        'name': item['name'], 
        'score': item.get('score', 0) * 100
    }
)

api_pipeline = compose_templates(api_client, response_processor, data_transformer)

# Fetch and process
results = api_pipeline("/users", "/products", "/orders")
```

---

## 📋 Registry and Discovery

### Template Registry Features

```python
from wumbo_framework import get_registry

registry = get_registry()

# Register custom templates
registry.register(MyTemplate, "my_template", aliases=["mt", "mine"])

# Discover templates
all_templates = registry.list_templates()
data_templates = registry.list_templates(template_type=TemplateType.DATA_PROCESSOR)

# Search functionality
search_results = registry.search("data processing")

# Template metadata
metadata = registry.get_metadata("my_template")
```

### Plugin System

```python
# Add plugin directories
registry.add_plugin_path(Path("./my_plugins"))
registry.add_plugin_path(Path("./shared_templates"))

# Auto-discover and load plugins
loaded_count = registry.load_plugins()

# Discover from modules
registry.discover_templates("my_custom_module")
```

---

## 🔧 Advanced Features

### Performance Monitoring

```python
# Execution context provides detailed monitoring
template = get_template("data_processor")
result = template.execute(data)

print(f"Execution time: {result.execution_time:.3f}s")
print(f"Success: {result.success}")
print(f"Execution ID: {result.context.execution_id}")
```

### Error Handling

```python
# Templates have built-in error handling
try:
    result = template.execute(invalid_data)
    if not result.success:
        print(f"Template failed: {result.error}")
        # Handle gracefully
except TemplateExecutionError as e:
    print(f"Execution error: {e}")
```

### Configuration Management

```python
# Templates accept configuration
template = create_data_processor(
    operation=my_operation,
    fail_silently=False,
    custom_setting="value"
)

# Configuration is accessible
print(template.config)
```

---

## 🎯 Best Practices

### 1. Template Design
- Keep templates focused on a single responsibility
- Use meaningful names and descriptions
- Add comprehensive metadata and tags
- Implement proper error handling

### 2. Composition Patterns
- Prefer composition over complex single templates
- Design templates to be composable and reusable
- Use consistent data formats between pipeline steps
- Handle edge cases gracefully

### 3. Registry Management
- Use descriptive names and aliases
- Tag templates appropriately for discovery
- Version your custom templates
- Document template capabilities

### 4. Performance Considerations
- Use batch processing for large datasets
- Enable parallel processing when appropriate
- Monitor execution times and optimize bottlenecks
- Cache expensive operations when possible

---

## 🧪 Testing Your Templates

```python
import unittest
from wumbo_framework import BaseTemplate

class TestMyTemplate(unittest.TestCase):
    def setUp(self):
        self.template = MyCustomTemplate()
    
    def test_basic_execution(self):
        result = self.template("test", "data")
        self.assertEqual(len(result), 2)
        
    def test_error_handling(self):
        result = self.template.execute("invalid")
        self.assertTrue(result.success)  # Should handle gracefully
        
    def test_composition(self):
        other = create_data_processor()
        composite = self.template.compose(other)
        result = composite("test")
        self.assertIsNotNone(result)
```

---

## 🤝 Contributing

We welcome contributions to the Wumbo Framework! Here's how to get started:

### Development Setup
```bash
git clone https://github.com/wumbo/wumbo-framework.git
cd wumbo-framework
pip install -e .[dev]
```

### Running Tests
```bash
python -m pytest tests/
python test_framework.py  # Run comprehensive tests
```

### Creating Templates
1. Follow the template creation patterns
2. Add comprehensive tests
3. Update documentation
4. Submit a pull request

### Guidelines
- Write clear, documented code
- Add type hints where possible
- Follow the existing code style
- Include comprehensive tests

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by functional programming patterns and pipeline architectures
- Built on the foundation of the original wumbo universal function
- Thanks to the community for feedback and contributions

---

## 🔮 What's Next?

The Wumbo Framework is continuously evolving. Upcoming features:

- **Async Templates**: Native support for asynchronous operations
- **Streaming Processing**: Real-time data stream handling
- **Visual Pipeline Builder**: GUI for creating template pipelines
- **Cloud Integration**: Native cloud service templates
- **ML Pipeline Support**: Machine learning workflow templates
- **Template Marketplace**: Share and discover community templates

---

## 📞 Support

- 📖 **Documentation**: [Full docs](https://wumbo-framework.readthedocs.io)
- 🐛 **Issues**: [GitHub Issues](https://github.com/wumbo/wumbo-framework/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/wumbo/wumbo-framework/discussions)
- 📧 **Email**: [support@wumbo.dev](mailto:support@wumbo.dev)

---

**🌀 Wumbo Framework - Where every template is possible, and every possibility becomes a template.** 🚀

---