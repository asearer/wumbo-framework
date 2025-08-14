"""
🌀 Wumbo Framework - Built-in Templates

This module provides a collection of pre-built template types for common use cases.
These templates demonstrate the framework's capabilities and serve as starting points
for custom implementations.
"""

import json
import time
import asyncio
try:
    import requests
except ImportError:
    requests = None
from typing import Any, Dict, List, Optional, Union, Callable, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import logging

from ..core.base import (
    BaseTemplate, TemplateMetadata, TemplateType, ExecutionContext,
    ProcessorFunc, ValidatorFunc, TransformFunc
)


class DataProcessorTemplate(BaseTemplate):
    """
    Template for data processing operations with preprocessing, transformation,
    and postprocessing capabilities.
    """

    def __init__(self,
                 preprocess: Optional[ProcessorFunc] = None,
                 operation: Optional[ProcessorFunc] = None,
                 postprocess: Optional[TransformFunc] = None,
                 fail_silently: bool = True,
                 as_dict: bool = False,
                 as_single: bool = False,
                 **config):
        """
        Initialize DataProcessorTemplate.

        Args:
            preprocess: Function to apply to each input before main operation
            operation: Core function to apply to each preprocessed input
            postprocess: Function to apply to the list of results
            fail_silently: If True, errors are caught and replaced with None
            as_dict: If True, returns results as a dictionary
            as_single: If True and only one result, return it as a single item
            **config: Additional configuration
        """
        self.preprocess_func = preprocess
        self.operation_func = operation
        self.postprocess_func = postprocess
        self.fail_silently = fail_silently
        self.as_dict = as_dict
        self.as_single = as_single
        super().__init__(**config)

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="data_processor",
            description="Flexible data processing template with preprocessing, operation, and postprocessing",
            template_type=TemplateType.DATA_PROCESSOR,
            version="1.0.0",
            tags=["data", "processing", "transformation"]
        )

    def _preprocess(self, *args, context: ExecutionContext, **kwargs):
        if self.preprocess_func:
            context.logger.debug("Applying preprocessing function")
            return tuple(self.preprocess_func(arg) for arg in args)
        return args

    def _execute_core(self, *args, context: ExecutionContext, **kwargs):
        results = []

        for arg in args:
            try:
                if self.operation_func and callable(self.operation_func):
                    result = self.operation_func(arg)
                else:
                    result = arg  # Default passthrough
                results.append(result)
            except Exception as e:
                context.logger.warning(f"Error processing {arg}: {e}")
                if self.fail_silently:
                    results.append(None)
                else:
                    raise

        return results

    def _postprocess(self, result: List[Any], context: ExecutionContext):
        if self.postprocess_func:
            context.logger.debug("Applying postprocessing function")
            result = self.postprocess_func(result)

        # Apply output formatting
        if self.as_dict:
            return {f"item_{i}": val for i, val in enumerate(result)}
        elif self.as_single and len(result) == 1:
            return result[0]

        return result


class APIClientTemplate(BaseTemplate):
    """
    Template for making HTTP API calls with built-in error handling,
    retries, and response processing.
    """

    def __init__(self,
                 base_url: str = "",
                 headers: Optional[Dict[str, str]] = None,
                 timeout: int = 30,
                 retries: int = 3,
                 retry_delay: float = 1.0,
                 **config):
        """
        Initialize APIClientTemplate.

        Args:
            base_url: Base URL for API requests
            headers: Default headers for requests
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            retry_delay: Delay between retries in seconds
            **config: Additional configuration
        """
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        super().__init__(**config)

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="api_client",
            description="HTTP API client template with retries and error handling",
            template_type=TemplateType.API_CLIENT,
            version="1.0.0",
            tags=["api", "http", "client", "web"]
        )

    def _execute_core(self, url: str, method: str = "GET",
                     data: Optional[Dict] = None,
                     params: Optional[Dict] = None,
                     headers: Optional[Dict] = None,
                     context: ExecutionContext = None,
                     **kwargs):

        if requests is None:
            raise ImportError("requests library is required for APIClientTemplate. Install with: pip install requests")

        # Prepare request
        full_url = f"{self.base_url}/{url.lstrip('/')}" if self.base_url else url
        request_headers = {**self.headers, **(headers or {})}

        context.logger.debug(f"Making {method} request to {full_url}")

        for attempt in range(self.retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=full_url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    timeout=self.timeout
                )

                response.raise_for_status()

                # Try to parse JSON response
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return response.text

            except requests.RequestException as e:
                if attempt == self.retries:
                    context.logger.error(f"API request failed after {self.retries + 1} attempts: {e}")
                    raise
                else:
                    context.logger.warning(f"API request attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(self.retry_delay)


class ValidationTemplate(BaseTemplate):
    """
    Template for data validation with customizable validators
    and error collection.
    """

    def __init__(self,
                 validators: List[ValidatorFunc] = None,
                 strict: bool = False,
                 collect_errors: bool = True,
                 **config):
        """
        Initialize ValidationTemplate.

        Args:
            validators: List of validation functions
            strict: If True, raise exception on first validation failure
            collect_errors: If True, collect all validation errors
            **config: Additional configuration
        """
        self.validators = validators or []
        self.strict = strict
        self.collect_errors = collect_errors
        super().__init__(**config)

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="validator",
            description="Data validation template with customizable validators",
            template_type=TemplateType.VALIDATOR,
            version="1.0.0",
            tags=["validation", "data", "quality", "checking"]
        )

    def _execute_core(self, *args, context: ExecutionContext, **kwargs):
        results = []

        for arg in args:
            errors = []
            is_valid = True

            for validator in self.validators:
                try:
                    if not validator(arg):
                        is_valid = False
                        error_msg = f"Validation failed for {arg} with validator {validator.__name__}"
                        errors.append(error_msg)

                        if self.strict:
                            raise ValueError(error_msg)

                except Exception as e:
                    is_valid = False
                    error_msg = f"Validator {validator.__name__} raised exception: {e}"
                    errors.append(error_msg)

                    if self.strict:
                        raise

            result = {
                "value": arg,
                "valid": is_valid,
                "errors": errors if self.collect_errors else []
            }
            results.append(result)

        return results


