"""
🌀 Wumbo Framework - Comprehensive Test Suite

This module contains comprehensive tests for the modular Wumbo framework,
testing all core components, built-in templates, registry functionality,
and framework features.
"""

import unittest
import json
import time
import threading
import sys
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor
import tempfile
import shutil
from pathlib import Path

# Import framework components
from wumbo_framework import (
    # Core classes
    BaseTemplate, TemplateMetadata, TemplateType, ExecutionContext,
    ExecutionResult, CompositeTemplate, template,

    # Registry
    TemplateRegistry, get_registry, register_template, get_template,
    list_templates, search_templates, auto_register,

    # Built-in templates
    DataProcessorTemplate, APIClientTemplate, ValidationTemplate,
    AggregatorTemplate, BatchProcessorTemplate, TransformTemplate,
    WorkflowTemplate, ClassicWumboTemplate,

    # Factory functions
    create_data_processor, create_api_client, create_validator,
    create_aggregator, create_batch_processor, create_transformer,
    create_workflow, create_classic_wumbo,

    # Classic function
    wumbo,

    # Convenience functions
    create_template, discover_templates, compose_templates,
    get_framework_info,

    # Exceptions
    TemplateError, TemplateConfigError, TemplateExecutionError,
    TemplateRegistrationError
)


class TestBaseTemplate(unittest.TestCase):
    """Test the BaseTemplate abstract class and core functionality."""

    def setUp(self):
        """Set up test template class."""
        class TestTemplate(BaseTemplate):
            def _get_metadata(self):
                return TemplateMetadata(
                    name="test_template",
                    description="A test template",
                    template_type=TemplateType.CUSTOM
                )

            def _execute_core(self, *args, context, **kwargs):
                return list(args)

        self.TestTemplate = TestTemplate

    def test_template_initialization(self):
        """Test template initialization."""
        template = self.TestTemplate(test_config="value")
        self.assertEqual(template.config["test_config"], "value")
        self.assertEqual(template.metadata.name, "test_template")

    def test_template_execution(self):
        """Test template execution."""
        template = self.TestTemplate()
        result = template.execute(1, 2, 3)

        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.data, [1, 2, 3])
        self.assertIsNotNone(result.execution_time)

    def test_template_callable(self):
        """Test template as callable."""
        template = self.TestTemplate()
        result = template(1, 2, 3)
        self.assertEqual(result, [1, 2, 3])

    def test_template_error_handling(self):
        """Test template error handling."""
        class ErrorTemplate(BaseTemplate):
            def _get_metadata(self):
                return TemplateMetadata(name="error_template")

            def _execute_core(self, *args, context, **kwargs):
                raise ValueError("Test error")

        template = ErrorTemplate()
        result = template.execute(1, 2, 3)

        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValueError)

    def test_template_composition(self):
        """Test template composition."""
        template1 = self.TestTemplate()
        template2 = self.TestTemplate()

        composite = template1.compose(template2)
        self.assertIsInstance(composite, CompositeTemplate)

    def test_preprocessing_and_postprocessing(self):
        """Test preprocessing and postprocessing hooks."""
        class ProcessingTemplate(BaseTemplate):
            def _get_metadata(self):
                return TemplateMetadata(name="processing_template")

            def _preprocess(self, *args, context, **kwargs):
                return tuple(arg * 2 for arg in args)

            def _execute_core(self, *args, context, **kwargs):
                return list(args)

            def _postprocess(self, result, context):
                return sum(result)

        template = ProcessingTemplate()
        result = template(1, 2, 3)
        self.assertEqual(result, 12)  # (1*2 + 2*2 + 3*2) = 12


