"""
🌀 Wumbo Framework - Multi-Language Support Tests

Comprehensive test suite for the multi-language template system.
Tests all language interfaces, validation, execution, and error handling.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the framework
try:
    from wumbo_framework import (
        create_multi_language_template,
        python_template,
        javascript_template,
        typescript_template,
        go_template,
        shell_template,
        get_available_languages,
        get_language_info,
        get_multi_language_info,
        validate_template_code,
        SupportedLanguage,
        MultiLanguageTemplate
    )
    from wumbo_framework.languages import (
        LanguageInterface,
        LanguageInterfaceRegistry,
        LanguageRuntime,
        SerializationConfig,
        ExecutionEnvironment,
        create_default_runtime
    )
    from wumbo_framework.languages.core import (
        ProcessExecutionMixin,
        DataSerializer,
        SecuritySandbox
    )
except ImportError as e:
    print(f"Failed to import Wumbo framework: {e}")
    print("Make sure the framework is properly installed and PYTHONPATH is set")
    raise


class TestLanguageInterfaceRegistry(unittest.TestCase):
    """Test the language interface registry system."""

    def test_supported_languages_enum(self):
        """Test that all expected languages are in the enum."""
        expected_languages = {
            'python', 'javascript', 'typescript', 'java', 'csharp',
            'go', 'rust', 'cpp', 'c', 'php', 'ruby', 'kotlin',
            'scala', 'r', 'julia', 'lua', 'perl', 'shell', 'powershell'
        }

        actual_languages = {lang.value for lang in SupportedLanguage}

        for lang in expected_languages:
            self.assertIn(lang, actual_languages, f"Language {lang} not found in SupportedLanguage enum")

    def test_registry_interface_registration(self):
        """Test that language interfaces can be registered and retrieved."""
        # Check that at least Python is registered
        registered_languages = LanguageInterfaceRegistry.list_supported_languages()
        self.assertIn(SupportedLanguage.PYTHON, registered_languages)

    def test_registry_get_interface(self):
        """Test getting interfaces from the registry."""
        runtime = create_default_runtime(SupportedLanguage.PYTHON)
        serialization = SerializationConfig()

        interface = LanguageInterfaceRegistry.get_interface(
            SupportedLanguage.PYTHON, runtime, serialization
        )

        self.assertIsInstance(interface, LanguageInterface)


class TestLanguageRuntime(unittest.TestCase):
    """Test language runtime configuration."""

    def test_language_runtime_creation(self):
        """Test creating language runtime configurations."""
        runtime = LanguageRuntime(
            language=SupportedLanguage.PYTHON,
            interpreter_path='python3',
            version='3.9',
            additional_args=['-u'],
            environment_vars={'PYTHONPATH': '.'},
            timeout=300,
            max_memory_mb=1024
        )

        self.assertEqual(runtime.language, SupportedLanguage.PYTHON)
        self.assertEqual(runtime.interpreter_path, 'python3')
        self.assertEqual(runtime.version, '3.9')
        self.assertEqual(runtime.additional_args, ['-u'])
        self.assertEqual(runtime.environment_vars, {'PYTHONPATH': '.'})
        self.assertEqual(runtime.timeout, 300)
        self.assertEqual(runtime.max_memory_mb, 1024)

    def test_create_default_runtime(self):
        """Test creating default runtime configurations."""
        for language in [SupportedLanguage.PYTHON, SupportedLanguage.JAVASCRIPT,
                        SupportedLanguage.GO, SupportedLanguage.SHELL]:
            runtime = create_default_runtime(language)
            self.assertEqual(runtime.language, language)
            self.assertIsInstance(runtime.interpreter_path, str)
            self.assertIsInstance(runtime.additional_args, list)
            self.assertIsInstance(runtime.environment_vars, dict)


class TestDataSerializer(unittest.TestCase):
    """Test data serialization functionality."""

    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        config = SerializationConfig(format='json')
        serializer = DataSerializer(config)

        test_data = {'key': 'value', 'number': 42, 'list': [1, 2, 3]}

        # Test serialization
        serialized = serializer.serialize(test_data)
        self.assertIsInstance(serialized, str)

        # Test deserialization
        deserialized = serializer.deserialize(serialized)
        self.assertEqual(deserialized, test_data)

    def test_serialization_with_custom_types(self):
        """Test serialization with custom types."""
        config = SerializationConfig(format='json')
        serializer = DataSerializer(config)

        from datetime import datetime
        test_data = {
            'date': datetime(2023, 1, 1),
            'path': Path('/tmp/test'),
            'normal': 'string'
        }

        # Should handle custom types gracefully
        serialized = serializer.serialize(test_data)
        self.assertIsInstance(serialized, str)


class TestPythonInterface(unittest.TestCase):
    """Test Python language interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.runtime = create_default_runtime(SupportedLanguage.PYTHON)
        self.serialization = SerializationConfig()

    def test_python_code_validation(self):
        """Test Python code validation."""
        interface = LanguageInterfaceRegistry.get_interface(
            SupportedLanguage.PYTHON, self.runtime, self.serialization
        )

        # Valid code
        self.assertTrue(interface.validate_code('print("hello")'))
        self.assertTrue(interface.validate_code('def func(): return 42'))

        # Invalid code
        self.assertFalse(interface.validate_code('print("hello"'))  # Missing closing parenthesis
        self.assertFalse(interface.validate_code('def func( return 42'))  # Syntax error

    def test_python_template_execution(self):
        """Test executing Python templates."""
        if 'python' not in get_available_languages():
            self.skipTest("Python runtime not available")

        template = python_template('''
result = sum(x * 2 for x in wumbo_args)
wumbo_success(result)
''')

        result = template(1, 2, 3, 4, 5)
        expected = sum(x * 2 for x in [1, 2, 3, 4, 5])  # 30
        self.assertEqual(result, expected)

    def test_python_template_with_kwargs(self):
        """Test Python templates with keyword arguments."""
        if 'python' not in get_available_languages():
            self.skipTest("Python runtime not available")

        template = python_template('''
multiplier = wumbo_kwargs.get('multiplier', 1)
result = [x * multiplier for x in wumbo_args]
wumbo_success(result)
''')

        result = template(1, 2, 3, multiplier=3)
        self.assertEqual(result, [3, 6, 9])

    def test_python_error_handling(self):
        """Test Python template error handling."""
        if 'python' not in get_available_languages():
            self.skipTest("Python runtime not available")

        template = python_template('''
# This will raise an error
result = 1 / 0
wumbo_success(result)
''')

        with self.assertRaises(Exception):
            template()


