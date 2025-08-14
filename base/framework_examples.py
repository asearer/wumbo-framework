#!/usr/bin/env python3
"""
🌀 Wumbo Framework - Comprehensive Examples
==========================================

This file demonstrates the full capabilities of the modular Wumbo framework,
showcasing how to use built-in templates, create custom templates, compose
pipelines, and leverage the framework's extensibility.

The examples progress from basic usage to advanced scenarios, demonstrating
real-world use cases and best practices.
"""

import json
import time
import math
import random
from typing import List, Dict, Any
from pathlib import Path

# Import framework components
from wumbo_framework import (
    # Core classes
    BaseTemplate, TemplateMetadata, TemplateType, ExecutionContext,
    template, auto_register,

    # Registry
    register_template, get_template, list_templates, search_templates,

    # Built-in templates and factories
    create_data_processor, create_api_client, create_validator,
    create_aggregator, create_batch_processor, create_transformer,
    create_workflow, create_classic_wumbo,

    # Classic function for backward compatibility
    wumbo,

    # Utilities
    create_template, compose_templates, get_framework_info
)


def separator(title: str, char: str = "=", width: int = 60):
    """Print a formatted separator."""
    print(f"\n{char * width}")
    print(f"🚀 {title}")
    print(f"{char * width}")


def example_backward_compatibility():
    """Demonstrate backward compatibility with original wumbo."""
    separator("Backward Compatibility - Classic Wumbo")

    print("The original wumbo function works exactly as before:")

    # Basic usage
    print("\n1. Basic passthrough:")
    result = wumbo(1, 2, 3)
    print(f"wumbo(1, 2, 3) = {result}")

    # With operation
    print("\n2. With operation function:")
    result = wumbo(2, 4, 6, operation=lambda x: x ** 2)
    print(f"wumbo(2, 4, 6, operation=lambda x: x ** 2) = {result}")

    # Full pipeline
    print("\n3. Full preprocessing -> operation -> postprocessing:")
    result = wumbo("hello", "world",
                  preprocess=str.upper,
                  operation=lambda x: f"[{x}]",
                  postprocess=lambda results: " | ".join(results))
    print(f'Full pipeline result: "{result}"')

    # Output formatting
    print("\n4. Different output formats:")
    print(f"As dict: {wumbo(10, 20, as_dict=True)}")
    print(f"As single: {wumbo(42, as_single=True)}")