class TestTemplateRegistry(unittest.TestCase):
    """Test the template registry functionality."""

    def setUp(self):
        """Set up test registry."""
        # Use a fresh registry instance for each test
        TemplateRegistry._instance = None
        self.registry = TemplateRegistry.get_instance()

        # Create test template
        class TestTemplate(BaseTemplate):
            def _get_metadata(self):
                return TemplateMetadata(
                    name="test_template",
                    description="Test template",
                    template_type=TemplateType.CUSTOM,
                    tags=["test", "example"]
                )

            def _execute_core(self, *args, context, **kwargs):
                return list(args)

        self.TestTemplate = TestTemplate

    def tearDown(self):
        """Clean up registry."""
        self.registry.clear()

    def test_template_registration(self):
        """Test template registration."""
        self.registry.register(self.TestTemplate)

        templates = self.registry.list_templates()
        self.assertIn("test_template", templates)

    def test_template_registration_with_aliases(self):
        """Test template registration with aliases."""
        self.registry.register(self.TestTemplate, aliases=["test", "example"])

        # Test getting by alias
        template = self.registry.get("test")
        self.assertIsInstance(template, self.TestTemplate)

    def test_template_retrieval(self):
        """Test template retrieval."""
        self.registry.register(self.TestTemplate)

        template = self.registry.get("test_template")
        self.assertIsInstance(template, self.TestTemplate)

    def test_template_search(self):
        """Test template search functionality."""
        self.registry.register(self.TestTemplate)

        results = self.registry.search("test")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test_template")

    def test_template_unregistration(self):
        """Test template unregistration."""
        self.registry.register(self.TestTemplate)
        self.assertTrue(self.registry.unregister("test_template"))

        templates = self.registry.list_templates()
        self.assertNotIn("test_template", templates)

    def test_registry_validation(self):
        """Test registry validation."""
        self.registry.register(self.TestTemplate)
        issues = self.registry.validate_registry()

        # Should have no issues with a properly registered template
        self.assertEqual(len(issues["missing_metadata"]), 0)
        self.assertEqual(len(issues["invalid_aliases"]), 0)


class TestDataProcessorTemplate(unittest.TestCase):
    """Test the DataProcessorTemplate."""

    def test_basic_data_processing(self):
        """Test basic data processing."""
        processor = create_data_processor()
        result = processor(1, 2, 3)
        self.assertEqual(result, [1, 2, 3])

    def test_data_processing_with_operation(self):
        """Test data processing with operation function."""
        processor = create_data_processor(operation=lambda x: x * 2)
        result = processor(1, 2, 3)
        self.assertEqual(result, [2, 4, 6])

    def test_data_processing_with_preprocessing(self):
        """Test data processing with preprocessing."""
        processor = create_data_processor(
            preprocess=str.upper,
            operation=lambda x: f"[{x}]"
        )
        result = processor("hello", "world")
        self.assertEqual(result, ["[HELLO]", "[WORLD]"])

    def test_data_processing_with_postprocessing(self):
        """Test data processing with postprocessing."""
        processor = create_data_processor(
            operation=lambda x: x * 2,
            postprocess=sum
        )
        result = processor(1, 2, 3)
        self.assertEqual(result, 12)  # (1*2 + 2*2 + 3*2) = 12

    def test_data_processing_output_formats(self):
        """Test different output formats."""
        # Test as_dict
        processor = create_data_processor(as_dict=True)
        result = processor(1, 2, 3)
        expected = {"item_0": 1, "item_1": 2, "item_2": 3}
        self.assertEqual(result, expected)

        # Test as_single
        processor = create_data_processor(as_single=True)
        result = processor(42)
        self.assertEqual(result, 42)

    def test_error_handling(self):
        """Test error handling in data processing."""
        def error_operation(x):
            if x == "error":
                raise ValueError("Test error")
            return x.upper()

        # Test fail_silently=True (default)
        processor = create_data_processor(operation=error_operation)
        result = processor("hello", "error", "world")
        self.assertEqual(result, ["HELLO", None, "WORLD"])

        # Test fail_silently=False
        processor = create_data_processor(
            operation=error_operation,
            fail_silently=False
        )
        with self.assertRaises(ValueError):
            processor("hello", "error", "world")


