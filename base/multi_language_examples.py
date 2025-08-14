"""
🌀 Wumbo Framework - Multi-Language Examples

This file demonstrates how to use the multi-language support in the Wumbo framework.
Examples show templates written in different programming languages doing the same tasks.
"""

from wumbo_framework import (
    create_multi_language_template,
    python_template,
    javascript_template,
    typescript_template,
    go_template,
    shell_template,
    get_available_languages,
    get_language_info,
    validate_template_code
)


def basic_examples():
    """Basic examples showing the same operation in different languages."""
    print("=== Basic Multi-Language Examples ===")

    # Python template - multiply numbers by 2
    python_code = """
result = [x * 2 for x in wumbo_args]
wumbo_success(result)
"""

    # JavaScript template - same operation
    javascript_code = """
const result = wumboArgs.map(x => x * 2);
wumbo.success(result);
"""

    # TypeScript template - with type annotations
    typescript_code = """
const result: number[] = wumboArgs.map((x: number) => x * 2);
wumbo.success(result);
"""

    # Go template - statically typed
    go_code = """
import "strconv"

result := make([]int, len(wumboArgs))
for i, arg := range wumboArgs {
    if num, ok := arg.(float64); ok {
        result[i] = int(num) * 2
    }
}
wumbo.Success(result)
"""

    # Shell template - using bash
    shell_code = """
result=""
for arg in "${WUMBO_ARGS[@]}"; do
    doubled=$((arg * 2))
    result="$result $doubled"
done
wumbo_success "$result"
"""

    # Test data
    test_data = [1, 2, 3, 4, 5]

    # Create and execute templates
    templates = {
        'Python': python_template(python_code),
        'JavaScript': javascript_template(javascript_code),
        'TypeScript': typescript_template(typescript_code),
        'Go': go_template(go_code),
        'Shell': shell_template(shell_code)
    }

    available = get_available_languages()

    for name, template in templates.items():
        lang_name = name.lower()
        if lang_name in available:
            try:
                result = template(*test_data)
                print(f"{name:10}: {result}")
            except Exception as e:
                print(f"{name:10}: Error - {e}")
        else:
            print(f"{name:10}: Runtime not available")


def data_processing_examples():
    """Examples showing data processing tasks in different languages."""
    print("\n=== Data Processing Examples ===")

    # Sample data
    data = [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "London"},
        {"name": "Charlie", "age": 35, "city": "Paris"},
        {"name": "Diana", "age": 28, "city": "Tokyo"}
    ]

    # Python - filter and transform
    python_filter_code = """
import json

# Parse input data (first argument should be JSON string)
data = json.loads(wumbo_args[0]) if wumbo_args else []

# Filter people over 28 and get their names
result = [person['name'] for person in data if person['age'] > 28]
wumbo_success(result)
"""

    # JavaScript - same operation
    javascript_filter_code = """
// Parse input data
const data = JSON.parse(wumboArgs[0] || '[]');

// Filter people over 28 and get their names
const result = data.filter(person => person.age > 28).map(person => person.name);
wumbo.success(result);
"""

    # TypeScript - with interfaces
    typescript_filter_code = """
interface Person {
    name: string;
    age: number;
    city: string;
}

// Parse input data
const data: Person[] = JSON.parse(wumboArgs[0] || '[]');

// Filter people over 28 and get their names
const result: string[] = data
    .filter((person: Person) => person.age > 28)
    .map((person: Person) => person.name);

wumbo.success(result);
"""

    available = get_available_languages()
    templates = {}

    if 'python' in available:
        templates['Python'] = python_template(python_filter_code)
    if 'javascript' in available:
        templates['JavaScript'] = javascript_template(javascript_filter_code)
    if 'typescript' in available:
        templates['TypeScript'] = typescript_template(typescript_filter_code)

    import json
    data_json = json.dumps(data)

    for name, template in templates.items():
        try:
            result = template(data_json)
            print(f"{name:10}: {result}")
        except Exception as e:
            print(f"{name:10}: Error - {e}")