def example_built_in_templates():
    """Demonstrate built-in template types."""
    separator("Built-in Template Types")

    print("1. DataProcessorTemplate - Universal data processing:")
    processor = create_data_processor(
        preprocess=lambda x: str(x).upper(),
        operation=lambda x: f"✓ {x}",
        postprocess=lambda results: " | ".join(results)
    )
    result = processor("hello", "world", 123)
    print(f"   Result: {result}")

    print("\n2. TransformTemplate - Map and filter operations:")
    transformer = create_transformer(
        filter_func=lambda x: isinstance(x, (int, float)),
        map_func=lambda x: x ** 2
    )
    result = transformer(1, "hello", 2, None, 3.5, "world", 4)
    print(f"   Filtered and squared numbers: {result}")

    print("\n3. ValidationTemplate - Data validation:")
    validators = [
        lambda x: isinstance(x, (int, float)),
        lambda x: x > 0,
        lambda x: x < 100
    ]
    validator = create_validator(validators=validators)
    result = validator(5, -2, 150, 25, "hello")
    print("   Validation results:")
    for r in result:
        status = "✅ VALID" if r["valid"] else "❌ INVALID"
        print(f"   {r['value']}: {status}")
        if r["errors"]:
            for error in r["errors"]:
                print(f"     - {error}")

    print("\n4. AggregatorTemplate - Data aggregation:")
    # Simple aggregation
    aggregator = create_aggregator(aggregation_func=sum)
    result = aggregator(1, 2, 3, 4, 5)
    print(f"   Sum aggregation: {result}")

    # Grouped aggregation
    grouped_agg = create_aggregator(
        aggregation_func=lambda group: {"sum": sum(group), "count": len(group), "avg": sum(group)/len(group)},
        group_by=lambda x: "even" if x % 2 == 0 else "odd"
    )
    result = grouped_agg(1, 2, 3, 4, 5, 6, 7, 8)
    print(f"   Grouped aggregation: {json.dumps(result, indent=4)}")

    print("\n5. BatchProcessorTemplate - Batch processing:")
    batch_processor = create_batch_processor(
        batch_size=3,
        processor_func=lambda batch: {"batch_sum": sum(batch), "batch_size": len(batch)}
    )
    result = batch_processor(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    print("   Batch processing results:")
    for i, batch_result in enumerate(result):
        print(f"   Batch {i+1}: {batch_result}")


def example_workflow_template():
    """Demonstrate the WorkflowTemplate for multi-step processing."""
    separator("Workflow Template - Multi-Step Processing")

    # Define a data processing workflow
    steps = [
        {
            "name": "clean_data",
            "func": lambda data: [x for x in data if isinstance(x, (int, float)) and x > 0]
        },
        {
            "name": "transform_data",
            "func": lambda data: [math.sqrt(x) for x in data]
        },
        {
            "name": "calculate_stats",
            "func": lambda data: {
                "values": data,
                "count": len(data),
                "sum": sum(data),
                "mean": sum(data) / len(data) if data else 0,
                "max": max(data) if data else 0,
                "min": min(data) if data else 0
            }
        }
    ]

    workflow = create_workflow(steps=steps)

    # Test data with mixed types and negative numbers
    test_data = [1, -2, 4, "hello", 9, None, 16, -5, 25, "world", 36]

    print(f"Input data: {test_data}")
    result = workflow(test_data)

    print("\nWorkflow execution results:")
    print(f"Final result: {json.dumps(result['final_result'], indent=2)}")

    print("\nStep-by-step results:")
    for step_name, step_result in result['step_results'].items():
        print(f"  {step_name}: {step_result}")


def example_conditional_workflow():
    """Demonstrate conditional workflow execution."""
    separator("Conditional Workflow Example")

    # Workflow with conditional steps
    steps = [
        {
            "name": "initial_processing",
            "func": lambda x: x * 2
        },
        {
            "name": "bonus_processing",
            "func": lambda x: x + 100,
            "condition": lambda data, results: results.get("initial_processing", 0) > 20
        },
        {
            "name": "final_processing",
            "func": lambda x: x / 2
        }
    ]

    workflow = create_workflow(steps=steps)

    print("Testing conditional workflow with different inputs:")

    test_values = [5, 15, 25]
    for value in test_values:
        result = workflow(value)
        initial = result["step_results"]["initial_processing"]
        has_bonus = "bonus_processing" in result["step_results"]
        final = result["final_result"]

        print(f"  Input: {value}")
        print(f"    Initial processing: {value} * 2 = {initial}")
        print(f"    Condition (> 20): {initial > 20} -> Bonus applied: {has_bonus}")
        if has_bonus:
            bonus = result["step_results"]["bonus_processing"]
            print(f"    Bonus processing: {initial} + 100 = {bonus}")
        print(f"    Final result: {final}")
        print()


def example_template_composition():
    """Demonstrate template composition and chaining."""
    separator("Template Composition and Chaining")

    print("Creating a data processing pipeline by composing multiple templates:")

    # Step 1: Clean and validate data
    cleaner = create_transformer(
        filter_func=lambda x: isinstance(x, (int, float)),
        map_func=lambda x: max(0, x)  # Ensure non-negative
    )

    # Step 2: Process and enhance data
    processor = create_data_processor(
        operation=lambda x: {"original": x, "squared": x**2, "sqrt": math.sqrt(x)}
    )

    # Step 3: Aggregate results
    aggregator = create_aggregator(
        aggregation_func=lambda items: {
            "count": len(items),
            "total_original": sum(item["original"] for item in items),
            "total_squared": sum(item["squared"] for item in items),
            "items": items
        }
    )

    # Compose into a pipeline
    pipeline = compose_templates(cleaner, processor, aggregator)

    # Test with mixed data
    test_data = [1, -2, 4, "invalid", 9, -1, 16, None, 25]
    print(f"Input data: {test_data}")

    result = pipeline(*test_data)
    print(f"\nPipeline result:")
    print(f"  Items processed: {result['count']}")
    print(f"  Sum of originals: {result['total_original']}")
    print(f"  Sum of squares: {result['total_squared']}")
    print("  Processed items:")
    for item in result['items']:
        print(f"    {item['original']} -> squared: {item['squared']}, sqrt: {item['sqrt']:.2f}")


def example_custom_templates():
    """Demonstrate creating custom templates."""
    separator("Custom Template Creation")

    print("1. Creating a custom template with class inheritance:")

    class MathOperationsTemplate(BaseTemplate):
        """Custom template for mathematical operations."""

        def __init__(self, operations=None, **config):
            self.operations = operations or ["square", "cube", "sqrt"]
            super().__init__(**config)

        def _get_metadata(self):
            return TemplateMetadata(
                name="math_operations",
                description="Performs multiple mathematical operations on input",
                template_type=TemplateType.DATA_PROCESSOR,
                version="1.0.0",
                tags=["math", "operations", "custom"],
                author="Framework Example"
            )

        def _execute_core(self, *args, context, **kwargs):
            results = []

            for value in args:
                if not isinstance(value, (int, float)):
                    context.logger.warning(f"Skipping non-numeric value: {value}")
                    continue

                operations_result = {"input": value}

                if "square" in self.operations:
                    operations_result["square"] = value ** 2
                if "cube" in self.operations:
                    operations_result["cube"] = value ** 3
                if "sqrt" in self.operations:
                    operations_result["sqrt"] = math.sqrt(abs(value))
                if "factorial" in self.operations and isinstance(value, int) and value >= 0:
                    operations_result["factorial"] = math.factorial(value)

                results.append(operations_result)

            return results

    # Register and use the custom template
    register_template(MathOperationsTemplate, "math_ops", aliases=["math", "ops"])

    math_template = get_template("math_ops", operations=["square", "sqrt", "factorial"])
    result = math_template(2, 4, 5, "invalid", 3.5)

    print("Mathematical operations results:")
    for ops_result in result:
        print(f"  Input: {ops_result['input']}")
        for op, value in ops_result.items():
            if op != "input":
                print(f"    {op}: {value}")
        print()

    print("2. Creating a template using the @template decorator:")

    @template("word_processor", TemplateType.TRANSFORMER, "Process and analyze words")
    def word_processing_template(*words, context=None):
        """Process words and return analysis."""
        results = []

        for word in words:
            if not isinstance(word, str):
                continue

            analysis = {
                "word": word,
                "length": len(word),
                "uppercase": word.upper(),
                "lowercase": word.lower(),
                "reversed": word[::-1],
                "vowel_count": sum(1 for char in word.lower() if char in "aeiou"),
                "is_palindrome": word.lower() == word.lower()[::-1]
            }
            results.append(analysis)

        return results

    # Register the decorated template
    word_template_class = word_processing_template
    register_template(word_template_class, "word_proc")

    word_processor = get_template("word_proc")
    result = word_processor("hello", "world", "radar", "python", "madam")

    print("Word processing results:")
    for analysis in result:
        print(f"  '{analysis['word']}': length={analysis['length']}, "
              f"vowels={analysis['vowel_count']}, palindrome={analysis['is_palindrome']}")


def example_auto_registration():
    """Demonstrate automatic template registration."""
    separator("Automatic Template Registration")

    print("Using @auto_register decorator for automatic registration:")

    @auto_register("stats_analyzer", aliases=["stats", "analyze"])
    class StatisticsTemplate(BaseTemplate):
        """Template for statistical analysis."""

        def _get_metadata(self):
            return TemplateMetadata(
                name="stats_analyzer",
                description="Statistical analysis of numeric data",
                template_type=TemplateType.AGGREGATOR,
                tags=["statistics", "analysis", "math"]
            )

        def _execute_core(self, *args, context, **kwargs):
            # Filter numeric values
            numeric_data = [x for x in args if isinstance(x, (int, float))]

            if not numeric_data:
                return {"error": "No numeric data provided"}

            n = len(numeric_data)
            total = sum(numeric_data)
            mean = total / n
            sorted_data = sorted(numeric_data)

            # Calculate median
            if n % 2 == 0:
                median = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
            else:
                median = sorted_data[n//2]

            # Calculate variance and standard deviation
            variance = sum((x - mean) ** 2 for x in numeric_data) / n
            std_dev = math.sqrt(variance)

            return {
                "count": n,
                "sum": total,
                "mean": mean,
                "median": median,
                "min": min(numeric_data),
                "max": max(numeric_data),
                "range": max(numeric_data) - min(numeric_data),
                "variance": variance,
                "std_deviation": std_dev,
                "data": sorted_data
            }

    # Template is automatically registered and can be used immediately
    stats_template = get_template("stats_analyzer")

    # Generate some test data
    test_data = [random.randint(1, 100) for _ in range(20)]
    result = stats_template(*test_data)

    print(f"Statistical analysis of {len(test_data)} random numbers:")
    print(f"  Data: {result['data']}")
    print(f"  Count: {result['count']}")
    print(f"  Mean: {result['mean']:.2f}")
    print(f"  Median: {result['median']:.2f}")
    print(f"  Min: {result['min']}, Max: {result['max']}")
    print(f"  Range: {result['range']}")
    print(f"  Standard Deviation: {result['std_deviation']:.2f}")


def example_registry_usage():
    """Demonstrate template registry features."""
    separator("Template Registry Features")

    print("1. Listing all available templates:")
    templates = list_templates()
    print(f"   Total templates: {len(templates)}")
    for template in templates[:10]:  # Show first 10
        print(f"   - {template}")
    if len(templates) > 10:
        print(f"   ... and {len(templates) - 10} more")

    print("\n2. Searching for templates:")
    search_results = search_templates("data")
    print("   Templates containing 'data':")
    for result in search_results[:5]:
        print(f"   - {result['name']}: {result['metadata'].description}")

    print("\n3. Getting template metadata:")
    template = get_template("classic_wumbo")
    print(f"   Template: {template.metadata.name}")
    print(f"   Type: {template.metadata.template_type.value}")
    print(f"   Description: {template.metadata.description}")
    print(f"   Tags: {', '.join(template.metadata.tags)}")

    print("\n4. Framework information:")
    info = get_framework_info()
    print(f"   Framework version: {info['version']}")
    print(f"   Total templates: {info['registry_stats']['total_templates']}")
    print("   Templates by type:")
    for template_type, count in info['registry_stats']['templates_by_type'].items():
        print(f"     {template_type}: {count}")


def example_real_world_scenarios():
    """Demonstrate real-world usage scenarios."""
    separator("Real-World Usage Scenarios")

    print("Scenario 1: Data ETL Pipeline")
    print("=" * 40)

    # Simulate CSV-like data processing
    raw_data = [
        "John,30,Engineer,75000",
        "Jane,25,Designer,65000",
        "Bob,35,Manager,85000",
        "Alice,28,Developer,70000",
        "Invalid,Data,Row",
        "Charlie,40,Director,95000"
    ]

    # Step 1: Parse CSV data
    csv_parser = create_transformer(
        filter_func=lambda row: len(row.split(',')) == 4,  # Valid CSV rows
        map_func=lambda row: {
            "name": row.split(',')[0],
            "age": int(row.split(',')[1]),
            "role": row.split(',')[2],
            "salary": int(row.split(',')[3])
        }
    )

    # Step 2: Data validation and enhancement
    data_enhancer = create_data_processor(
        operation=lambda person: {
            **person,
            "age_group": "young" if person["age"] < 30 else "experienced",
            "salary_band": "high" if person["salary"] > 70000 else "standard"
        }
    )

    # Step 3: Generate analytics
    analytics = create_aggregator(
        aggregation_func=lambda people: {
            "total_employees": len(people),
            "average_age": sum(p["age"] for p in people) / len(people),
            "average_salary": sum(p["salary"] for p in people) / len(people),
            "roles": list(set(p["role"] for p in people)),
            "high_earners": [p["name"] for p in people if p["salary"] > 75000],
            "by_age_group": {
                "young": len([p for p in people if p["age_group"] == "young"]),
                "experienced": len([p for p in people if p["age_group"] == "experienced"])
            }
        }
    )

    # Create ETL pipeline
    etl_pipeline = compose_templates(csv_parser, data_enhancer, analytics)

    print(f"Processing {len(raw_data)} CSV rows...")
    result = etl_pipeline(*raw_data)

    print("ETL Results:")
    print(f"  Total employees: {result['total_employees']}")
    print(f"  Average age: {result['average_age']:.1f} years")
    print(f"  Average salary: ${result['average_salary']:,.0f}")
    print(f"  Roles: {', '.join(result['roles'])}")
    print(f"  High earners: {', '.join(result['high_earners'])}")
    print(f"  Age distribution: {result['by_age_group']}")

    print(f"\nScenario 2: Text Processing and Analysis")
    print("=" * 40)

    # Text data
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "Python is an amazing programming language",
        "Machine learning and AI are transforming industries",
        "Data science requires statistical knowledge",
        "Cloud computing enables scalable applications"
    ]

    # Create text analysis pipeline
    text_processor = create_data_processor(
        preprocess=lambda text: text.lower().replace(',', '').split(),
        operation=lambda words: {
            "word_count": len(words),
            "unique_words": len(set(words)),
            "avg_word_length": sum(len(word) for word in words) / len(words),
            "long_words": [word for word in words if len(word) > 6]
        }
    )

    text_aggregator = create_aggregator(
        aggregation_func=lambda analyses: {
            "total_texts": len(analyses),
            "total_words": sum(a["word_count"] for a in analyses),
            "total_unique_words": len(set(word for a in analyses for word in a.get("long_words", []))),
            "avg_words_per_text": sum(a["word_count"] for a in analyses) / len(analyses),
            "all_long_words": list(set(word for a in analyses for word in a.get("long_words", [])))
        }
    )

    text_pipeline = compose_templates(text_processor, text_aggregator)

    result = text_pipeline(*texts)

    print("Text Analysis Results:")
    print(f"  Texts analyzed: {result['total_texts']}")
    print(f"  Total words: {result['total_words']}")
    print(f"  Average words per text: {result['avg_words_per_text']:.1f}")
    print(f"  Unique long words (>6 chars): {result['total_unique_words']}")
    print(f"  Long words found: {', '.join(result['all_long_words'][:10])}...")


def example_performance_monitoring():
    """Demonstrate performance monitoring and execution context."""
    separator("Performance Monitoring and Execution Context")

    # Create a computationally intensive template
    class PerformanceTestTemplate(BaseTemplate):
        def _get_metadata(self):
            return TemplateMetadata(
                name="performance_test",
                description="Template for performance testing"
            )

        def _execute_core(self, *args, context, **kwargs):
            import time

            results = []
            for i, value in enumerate(args):
                context.logger.info(f"Processing item {i+1}/{len(args)}: {value}")

                # Simulate some work
                time.sleep(0.1)  # 100ms delay per item

                # Perform computation
                result = sum(range(value * 1000))
                results.append({"input": value, "computation": result})

            return results

    register_template(PerformanceTestTemplate, "perf_test")

    # Test performance with timing
    perf_template = get_template("perf_test")

    print("Running performance test with execution context monitoring...")
    start_time = time.time()

    execution_result = perf_template.execute(5, 10, 15, 20)

    end_time = time.time()

    print(f"\nPerformance Results:")
    print(f"  Execution successful: {execution_result.success}")
    print(f"  Total execution time: {execution_result.execution_time:.3f} seconds")
    print(f"  Items processed: {len(execution_result.data)}")
    print(f"  Average time per item: {execution_result.execution_time/len(execution_result.data):.3f} seconds")

    print(f"  Execution ID: {execution_result.context.execution_id}")
    print(f"  Template used: {execution_result.context.template_name}")


def main():
    """Run all framework examples."""
    print("🌀 WUMBO FRAMEWORK COMPREHENSIVE EXAMPLES")
    print("=========================================")
    print("Demonstrating the full capabilities of the modular Wumbo framework")

    try:
        # Core examples
        example_backward_compatibility()
        example_built_in_templates()
        example_workflow_template()
        example_conditional_workflow()
        example_template_composition()

        # Advanced examples
        example_custom_templates()
        example_auto_registration()
        example_registry_usage()

        # Real-world scenarios
        example_real_world_scenarios()
        example_performance_monitoring()

        separator("🎉 Framework Examples Complete!", "=", 60)
        print("All examples have been demonstrated successfully!")
        print("\nKey takeaways:")
        print("• The framework maintains full backward compatibility with classic wumbo")
        print("• Built-in templates cover common use cases out of the box")
        print("• Custom templates can be easily created and registered")
        print("• Template composition enables powerful data processing pipelines")
        print("• The registry system provides discovery and management capabilities")
        print("• Real-world scenarios demonstrate practical applications")
        print("• Performance monitoring and execution context provide visibility")
        print("\nStart building your own templates and pipelines! 🚀")

    except Exception as e:
        print(f"❌ An error occurred while running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