class AggregatorTemplate(BaseTemplate):
    """
    Template for aggregating data with various aggregation functions.
    """

    def __init__(self,
                 aggregation_func: Optional[Callable] = None,
                 group_by: Optional[Callable] = None,
                 **config):
        """
        Initialize AggregatorTemplate.

        Args:
            aggregation_func: Function to aggregate data (sum, max, min, etc.)
            group_by: Function to group data before aggregation
            **config: Additional configuration
        """
        self.aggregation_func = aggregation_func or sum
        self.group_by = group_by
        super().__init__(**config)

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="aggregator",
            description="Data aggregation template with grouping capabilities",
            template_type=TemplateType.AGGREGATOR,
            version="1.0.0",
            tags=["aggregation", "grouping", "statistics", "data"]
        )

    def _execute_core(self, *args, context: ExecutionContext, **kwargs):
        data = list(args)

        if self.group_by:
            # Group data first
            groups = {}
            for item in data:
                key = self.group_by(item)
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)

            # Aggregate each group
            results = {}
            for key, group in groups.items():
                try:
                    results[key] = self.aggregation_func(group)
                except Exception as e:
                    context.logger.error(f"Aggregation failed for group {key}: {e}")
                    results[key] = None

            return results
        else:
            # Aggregate all data
            try:
                return self.aggregation_func(data)
            except Exception as e:
                context.logger.error(f"Aggregation failed: {e}")
                return None


class BatchProcessorTemplate(BaseTemplate):
    """
    Template for processing data in batches with optional parallel processing.
    """

    def __init__(self,
                 batch_size: int = 10,
                 processor_func: Optional[ProcessorFunc] = None,
                 parallel: bool = False,
                 max_workers: Optional[int] = None,
                 **config):
        """
        Initialize BatchProcessorTemplate.

        Args:
            batch_size: Size of each batch
            processor_func: Function to process each batch
            parallel: Whether to process batches in parallel
            max_workers: Maximum number of worker threads (for parallel processing)
            **config: Additional configuration
        """
        self.batch_size = batch_size
        self.processor_func = processor_func
        self.parallel = parallel
        self.max_workers = max_workers
        super().__init__(**config)

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="batch_processor",
            description="Batch processing template with optional parallel execution",
            template_type=TemplateType.DATA_PROCESSOR,
            version="1.0.0",
            tags=["batch", "parallel", "processing", "performance"]
        )

    def _create_batches(self, data: List[Any]) -> List[List[Any]]:
        """Create batches from input data."""
        batches = []
        for i in range(0, len(data), self.batch_size):
            batches.append(data[i:i + self.batch_size])
        return batches

    def _execute_core(self, *args, context: ExecutionContext, **kwargs):
        data = list(args)
        batches = self._create_batches(data)

        context.logger.debug(f"Processing {len(data)} items in {len(batches)} batches")

        if not self.processor_func:
            return batches  # Return batches without processing

        if self.parallel and len(batches) > 1:
            # Parallel processing
            results = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_batch = {
                    executor.submit(self.processor_func, batch): batch
                    for batch in batches
                }

                for future in as_completed(future_to_batch):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        context.logger.error(f"Batch processing failed: {e}")
                        results.append(None)

            return results
        else:
            # Sequential processing
            results = []
            for i, batch in enumerate(batches):
                try:
                    context.logger.debug(f"Processing batch {i+1}/{len(batches)}")
                    result = self.processor_func(batch)
                    results.append(result)
                except Exception as e:
                    context.logger.error(f"Batch {i+1} processing failed: {e}")
                    results.append(None)

            return results