class TestJavaScriptInterface(unittest.TestCase):
    """Test JavaScript language interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.runtime = create_default_runtime(SupportedLanguage.JAVASCRIPT)
        self.serialization = SerializationConfig()

    def test_javascript_availability(self):
        """Test if JavaScript runtime is available."""
        available_languages = get_available_languages()
        if 'javascript' not in available_languages:
            self.skipTest("JavaScript runtime (Node.js) not available")

    def test_javascript_code_validation(self):
        """Test JavaScript code validation."""
        if 'javascript' not in get_available_languages():
            self.skipTest("JavaScript runtime not available")

        # Valid code
        self.assertTrue(validate_template_code('javascript', 'console.log("hello");'))
        self.assertTrue(validate_template_code('javascript', 'function test() { return 42; }'))

        # Invalid code
        self.assertFalse(validate_template_code('javascript', 'console.log("hello"'))  # Missing closing

    def test_javascript_template_execution(self):
        """Test executing JavaScript templates."""
        if 'javascript' not in get_available_languages():
            self.skipTest("JavaScript runtime not available")

        template = javascript_template('''
const result = wumboArgs.reduce((sum, x) => sum + x * 2, 0);
wumbo.success(result);
''')

        result = template(1, 2, 3, 4, 5)
        expected = sum(x * 2 for x in [1, 2, 3, 4, 5])  # 30
        self.assertEqual(result, expected)


class TestTypeScriptInterface(unittest.TestCase):
    """Test TypeScript language interface."""

    def test_typescript_availability(self):
        """Test if TypeScript runtime is available."""
        available_languages = get_available_languages()
        if 'typescript' not in available_languages:
            self.skipTest("TypeScript runtime not available")

    def test_typescript_template_execution(self):
        """Test executing TypeScript templates."""
        if 'typescript' not in get_available_languages():
            self.skipTest("TypeScript runtime not available")

        template = typescript_template('''
const result: number = wumboArgs.reduce((sum: number, x: number) => sum + x * 2, 0);
wumbo.success(result);
''')

        result = template(1, 2, 3, 4, 5)
        expected = sum(x * 2 for x in [1, 2, 3, 4, 5])  # 30
        self.assertEqual(result, expected)


class TestGoInterface(unittest.TestCase):
    """Test Go language interface."""

    def test_go_availability(self):
        """Test if Go runtime is available."""
        available_languages = get_available_languages()
        if 'go' not in available_languages:
            self.skipTest("Go runtime not available")

    def test_go_template_execution(self):
        """Test executing Go templates."""
        if 'go' not in get_available_languages():
            self.skipTest("Go runtime not available")

        template = go_template('''
sum := 0
for _, arg := range wumboArgs {
    if num, ok := arg.(float64); ok {
        sum += int(num) * 2
    }
}
wumbo.Success(sum)
''')

        result = template(1, 2, 3, 4, 5)
        expected = sum(x * 2 for x in [1, 2, 3, 4, 5])  # 30
        self.assertEqual(result, expected)


class TestShellInterface(unittest.TestCase):
    """Test Shell scripting interface."""

    def test_shell_availability(self):
        """Test if shell runtime is available."""
        available_languages = get_available_languages()
        if 'shell' not in available_languages:
            self.skipTest("Shell runtime not available")

    def test_shell_code_validation(self):
        """Test shell code validation."""
        if 'shell' not in get_available_languages():
            self.skipTest("Shell runtime not available")

        # Valid code
        self.assertTrue(validate_template_code('shell', 'echo "hello"'))
        self.assertTrue(validate_template_code('shell', 'for i in {1..5}; do echo $i; done'))

    def test_shell_template_execution(self):
        """Test executing shell script templates."""
        if 'shell' not in get_available_languages():
            self.skipTest("Shell runtime not available")

        template = shell_template('''
sum=0
for arg in "${WUMBO_ARGS[@]}"; do
    doubled=$((arg * 2))
    sum=$((sum + doubled))
done
wumbo_success "$sum"
''')

        result = template(1, 2, 3, 4, 5)
        # Shell returns string, so convert for comparison
        expected = str(sum(x * 2 for x in [1, 2, 3, 4, 5]))  # "30"
        self.assertEqual(str(result), expected)


class TestMultiLanguageTemplate(unittest.TestCase):
    """Test the MultiLanguageTemplate class."""

    def test_create_multi_language_template(self):
        """Test creating multi-language templates."""
        template = create_multi_language_template(
            'python',
            'wumbo_success("Hello from Python")'
        )

        self.assertIsInstance(template, MultiLanguageTemplate)
        self.assertEqual(template.language, SupportedLanguage.PYTHON)

    def test_invalid_language(self):
        """Test creating template with invalid language."""
        with self.assertRaises(ValueError):
            create_multi_language_template('invalid_language', 'some code')

    def test_template_metadata(self):
        """Test template metadata functionality."""
        template = create_multi_language_template(
            'python',
            'wumbo_success("test")',
            name='test_template',
            description='A test template',
            metadata={'author': 'test', 'version': '1.0'}
        )

        self.assertEqual(template.name, 'test_template')
        self.assertEqual(template.description, 'A test template')
        self.assertEqual(template.metadata['author'], 'test')


class TestLanguageInfoFunctions(unittest.TestCase):
    """Test language information and utility functions."""

    def test_get_available_languages(self):
        """Test getting available languages."""
        available = get_available_languages()
        self.assertIsInstance(available, list)

        # Python should always be available
        self.assertIn('python', available)

    def test_get_language_info(self):
        """Test getting language information."""
        info = get_language_info('python')

        self.assertIsInstance(info, dict)
        self.assertIn('language', info)
        self.assertIn('available', info)
        self.assertIn('features', info)
        self.assertEqual(info['language'], 'python')
        self.assertTrue(info['available'])  # Python should be available
        self.assertIsInstance(info['features'], list)

    def test_get_language_info_invalid(self):
        """Test getting info for invalid language."""
        with self.assertRaises(ValueError):
            get_language_info('invalid_language')

    def test_get_multi_language_info(self):
        """Test getting comprehensive multi-language information."""
        info = get_multi_language_info()

        self.assertIsInstance(info, dict)
        self.assertIn('version', info)
        self.assertIn('total_languages', info)
        self.assertIn('available_languages', info)
        self.assertIn('supported_languages', info)
        self.assertIn('language_details', info)

    def test_validate_template_code_function(self):
        """Test the standalone validate_template_code function."""
        # Valid Python code
        self.assertTrue(validate_template_code('python', 'print("hello")'))

        # Invalid Python code
        self.assertFalse(validate_template_code('python', 'print("hello"'))

        # Invalid language
        self.assertFalse(validate_template_code('invalid_language', 'any code'))


class TestSecurityFeatures(unittest.TestCase):
    """Test security features of the multi-language system."""

    def test_security_sandbox_context(self):
        """Test security sandbox context manager."""
        with SecuritySandbox() as sandbox:
            self.assertIsNotNone(sandbox)
            # Sandbox should be active here

    def test_execution_timeout(self):
        """Test execution timeout handling."""
        if 'python' not in get_available_languages():
            self.skipTest("Python runtime not available")

        # Create template with short timeout
        template = create_multi_language_template(
            'python',
            '''
import time
time.sleep(10)  # This should timeout
wumbo_success("Should not reach here")
''',
            timeout=1  # 1 second timeout
        )

        with self.assertRaises(Exception):
            template()

    def test_resource_limits(self):
        """Test resource limit configuration."""
        runtime = LanguageRuntime(
            language=SupportedLanguage.PYTHON,
            interpreter_path='python3',
            version='latest',
            additional_args=[],
            environment_vars={},
            timeout=300,
            max_memory_mb=256  # 256MB limit
        )

        self.assertEqual(runtime.max_memory_mb, 256)


class TestProcessExecutionMixin(unittest.TestCase):
    """Test process execution utilities."""

    def test_process_execution_mixin(self):
        """Test the process execution mixin functionality."""
        class TestInterface(ProcessExecutionMixin):
            pass

        interface = TestInterface()

        # Test simple command execution
        result = interface.execute_process(['echo', 'hello'], timeout=10)

        self.assertIsInstance(result, dict)
        self.assertIn('returncode', result)
        self.assertIn('stdout', result)
        self.assertIn('stderr', result)
        self.assertEqual(result['returncode'], 0)
        self.assertIn('hello', result['stdout'])


class TestErrorHandling(unittest.TestCase):
    """Test error handling across the multi-language system."""

    def test_syntax_error_handling(self):
        """Test handling of syntax errors in template code."""
        if 'python' not in get_available_languages():
            self.skipTest("Python runtime not available")

        template = python_template('print("hello"')  # Missing closing parenthesis

        with self.assertRaises(Exception):
            template()

    def test_runtime_error_handling(self):
        """Test handling of runtime errors in templates."""
        if 'python' not in get_available_languages():
            self.skipTest("Python runtime not available")

        template = python_template('''
# This will cause a runtime error
undefined_variable + 1
''')

        with self.assertRaises(Exception):
            template()

    def test_missing_runtime_error(self):
        """Test handling when language runtime is missing."""
        # Mock the runtime detection to simulate missing runtime
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError("Command not found")

            with self.assertRaises(Exception):
                create_multi_language_template('go', 'some code')()


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and real-world use cases."""

    def test_cross_language_data_consistency(self):
        """Test that the same data produces consistent results across languages."""
        test_data = [1, 2, 3, 4, 5]
        expected_result = [2, 4, 6, 8, 10]  # Each number doubled

        # Python implementation
        python_code = '''
result = [x * 2 for x in wumbo_args]
wumbo_success(result)
'''

        # JavaScript implementation
        javascript_code = '''
const result = wumboArgs.map(x => x * 2);
wumbo.success(result);
'''

        available = get_available_languages()

        if 'python' in available:
            python_result = python_template(python_code)(*test_data)
            self.assertEqual(python_result, expected_result)

        if 'javascript' in available:
            js_result = javascript_template(javascript_code)(*test_data)
            self.assertEqual(js_result, expected_result)

            # Cross-language consistency check
            if 'python' in available:
                self.assertEqual(python_result, js_result)

    def test_file_processing_across_languages(self):
        """Test file processing capabilities across different languages."""
        # Create a temporary file
        test_content = "line1\nline2\nline3\n"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_content)
            temp_file = f.name

        try:
            # Python file processing
            python_code = f'''
with open("{temp_file}", "r") as f:
    lines = f.readlines()
result = len(lines)
wumbo_success(result)
'''

            # Shell file processing
            shell_code = f'''
line_count=$(wc -l < "{temp_file}")
wumbo_success "$line_count"
'''

            available = get_available_languages()

            if 'python' in available:
                python_result = python_template(python_code)()
                self.assertEqual(python_result, 3)

            if 'shell' in available:
                shell_result = shell_template(shell_code)()
                # Shell wc includes trailing newlines, so result might be string
                self.assertIn(str(shell_result).strip(), ['3', '4'])

        finally:
            os.unlink(temp_file)

    def test_template_composition(self):
        """Test composing templates from different languages."""
        # This tests the framework's ability to handle multiple templates
        available = get_available_languages()

        if len(available) < 2:
            self.skipTest("Need at least 2 language runtimes for composition test")

        # Create templates in different languages that process data sequentially
        templates = []

        if 'python' in available:
            templates.append(python_template('''
# Double the numbers
result = [x * 2 for x in wumbo_args]
wumbo_success(result)
'''))

        if 'javascript' in available and 'python' not in available:
            templates.append(javascript_template('''
// Double the numbers
const result = wumboArgs.map(x => x * 2);
wumbo.success(result);
'''))

        # Test that templates can be executed independently
        for template in templates:
            result = template(1, 2, 3)
            self.assertEqual(result, [2, 4, 6])