class TestAPIClientTemplate(unittest.TestCase):
    """Test the APIClientTemplate."""

    @patch('wumbo_framework.templates.builtins.requests.request')
    def test_api_client_get_request(self, mock_request):
        """Test API client GET request."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        client = create_api_client(base_url="https://api.example.com")
        result = client("/test")

        self.assertEqual(result, {"data": "test"})
        mock_request.assert_called_once()

    @patch('wumbo_framework.templates.builtins.requests.request')
    def test_api_client_with_retries(self, mock_request):
        """Test API client retry functionality."""
        # Mock to fail twice, then succeed
        mock_request.side_effect = [
            Exception("Connection error"),
            Exception("Connection error"),
            Mock(json=lambda: {"data": "success"}, raise_for_status=lambda: None)
        ]

        client = create_api_client(retries=3, retry_delay=0.01)
        result = client("/test")

        self.assertEqual(result, {"data": "success"})
        self.assertEqual(mock_request.call_count, 3)


class TestValidationTemplate(unittest.TestCase):
    """Test the ValidationTemplate."""

    def test_validation_success(self):
        """Test successful validation."""
        validators = [
            lambda x: isinstance(x, int),
            lambda x: x > 0
        ]

        validator = create_validator(validators=validators)
        result = validator(5, 10)

        self.assertTrue(all(r["valid"] for r in result))

    def test_validation_failure(self):
        """Test validation failure."""
        validators = [
            lambda x: isinstance(x, int),
            lambda x: x > 0
        ]

        validator = create_validator(validators=validators)
        result = validator(5, -1, "hello")

        # First should pass, second should fail (negative), third should fail (not int)
        self.assertTrue(result[0]["valid"])
        self.assertFalse(result[1]["valid"])
        self.assertFalse(result[2]["valid"])

    def test_strict_validation(self):
        """Test strict validation mode."""
        validators = [lambda x: x > 0]

        validator = create_validator(validators=validators, strict=True)

        with self.assertRaises(ValueError):
            validator(5, -1, 10)


class TestAggregatorTemplate(unittest.TestCase):
    """Test the AggregatorTemplate."""

    def test_basic_aggregation(self):
        """Test basic aggregation."""
        aggregator = create_aggregator(aggregation_func=sum)
        result = aggregator(1, 2, 3, 4, 5)
        self.assertEqual(result, 15)

    def test_aggregation_with_grouping(self):
        """Test aggregation with grouping."""
        # Group numbers by even/odd
        aggregator = create_aggregator(
            aggregation_func=sum,
            group_by=lambda x: x % 2
        )
        result = aggregator(1, 2, 3, 4, 5, 6)

        # Odd numbers (1, 3, 5) sum to 9, even numbers (2, 4, 6) sum to 12
        self.assertEqual(result[1], 9)  # Odd group
        self.assertEqual(result[0], 12)  # Even group


class TestBatchProcessorTemplate(unittest.TestCase):
    """Test the BatchProcessorTemplate."""

    def test_batch_processing(self):
        """Test basic batch processing."""
        processor = create_batch_processor(
            batch_size=2,
            processor_func=sum
        )
        result = processor(1, 2, 3, 4, 5)

        # Should create batches [1,2], [3,4], [5] and sum each
        expected = [3, 7, 5]  # sum([1,2]), sum([3,4]), sum([5])
        self.assertEqual(result, expected)

    def test_parallel_batch_processing(self):
        """Test parallel batch processing."""
        processor = create_batch_processor(
            batch_size=2,
            processor_func=sum,
            parallel=True,
            max_workers=2
        )
        result = processor(1, 2, 3, 4, 5)

        # Results might be in different order due to parallel processing
        # but should contain the same sums
        result.sort()
        expected = [3, 5, 7]
        self.assertEqual(result, expected)


class TestTransformTemplate(unittest.TestCase):
    """Test the TransformTemplate."""

    def test_map_transformation(self):
        """Test map transformation."""
        transformer = create_transformer(map_func=lambda x: x * 2)
        result = transformer(1, 2, 3)
        self.assertEqual(result, [2, 4, 6])

    def test_filter_transformation(self):
        """Test filter transformation."""
        transformer = create_transformer(filter_func=lambda x: x % 2 == 0)
        result = transformer(1, 2, 3, 4, 5, 6)
        self.assertEqual(result, [2, 4, 6])

    def test_map_and_filter_transformation(self):
        """Test combined map and filter transformation."""
        transformer = create_transformer(
            map_func=lambda x: x * 2,
            filter_func=lambda x: x > 5
        )
        result = transformer(1, 2, 3, 4, 5)
        # First filter: [3, 4, 5], then map: [6, 8, 10]
        self.assertEqual(result, [6, 8, 10])


class TestWorkflowTemplate(unittest.TestCase):
    """Test the WorkflowTemplate."""

    def test_workflow_execution(self):
        """Test workflow execution."""
        steps = [
            {"name": "step1", "func": lambda x: x * 2},
            {"name": "step2", "func": lambda x: x + 10},
            {"name": "step3", "func": lambda x: x / 2}
        ]

        workflow = create_workflow(steps=steps)
        result = workflow(5)

        # (5 * 2 + 10) / 2 = 10
        self.assertEqual(result["final_result"], 10.0)
        self.assertEqual(result["step_results"]["step1"], 10)
        self.assertEqual(result["step_results"]["step2"], 20)
        self.assertEqual(result["step_results"]["step3"], 10.0)

    def test_conditional_workflow(self):
        """Test workflow with conditional steps."""
        steps = [
            {"name": "step1", "func": lambda x: x * 2},
            {
                "name": "step2",
                "func": lambda x: x + 100,
                "condition": lambda data, results: results.get("step1", 0) > 15
            },
            {"name": "step3", "func": lambda x: x + 1}
        ]

        workflow = create_workflow(steps=steps)

        # Test with value that makes condition True
        result = workflow(10)  # step1: 20, condition: 20 > 15 = True
        self.assertEqual(result["final_result"], 121)  # (10*2 + 100 + 1)

        # Test with value that makes condition False
        result = workflow(5)  # step1: 10, condition: 10 > 15 = False
        self.assertEqual(result["final_result"], 11)  # (5*2 + 1)


class TestClassicWumboTemplate(unittest.TestCase):
    """Test the ClassicWumboTemplate and backward compatibility."""

    def test_classic_wumbo_basic(self):
        """Test basic classic wumbo functionality."""
        result = wumbo(1, 2, 3)
        self.assertEqual(result, [1, 2, 3])

    def test_classic_wumbo_with_operation(self):
        """Test classic wumbo with operation."""
        result = wumbo(2, 4, 6, operation=lambda x: x ** 2)
        self.assertEqual(result, [4, 16, 36])

    def test_classic_wumbo_full_pipeline(self):
        """Test classic wumbo with full pipeline."""
        result = wumbo("hello", "world",
                      preprocess=str.upper,
                      operation=lambda x: f"[{x}]",
                      postprocess=lambda results: " | ".join(results))
        self.assertEqual(result, "[HELLO] | [WORLD]")

    def test_classic_wumbo_output_formats(self):
        """Test classic wumbo output formats."""
        # Test as_dict
        result = wumbo(100, 200, as_dict=True)
        expected = {"item_0": 100, "item_1": 200}
        self.assertEqual(result, expected)

        # Test as_single
        result = wumbo(42, as_single=True)
        self.assertEqual(result, 42)

    def test_classic_wumbo_template_creation(self):
        """Test classic wumbo template creation."""
        template = create_classic_wumbo(operation=lambda x: x * 3)
        result = template(2, 4, 6)
        self.assertEqual(result, [6, 12, 18])


class TestCompositeTemplate(unittest.TestCase):
    """Test template composition functionality."""

    def test_template_composition(self):
        """Test composing multiple templates."""
        step1 = create_transformer(map_func=lambda x: x * 2)
        step2 = create_data_processor(operation=lambda x: x + 10)

        composite = compose_templates(step1, step2)
        result = composite(1, 2, 3)

        # First step: [2, 4, 6], second step: [12, 14, 16]
        self.assertEqual(result, [12, 14, 16])

    def test_template_chaining(self):
        """Test template chaining with compose method."""
        step1 = create_data_processor(operation=lambda x: x * 2)
        step2 = create_data_processor(operation=sum)

        composite = step1.compose(step2)
        result = composite(1, 2, 3)

        # First step: [2, 4, 6], second step: sum([2, 4, 6]) = 12
        self.assertEqual(result, 12)


class TestFrameworkUtilities(unittest.TestCase):
    """Test framework utility functions."""

    def test_create_template(self):
        """Test create_template convenience function."""
        template = create_template("classic_wumbo", operation=lambda x: x * 2)
        result = template(5)
        self.assertEqual(result, [10])

    def test_get_framework_info(self):
        """Test get_framework_info function."""
        info = get_framework_info()

        self.assertIn("version", info)
        self.assertIn("registry_stats", info)
        self.assertIn("available_templates", info)
        self.assertIn("template_types", info)

    def test_list_templates(self):
        """Test list_templates function."""
        templates = list_templates()
        self.assertIsInstance(templates, list)
        # Should include built-in templates
        self.assertIn("classic_wumbo", templates)

    def test_search_templates(self):
        """Test search_templates function."""
        results = search_templates("data")
        self.assertIsInstance(results, list)
        # Should find templates with "data" in name or description


class TestTemplateDecorator(unittest.TestCase):
    """Test the @template decorator."""

    def test_template_decorator(self):
        """Test template decorator functionality."""
        @template("decorated_template",
                 template_type=TemplateType.CUSTOM,
                 description="A decorated template")
        def my_template_func(x, y):
            return x + y

        # Should return a template class
        template_class = my_template_func
        template_instance = template_class()

        self.assertIsInstance(template_instance, BaseTemplate)
        self.assertEqual(template_instance.metadata.name, "decorated_template")

        result = template_instance(5, 3)
        self.assertEqual(result, 8)


class TestAutoRegisterDecorator(unittest.TestCase):
    """Test the @auto_register decorator."""

    def setUp(self):
        """Set up registry for auto-registration tests."""
        # Clear registry before each test
        get_registry().clear()

    def test_auto_register_decorator(self):
        """Test auto_register decorator."""
        @auto_register("auto_test", aliases=["auto"])
        class AutoTestTemplate(BaseTemplate):
            def _get_metadata(self):
                return TemplateMetadata(
                    name="auto_test",
                    template_type=TemplateType.CUSTOM
                )

            def _execute_core(self, *args, context, **kwargs):
                return "auto_registered"

        # Template should be automatically registered
        template = get_template("auto_test")
        self.assertIsInstance(template, AutoTestTemplate)

        # Should also work with alias
        template_by_alias = get_template("auto")
        self.assertIsInstance(template_by_alias, AutoTestTemplate)


class TestConcurrencyAndThreadSafety(unittest.TestCase):
    """Test concurrency and thread safety aspects."""

    def test_template_thread_safety(self):
        """Test template execution in multiple threads."""
        template = create_data_processor(operation=lambda x: x * 2)

        def worker():
            return template(1, 2, 3)

        # Run template in multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker) for _ in range(10)]
            results = [future.result() for future in futures]

        # All results should be the same
        expected = [2, 4, 6]
        for result in results:
            self.assertEqual(result, expected)

    def test_registry_thread_safety(self):
        """Test registry thread safety."""
        registry = get_registry()
        registry.clear()

        class ThreadTestTemplate(BaseTemplate):
            def __init__(self, thread_id=0, **config):
                self.thread_id = thread_id
                super().__init__(**config)

            def _get_metadata(self):
                return TemplateMetadata(
                    name=f"thread_test_{self.thread_id}",
                    template_type=TemplateType.CUSTOM
                )

            def _execute_core(self, *args, context, **kwargs):
                return self.thread_id

        def register_template_worker(thread_id):
            template_class = type(f"ThreadTestTemplate{thread_id}",
                                (ThreadTestTemplate,),
                                {"thread_id": thread_id})
            registry.register(template_class, f"thread_test_{thread_id}")

        # Register templates from multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(register_template_worker, i) for i in range(10)]
            [future.result() for future in futures]

        # Should have 10 templates registered
        templates = registry.list_templates()
        thread_templates = [t for t in templates if t.startswith("thread_test_")]
        self.assertEqual(len(thread_templates), 10)


class TestErrorHandlingAndExceptions(unittest.TestCase):
    """Test error handling and exception scenarios."""

    def test_template_registration_errors(self):
        """Test template registration error scenarios."""
        registry = get_registry()
        registry.clear()

        class TestTemplate(BaseTemplate):
            def _get_metadata(self):
                return TemplateMetadata(name="test")

            def _execute_core(self, *args, context, **kwargs):
                return "test"

        # Register template
        registry.register(TestTemplate, "test")

        # Try to register again without override - should raise error
        with self.assertRaises(TemplateRegistrationError):
            registry.register(TestTemplate, "test")

        # Should work with override=True
        registry.register(TestTemplate, "test", override=True)

    def test_template_execution_errors(self):
        """Test template execution error handling."""
        class ErrorTemplate(BaseTemplate):
            def _get_metadata(self):
                return TemplateMetadata(name="error_test")

            def _execute_core(self, *args, context, **kwargs):
                raise RuntimeError("Intentional error")

        template = ErrorTemplate()

        # Execute should return error result, not raise
        result = template.execute(1, 2, 3)
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, RuntimeError)

        # But calling as function should raise
        with self.assertRaises(RuntimeError):
            template(1, 2, 3)

    def test_invalid_template_retrieval(self):
        """Test retrieving non-existent templates."""
        registry = get_registry()

        with self.assertRaises(TemplateRegistrationError):
            registry.get("non_existent_template")


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and real-world use cases."""

    def test_data_pipeline_integration(self):
        """Test complete data processing pipeline."""
        # Create a multi-step data processing pipeline
        step1 = create_transformer(
            filter_func=lambda x: isinstance(x, (int, float)),
            map_func=lambda x: x * 2
        )

        step2 = create_aggregator(aggregation_func=sum)

        step3 = create_data_processor(
            operation=lambda x: f"Total: {x}",
            as_single=True
        )

        pipeline = compose_templates(step1, step2, step3)

        # Process mixed data
        result = pipeline(1, "hello", 2, None, 3.5, "world", 4)

        # Should filter to [1, 2, 3.5, 4], double to [2, 4, 7.0, 8], sum to 21.0
        self.assertEqual(result, "Total: 21.0")

    def test_validation_and_processing_pipeline(self):
        """Test validation followed by processing."""
        # Step 1: Validate data
        validators = [
            lambda x: isinstance(x, (int, float)),
            lambda x: x > 0
        ]
        validator = create_validator(validators=validators)

        # Step 2: Process valid data
        processor = create_data_processor(
            operation=lambda validation_result: validation_result["value"] ** 2
                     if validation_result["valid"] else None,
            postprocess=lambda results: [r for r in results if r is not None]
        )

        # Test pipeline
        validation_results = validator(5, -2, "hello", 3)
        processed_results = processor(*validation_results)

        # Should square valid positive numbers: 5^2=25, 3^2=9
        self.assertEqual(processed_results, [25, 9])

    def test_batch_processing_workflow(self):
        """Test batch processing with workflow."""
        # Define workflow steps for each batch
        steps = [
            {"name": "validate", "func": lambda batch: [x for x in batch if isinstance(x, int)]},
            {"name": "transform", "func": lambda batch: [x * 3 for x in batch]},
            {"name": "aggregate", "func": sum}
        ]

        workflow = create_workflow(steps=steps)

        # Create batch processor that uses the workflow
        batch_processor = create_batch_processor(
            batch_size=3,
            processor_func=workflow
        )

        # Process data in batches
        result = batch_processor(1, "a", 2, 3, "b", 4, 5)

        # Batches: [1,"a",2], [3,"b",4], [5]
        # After workflow: [9], [21], [15] (validate, *3, sum)
        expected_results = [
            {'final_result': 9, 'step_results': {'validate': [1, 2], 'transform': [3, 6], 'aggregate': 9}},
            {'final_result': 21, 'step_results': {'validate': [3, 4], 'transform': [9, 12], 'aggregate': 21}},
            {'final_result': 15, 'step_results': {'validate': [5], 'transform': [15], 'aggregate': 15}}
        ]

        self.assertEqual(len(result), 3)
        for i, expected in enumerate(expected_results):
            self.assertEqual(result[i]['final_result'], expected['final_result'])


if __name__ == '__main__':
    # Setup logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests

    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    if result.wasSuccessful():
        print("\n🎉 All framework tests passed!")
    else:
        print(f"\n❌ Tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