def web_api_examples():
    """Examples showing web API calls in different languages."""
    print("\n=== Web API Examples ===")

    # Python - HTTP request
    python_api_code = """
import urllib.request
import json

try:
    url = wumbo_kwargs.get('url', 'https://httpbin.org/json')
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

    # Extract just the slideshow title
    result = data.get('slideshow', {}).get('title', 'No title found')
    wumbo_success(result)
except Exception as e:
    wumbo_error(f"HTTP request failed: {e}")
"""

    # JavaScript - using built-in fetch utility
    javascript_api_code = """
async function fetchData() {
    try {
        const url = wumbo.kwargs.url || 'https://httpbin.org/json';
        const response = await wumboFetch(url);
        const data = await response.json();

        // Extract just the slideshow title
        const result = data.slideshow?.title || 'No title found';
        wumbo.success(result);
    } catch (error) {
        wumbo.error(`HTTP request failed: ${error.message}`);
    }
}

// Note: This is wrapped in the async execution context
fetchData();
"""

    # Shell - using curl
    shell_api_code = """
url="${WUMBO_KWARGS_url:-https://httpbin.org/json}"

if command -v curl >/dev/null 2>&1; then
    response=$(curl -s "$url" || echo "")
    if [ -n "$response" ] && command -v jq >/dev/null 2>&1; then
        title=$(echo "$response" | jq -r '.slideshow.title // "No title found"')
        wumbo_success "$title"
    else
        wumbo_success "curl available but jq not found for JSON parsing"
    fi
else
    wumbo_error "curl not available for HTTP requests"
fi
"""

    available = get_available_languages()
    templates = {}

    if 'python' in available:
        templates['Python'] = python_template(python_api_code)
    if 'javascript' in available:
        templates['JavaScript'] = javascript_template(javascript_api_code)
    if 'shell' in available:
        templates['Shell'] = shell_template(shell_api_code)

    print("Making HTTP requests to httpbin.org...")

    for name, template in templates.items():
        try:
            # Set a timeout for API calls
            result = template(url='https://httpbin.org/json')
            print(f"{name:10}: {result}")
        except Exception as e:
            print(f"{name:10}: Error - {e}")


def file_processing_examples():
    """Examples showing file processing in different languages."""
    print("\n=== File Processing Examples ===")

    # Create a temporary file with sample data
    import tempfile
    import os

    sample_data = """line1,value1,10
line2,value2,20
line3,value3,30
line4,value4,40
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write(sample_data)
        temp_file = f.name

    try:
        # Python - read and process CSV
        python_csv_code = f"""
import csv

filename = "{temp_file}"
total = 0
count = 0

try:
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3:
                total += int(row[2])
                count += 1

    result = {{"total": total, "count": count, "average": total / count if count > 0 else 0}}
    wumbo_success(result)
except Exception as e:
    wumbo_error(f"File processing failed: {{e}}")
"""

        # Shell - same operation
        shell_csv_code = f"""
filename="{temp_file}"
total=0
count=0

if [ -f "$filename" ]; then
    while IFS=',' read -r col1 col2 col3; do
        if [ -n "$col3" ] && [ "$col3" -eq "$col3" ] 2>/dev/null; then
            total=$((total + col3))
            count=$((count + 1))
        fi
    done < "$filename"

    if [ "$count" -gt 0 ]; then
        average=$((total / count))
        result="{{\\\"total\\\": $total, \\\"count\\\": $count, \\\"average\\\": $average}}"
        wumbo_success "$result"
    else
        wumbo_error "No valid data found"
    fi
else
    wumbo_error "File not found: $filename"