class TransformTemplate(BaseTemplate):
    """
    Template for data transformation with mapping and filtering capabilities.
    """

    def __init__(self,
                 map_func: Optional[ProcessorFunc] = None,
                 filter_func: Optional[ValidatorFunc] = None,
                 **config):
        """
        Initialize TransformTemplate.

        Args:
            map_func: Function to apply to each item (map operation)
            filter_func: Function to filter items (filter operation)
            **config: Additional configuration
        """
        self.map_func = map_func
        self.filter_func = filter_func
        super().__init__(**config)

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="transformer",
            description="Data transformation template with map and filter operations",
            template_type=TemplateType.TRANSFORMER,
            version="1.0.0",
            tags=["transform", "map", "filter", "functional"]
        )

    def _execute_core(self, *args, context: ExecutionContext, **kwargs):
        data = list(args)

        # Apply filter if provided
        if self.filter_func:
            context.logger.debug(f"Filtering {len(data)} items")
            data = [item for item in data if self.filter_func(item)]
            context.logger.debug(f"After filtering: {len(data)} items")

        # Apply map function if provided
        if self.map_func:
            context.logger.debug(f"Mapping {len(data)} items")
            data = [self.map_func(item) for item in data]

        return data


class WorkflowTemplate(BaseTemplate):
    """
    Template for creating workflows with multiple steps and conditional execution.
    """

    def __init__(self,
                 steps: List[Dict[str, Any]] = None,
                 **config):
        """
        Initialize WorkflowTemplate.

        Args:
            steps: List of workflow steps, each containing 'name', 'func', and optional 'condition'
            **config: Additional configuration
        """
        self.steps = steps or []
        super().__init__(**config)

    def _get_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="workflow",
            description="Workflow template for multi-step processing with conditional execution",
            template_type=TemplateType.WORKFLOW,
            version="1.0.0",
            tags=["workflow", "pipeline", "steps", "conditional"]
        )

    def _execute_core(self, *args, context: ExecutionContext, **kwargs):
        current_data = args
        step_results = {}

        for i, step in enumerate(self.steps):
            step_name = step.get('name', f'step_{i+1}')
            step_func = step.get('func')
            condition = step.get('condition')

            context.logger.debug(f"Executing workflow step: {step_name}")

            # Check condition if provided
            if condition and not condition(current_data, step_results):
                context.logger.debug(f"Skipping step {step_name} due to condition")
                continue

            if not step_func:
                context.logger.warning(f"Step {step_name} has no function defined")
                continue

            try:
                # Execute step
                if isinstance(current_data, tuple):
                    result = step_func(*current_data)
                else:
                    result = step_func(current_data)

                step_results[step_name] = result
                current_data = (result,) if not isinstance(result, tuple) else result

            except Exception as e:
                context.logger.error(f"Step {step_name} failed: {e}")
                raise

        return {
            'final_result': current_data[0] if len(current_data) == 1 else current_data,
            'step_results': step_results
        }


# Convenience factory functions
def create_data_processor(**kwargs) -> DataProcessorTemplate:
    """Create a DataProcessorTemplate instance."""
    return DataProcessorTemplate(**kwargs)


def create_api_client(base_url: str = "", **kwargs) -> APIClientTemplate:
    """Create an APIClientTemplate instance."""
    return APIClientTemplate(base_url=base_url, **kwargs)


def create_validator(validators: List[ValidatorFunc] = None, **kwargs) -> ValidationTemplate:
    """Create a ValidationTemplate instance."""
    return ValidationTemplate(validators=validators, **kwargs)


def create_aggregator(aggregation_func: Optional[Callable] = None, **kwargs) -> AggregatorTemplate:
    """Create an AggregatorTemplate instance."""
    return AggregatorTemplate(aggregation_func=aggregation_func, **kwargs)


def create_batch_processor(batch_size: int = 10, **kwargs) -> BatchProcessorTemplate:
    """Create a BatchProcessorTemplate instance."""
    return BatchProcessorTemplate(batch_size=batch_size, **kwargs)


def create_transformer(**kwargs) -> TransformTemplate:
    """Create a TransformTemplate instance."""
    return TransformTemplate(**kwargs)


def create_workflow(steps: List[Dict[str, Any]] = None, **kwargs) -> WorkflowTemplate:
    """Create a WorkflowTemplate instance."""
    return WorkflowTemplate(steps=steps, **kwargs)