def run_performance_tests():
    """Run performance comparison tests."""
    print("\n=== Performance Tests ===")

    import time

    # Simple computation test
    test_code = {
        'python': '''
result = sum(i*i for i in range(1, 1001))
wumbo_success(result)
''',
        'javascript': '''
let result = 0;
for (let i = 1; i <= 1000; i++) {
    result += i * i;
}
wumbo.success(result);
''',
        'shell': '''
result=0
for i in {1..1000}; do
    result=$((result + i * i))
done
wumbo_success "$result"
'''
    }

    available = get_available_languages()
    expected_result = 333833500

    print(f"Computing sum of squares from 1 to 1000 (expected: {expected_result})")

    for lang in test_code:
        if lang in available:
            try:
                if lang == 'python':
                    template = python_template(test_code[lang])
                elif lang == 'javascript':
                    template = javascript_template(test_code[lang])
                elif lang == 'shell':
                    template = shell_template(test_code[lang])
                else:
                    continue

                start_time = time.time()
                result = template()
                end_time = time.time()

                execution_time = (end_time - start_time) * 1000

                # Normalize result for comparison
                result_int = int(str(result).strip())

                print(f"{lang:10}: {result_int} ({execution_time:.2f}ms) {'✓' if result_int == expected_result else '✗'}")

            except Exception as e:
                print(f"{lang:10}: Error - {e}")
        else:
            print(f"{lang:10}: Runtime not available")


def main():
    """Main test runner with additional diagnostics."""
    print("🌀 Wumbo Framework - Multi-Language Support Tests")
    print("=" * 60)

    # Show system info
    print("System Information:")
    print(f"Available languages: {', '.join(get_available_languages())}")

    try:
        ml_info = get_multi_language_info()
        print(f"Registered interfaces: {ml_info['registered_interfaces']}")
        print(f"Total supported languages: {ml_info['total_languages']}")
    except Exception as e:
        print(f"Could not get multi-language info: {e}")

    print("\nRunning tests...")

    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))

    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    # Run performance tests if requested
    if os.environ.get('WUMBO_PERF_TESTS'):
        run_performance_tests()

    # Summary
    print(f"\n{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    return len(result.failures) + len(result.errors) == 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