fi
"""

        available = get_available_languages()
        templates = {}

        if 'python' in available:
            templates['Python'] = python_template(python_csv_code)
        if 'shell' in available:
            templates['Shell'] = shell_template(shell_csv_code)

        print(f"Processing CSV file: {temp_file}")

        for name, template in templates.items():
            try:
                result = template()
                print(f"{name:10}: {result}")
            except Exception as e:
                print(f"{name:10}: Error - {e}")

    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def validation_examples():
    """Examples showing code validation across languages."""
    print("\n=== Code Validation Examples ===")

    test_codes = {
        'python': [
            ('print("hello")', True),
            ('print("hello"', False),  # Missing closing parenthesis
            ('def func(): return 42', True),
            ('def func( return 42', False)  # Missing colon
        ],
        'javascript': [
            ('console.log("hello");', True),
            ('console.log("hello"', False),  # Missing closing parenthesis
            ('function test() { return 42; }', True),
            ('function test() return 42; }', False)  # Missing opening brace
        ],
        'shell': [
            ('echo "hello"', True),
            ('echo "hello', False),  # Missing closing quote
            ('for i in {1..5}; do echo $i; done', True),
            ('for i in {1..5} do echo $i; done', False)  # Missing semicolon
        ]
    }

    available = get_available_languages()

    for language in test_codes:
        if language in available:
            print(f"\n{language.upper()} validation:")
            for code, expected in test_codes[language]:
                try:
                    valid = validate_template_code(language, code)
                    status = "✓" if valid == expected else "✗"
                    print(f"  {status} {code[:30]}... -> Valid: {valid}")
                except Exception as e:
                    print(f"  ✗ {code[:30]}... -> Error: {e}")
        else:
            print(f"\n{language.upper()}: Runtime not available")


def language_info_demo():
    """Demonstrate language information queries."""
    print("\n=== Language Information ===")

    available = get_available_languages()
    print(f"Available languages: {', '.join(available) if available else 'None'}")

    from wumbo_framework import SupportedLanguage

    for language in SupportedLanguage:
        lang_name = language.value
        try:
            info = get_language_info(lang_name)
            status = "Available" if info['available'] else "Not available"
            features = len(info['features'])

            print(f"\n{lang_name.upper():12}: {status}")
            if info['available']:
                print(f"             Features: {features} supported")
                if info['runtime_info']:
                    for key, value in info['runtime_info'].items():
                        print(f"             {key}: {value}")
        except Exception as e:
            print(f"{lang_name.upper():12}: Error - {e}")


def performance_comparison():
    """Compare performance across languages for the same task."""
    print("\n=== Performance Comparison ===")

    # Simple computation task - sum of squares
    task_description = "Calculate sum of squares from 1 to 1000"

    python_code = """
result = sum(i*i for i in range(1, 1001))
wumbo_success(result)
"""

    javascript_code = """
let result = 0;
for (let i = 1; i <= 1000; i++) {
    result += i * i;
}
wumbo.success(result);
"""

    go_code = """
result := 0
for i := 1; i <= 1000; i++ {
    result += i * i
}
wumbo.Success(result)
"""

    shell_code = """
result=0
for i in {1..1000}; do
    result=$((result + i * i))
done
wumbo_success "$result"
"""

    templates = {
        'python': python_template(python_code),
        'javascript': javascript_template(javascript_code),
        'go': go_template(go_code),
        'shell': shell_template(shell_code)
    }

    available = get_available_languages()
    print(f"Task: {task_description}")
    print("Expected result: 333833500\n")

    import time

    for name, template in templates.items():
        if name in available:
            try:
                start_time = time.time()
                result = template()
                end_time = time.time()

                execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                print(f"{name:10}: Result={result}, Time={execution_time:.2f}ms")
            except Exception as e:
                print(f"{name:10}: Error - {e}")
        else:
            print(f"{name:10}: Runtime not available")


def main():
    """Run all multi-language examples."""
    print("🌀 Wumbo Framework - Multi-Language Examples")
    print("=" * 50)

    # Show framework info
    from wumbo_framework import get_framework_info
    info = get_framework_info()
    if 'multi_language' in info:
        ml_info = info['multi_language']
        if 'error' not in ml_info:
            print(f"Multi-language support: {ml_info['registered_interfaces']} interfaces registered")
            print(f"Available runtimes: {len(ml_info['available_languages'])}")

    # Run all examples
    try:
        language_info_demo()
        basic_examples()
        data_processing_examples()
        validation_examples()
        performance_comparison()
        file_processing_examples()
        # web_api_examples()  # Commented out to avoid external dependencies in examples
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
