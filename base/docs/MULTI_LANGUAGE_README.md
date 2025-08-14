# 🌀 Wumbo Framework - Multi-Language Support

The Wumbo Framework provides comprehensive multi-language template support, enabling you to write templates in various programming languages while maintaining a unified interface and execution model.

## Table of Contents

- [Overview](#overview)
- [Supported Languages](#supported-languages)
- [Quick Start](#quick-start)
- [Language-Specific Examples](#language-specific-examples)
- [Advanced Features](#advanced-features)
- [Configuration](#configuration)
- [Security](#security)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

## Overview

The multi-language system allows you to:

- ✅ **Write templates in multiple programming languages**
- ✅ **Execute them with a unified interface**
- ✅ **Share data seamlessly between languages**
- ✅ **Apply security sandboxing consistently**
- ✅ **Manage runtime environments automatically**
- ✅ **Validate code before execution**

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Wumbo Framework                              │
├─────────────────────────────────────────────────────────────────┤
│  Multi-Language Template Interface                             │
├─────────────────────────────────────────────────────────────────┤
│  Language Interface Registry                                   │
├─────┬─────────┬─────────┬─────────┬─────────┬─────────────────────┤
│Python│JavaScript│TypeScript│   Go    │  Shell  │  ... (Extensible) │
├─────┼─────────┼─────────┼─────────┼─────────┼─────────────────────┤
│Python│ Node.js │   tsc   │   go    │  bash   │                   │
│ CPython │     │ts-node  │compiler │   zsh   │                   │
└─────┴─────────┴─────────┴─────────┴─────────┴─────────────────────┘
```

## Supported Languages

| Language   | Status | Runtime Required | Features |
|------------|--------|------------------|----------|
| **Python** | ✅ Full | Python 3.7+ | Native integration, security sandbox, import restrictions |
| **JavaScript** | ✅ Full | Node.js 14+ | ES6+, npm packages, async/await |
| **TypeScript** | ✅ Full | Node.js + TypeScript | Static typing, generics, interfaces |
| **Go** | ✅ Full | Go 1.16+ | Static typing, goroutines, modules |
| **Shell** | ✅ Full | Bash/Zsh | Scripting, file operations, process control |

### Coming Soon
- Java (OpenJDK/Oracle JDK)
- Rust (rustc)
- C++ (GCC/Clang)
- PHP (PHP 8+)
- Ruby (Ruby 3+)

## Quick Start

### Installation Requirements

Make sure you have the required runtimes installed:

```bash
# Check available languages
python -c "from wumbo_framework import get_available_languages; print(get_available_languages())"

# Install additional runtimes as needed
# Node.js (for JavaScript/TypeScript)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# TypeScript
npm install -g typescript ts-node

# Go
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

### Basic Usage

```python
from wumbo_framework import (
    python_template,
    javascript_template,
    typescript_template,
    go_template,
    shell_template,
    create_multi_language_template
)

# Method 1: Language-specific factory functions
py_template = python_template('''
result = [x * 2 for x in wumbo_args]
wumbo_success(result)
''')

js_template = javascript_template('''
const result = wumboArgs.map(x => x * 2);
wumbo.success(result);
''')

# Method 2: Generic factory function
template = create_multi_language_template('go', '''
result := make([]int, len(wumboArgs))
for i, arg := range wumboArgs {
    if num, ok := arg.(float64); ok {
        result[i] = int(num) * 2
    }
}
wumbo.Success(result)
''')

# All templates work the same way
print(py_template(1, 2, 3, 4, 5))  # [2, 4, 6, 8, 10]
print(js_template(1, 2, 3, 4, 5))  # [2, 4, 6, 8, 10]
print(template(1, 2, 3, 4, 5))     # [2, 4, 6, 8, 10]
```

## Language-Specific Examples

### Python Templates

Python templates have full access to the Python ecosystem with security restrictions:

```python
python_template('''
import json
import math

# Process input data
data = {
    'numbers': list(wumbo_args),
    'sum': sum(wumbo_args),
    'mean': sum(wumbo_args) / len(wumbo_args) if wumbo_args else 0,
    'sqrt_sum': math.sqrt(sum(wumbo_args))
}

# Use kwargs
if 'format' in wumbo_kwargs and wumbo_kwargs['format'] == 'json':
    wumbo_success(json.dumps(data))
else:
    wumbo_success(data)
''')

# Usage
result = template(1, 4, 9, 16, format='json')
```

### JavaScript Templates

JavaScript templates run in Node.js with built-in utilities:

```python
javascript_template('''
// Async operations supported
async function processData() {
    const numbers = wumboArgs;
    const sum = numbers.reduce((a, b) => a + b, 0);
    
    // Built-in utilities available
    const doubled = wumboMap(numbers, x => x * 2);
    const filtered = wumboFilter(numbers, x => x > 5);
    
    // HTTP requests (if network access enabled)
    try {
        const response = await wumboFetch('https://api.example.com/data');
        const data = await response.json();
        wumbo.success({sum, doubled, filtered, external: data});
    } catch (error) {
        wumbo.success({sum, doubled, filtered});
    }
}

processData();
''')
```

### TypeScript Templates

TypeScript templates provide static typing and modern language features:

```python
typescript_template('''
interface DataPoint {
    value: number;
    processed: boolean;
}

interface Result {
    total: number;
    processed: DataPoint[];
    metadata: {
        count: number;
        average: number;
    };
}

function processNumbers(numbers: number[]): Result {
    const processed: DataPoint[] = numbers.map(value => ({
        value: value * 2,
        processed: true
    }));
    
    const total = processed.reduce((sum, item) => sum + item.value, 0);
    const average = numbers.length > 0 ? total / numbers.length : 0;
    
    return {
        total,
        processed,
        metadata: {
            count: numbers.length,
            average
        }
    };
}

const result: Result = processNumbers(wumboArgs);
wumbo.success(result);
''')
```

### Go Templates

Go templates provide high-performance execution with static typing:

```python
go_template('''
import (
    "sort"
    "math"
)

type Stats struct {
    Numbers []float64 `json:"numbers"`
    Sum     float64   `json:"sum"`
    Mean    float64   `json:"mean"`
    Median  float64   `json:"median"`
    StdDev  float64   `json:"stddev"`
}

func calculateStats(numbers []interface{}) Stats {
    var nums []float64
    for _, n := range numbers {
        if num, ok := n.(float64); ok {
            nums = append(nums, num)
        }
    }
    
    if len(nums) == 0 {
        return Stats{}
    }
    
    // Calculate sum
    sum := 0.0
    for _, n := range nums {
        sum += n
    }
    
    // Calculate mean
    mean := sum / float64(len(nums))
    
    // Calculate median
    sorted := make([]float64, len(nums))
    copy(sorted, nums)
    sort.Float64s(sorted)
    
    var median float64
    mid := len(sorted) / 2
    if len(sorted)%2 == 0 {
        median = (sorted[mid-1] + sorted[mid]) / 2
    } else {
        median = sorted[mid]
    }
    
    // Calculate standard deviation
    variance := 0.0
    for _, n := range nums {
        variance += math.Pow(n-mean, 2)
    }
    stddev := math.Sqrt(variance / float64(len(nums)))
    
    return Stats{
        Numbers: nums,
        Sum:     sum,
        Mean:    mean,
        Median:  median,
        StdDev:  stddev,
    }
}

stats := calculateStats(wumboArgs)
wumbo.Success(stats)
''')
```

### Shell Templates

Shell templates provide system integration and process control:

```python
shell_template('''
#!/bin/bash

# Process files in directory
directory="${WUMBO_KWARGS_directory:-.}"
pattern="${WUMBO_KWARGS_pattern:-*.txt}"

if [ ! -d "$directory" ]; then
    wumbo_error "Directory not found: $directory"
fi

# Count files matching pattern
file_count=0
total_size=0

for file in "$directory"/$pattern; do
    if [ -f "$file" ]; then
        file_count=$((file_count + 1))
        if command -v stat >/dev/null 2>&1; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
            total_size=$((total_size + size))
        fi
    fi
done

# Create result
result="{\\"file_count\\": $file_count, \\"total_size\\": $total_size, \\"directory\\": \\"$directory\\", \\"pattern\\": \\"$pattern\\"}"
wumbo_success "$result"
''')

# Usage
result = template(directory="/tmp", pattern="*.log")
```

## Advanced Features

### Template Configuration

```python
# Advanced runtime configuration
template = create_multi_language_template(
    'javascript',
    code='const result = wumboArgs.map(x => x * 2); wumbo.success(result);',
    
    # Runtime settings
    timeout=60,              # 60 second timeout
    max_memory_mb=2048,      # 2GB memory limit
    working_dir='/tmp/work', # Working directory
    
    # Environment variables
    env_vars={
        'NODE_ENV': 'development',
        'DEBUG': '1'
    },
    
    # Interpreter options
    node_args=['--max-old-space-size=2048'],
    
    # Serialization options
    serialization_format='json',
    serialization_encoding='utf-8',
    
    # Template metadata
    name='advanced_js_template',
    description='Advanced JavaScript template with custom config',
    metadata={'version': '1.0', 'author': 'developer'}
)
```

### Security Configuration

```python
from wumbo_framework.languages import ExecutionEnvironment

# Create secure execution environment
secure_env = ExecutionEnvironment(
    runtime=runtime,
    sandbox_enabled=True,
    network_access=False,     # Disable network
    file_system_access=False, # Disable file system
    allowed_imports=[         # Python: restrict imports
        'json', 'math', 're'
    ],
    resource_limits={
        'max_execution_time': 30,
        'max_memory_mb': 512,
        'max_output_size': 1024 * 1024  # 1MB
    }
)

# Apply to template
template = create_multi_language_template(
    'python',
    code=code,
    execution_environment=secure_env
)
```

### Error Handling

```python
from wumbo_framework import TemplateExecutionError

try:
    result = template(1, 2, 3)
    print(f"Success: {result}")
except TemplateExecutionError as e:
    print(f"Execution failed: {e.message}")
    print(f"Language: {e.metadata.get('language')}")
    print(f"Error type: {e.metadata.get('error_type')}")
    if e.metadata.get('stderr'):
        print(f"stderr: {e.metadata['stderr']}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Template Validation

```python
from wumbo_framework import validate_template_code

# Validate before creating template
code = '''
const result = wumboArgs.map(x => x * 2);
wumbo.success(result);
'''

if validate_template_code('javascript', code):
    template = javascript_template(code)
    print("Template created successfully")
else:
    print("Invalid template code")
```

## Configuration

### Runtime Detection

The framework automatically detects available language runtimes:

```python
from wumbo_framework import get_available_languages, get_language_info

# Check what's available
available = get_available_languages()
print(f"Available languages: {available}")

# Get detailed info for each language
for lang in available:
    info = get_language_info(lang)
    print(f"{lang}: {info['features']}")
```

### Custom Runtime Paths

```python
# Specify custom interpreter paths
template = create_multi_language_template(
    'python',
    code=code,
    interpreter_path='/opt/python3.11/bin/python3',
    python_args=['-O', '-u'],  # Optimized, unbuffered
)

# Or for Node.js
template = create_multi_language_template(
    'javascript',
    code=code,
    node_path='/usr/local/bin/node',
    node_args=['--harmony', '--experimental-modules']
)
```

### Environment Variables

```python
template = create_multi_language_template(
    'shell',
    code='''
    echo "Current user: $USER"
    echo "Custom var: $MY_CUSTOM_VAR"
    echo "Python path: $PYTHONPATH"
    ''',
    env_vars={
        'MY_CUSTOM_VAR': 'hello world',
        'PYTHONPATH': '/custom/python/path',
        'PATH': os.environ['PATH'] + ':/custom/bin'
    }
)
```

## Security

### Security Features

1. **Process Isolation**: Each template runs in a separate process
2. **Resource Limits**: CPU time, memory, and output size limits
3. **Filesystem Restrictions**: Configurable file system access
4. **Network Restrictions**: Configurable network access
5. **Import Restrictions**: Python import filtering
6. **Code Validation**: Syntax checking before execution

### Security Best Practices

```python
# Minimal permissions template
secure_template = create_multi_language_template(
    'python',
    code='''
    # Only basic operations allowed
    result = sum(x**2 for x in wumbo_args)
    wumbo_success(result)
    ''',
    
    # Strict security
    sandbox_enabled=True,
    network_access=False,
    file_system_access=False,
    timeout=10,
    max_memory_mb=128,
    
    # Allowed Python modules only
    allowed_imports=['math', 'json']
)
```

### Dangerous Operations

These operations are restricted or monitored:

- **File system access**: Reading/writing files
- **Network access**: HTTP requests, socket operations  
- **Process execution**: Running subprocesses
- **System calls**: Direct OS interaction
- **Import restrictions**: Dangerous Python modules

## Performance

### Performance Characteristics

| Language | Startup Time | Execution Speed | Memory Usage |
|----------|--------------|-----------------|--------------|
| Python | Fast | Medium | Medium |
| JavaScript | Medium | Fast | Medium |
| TypeScript | Slow (compilation) | Fast | Medium |
| Go | Slow (compilation) | Very Fast | Low |
| Shell | Very Fast | Slow | Very Low |

### Optimization Tips

1. **Reuse Templates**: Create once, execute many times
2. **Choose Right Language**: Go for CPU-intensive, Shell for file operations
3. **Minimize Compilation**: Cache compiled artifacts for TypeScript/Go
4. **Resource Limits**: Set appropriate memory and time limits
5. **Batch Operations**: Process multiple items in single execution

### Performance Example

```python
import time

# Performance comparison
test_data = list(range(1000))

# Measure execution time
def time_template(template, *args):
    start = time.time()
    result = template(*args)
    end = time.time()
    return result, (end - start) * 1000  # ms

# Test different languages
templates = {
    'Python': python_template('wumbo_success(sum(x*x for x in wumbo_args))'),
    'JavaScript': javascript_template('wumbo.success(wumboArgs.reduce((s,x) => s + x*x, 0));'),
    'Go': go_template('''
        sum := 0
        for _, arg := range wumboArgs {
            if num, ok := arg.(float64); ok {
                sum += int(num * num)
            }
        }
        wumbo.Success(sum)
    ''')
}

for name, template in templates.items():
    try:
        result, exec_time = time_template(template, *test_data)
        print(f"{name:10}: {result} ({exec_time:.2f}ms)")
    except Exception as e:
        print(f"{name:10}: Error - {e}")
```

## Troubleshooting

### Common Issues

#### 1. Runtime Not Found

```
Error: Node.js executable not found
```

**Solution**: Install the required runtime:
```bash
# For JavaScript/TypeScript
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

#### 2. Permission Denied

```
Error: Permission denied executing script
```

**Solution**: Check file permissions and execution policy:
```python
# Enable file system access if needed
template = create_multi_language_template(
    'shell',
    code=code,
    file_system_access=True
)
```

#### 3. Timeout Errors

```
Error: Template execution timed out
```

**Solution**: Increase timeout or optimize code:
```python
template = create_multi_language_template(
    'python',
    code=code,
    timeout=120  # 2 minutes
)
```

#### 4. Memory Limit Exceeded

```
Error: Memory limit exceeded
```

**Solution**: Increase memory limit or optimize code:
```python
template = create_multi_language_template(
    'javascript',
    code=code,
    max_memory_mb=2048  # 2GB
)
```

#### 5. Import/Module Errors

```python
# Python: Module not allowed
template = create_multi_language_template(
    'python',
    code='import os; wumbo_success("ok")',  # os module restricted
    allowed_imports=['os']  # Add to allowed list
)

# JavaScript: Package not found
template = javascript_template('''
// Make sure required packages are installed
const fs = require('fs');  // Built-in modules work
wumbo.success('ok');
''')
```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Create template with debug info
template = create_multi_language_template(
    'python',
    code=code,
    metadata={'debug': True}
)

# Execution will show detailed logs
result = template(1, 2, 3)
```

### Testing Templates

```python
# Test template with various inputs
def test_template(template, test_cases):
    for inputs, expected in test_cases:
        try:
            result = template(*inputs)
            assert result == expected, f"Expected {expected}, got {result}"
            print(f"✓ {inputs} -> {result}")
        except Exception as e:
            print(f"✗ {inputs} -> Error: {e}")

# Example test cases
test_cases = [
    ([1, 2, 3], 6),      # sum
    ([0], 0),            # edge case
    ([], 0),             # empty input
    ([-1, 1], 0),        # negative numbers
]

test_template(python_template('wumbo_success(sum(wumbo_args))'), test_cases)
```

### Getting Help

1. **Check Available Languages**: Use `get_available_languages()`
2. **Validate Code**: Use `validate_template_code()` before execution
3. **Review Logs**: Enable debug logging for detailed information
4. **Test Incrementally**: Start with simple templates and add complexity
5. **Check Documentation**: Each language interface has specific documentation

---

## Complete Example: Multi-Language Data Pipeline

Here's a comprehensive example showing a data processing pipeline using multiple languages:

```python
from wumbo_framework import *
import json

# Step 1: Data extraction (Shell)
extract_template = shell_template('''
# Extract data from CSV file
input_file="${WUMBO_KWARGS_input_file:-data.csv}"

if [ -f "$input_file" ]; then
    # Read CSV and convert to JSON
    result="["
    first=true
    while IFS=',' read -r name age city; do
        if [ "$first" = true ]; then
            first=false
        else
            result="$result,"
        fi
        result="$result{\\"name\\":\\"$name\\",\\"age\\":$age,\\"city\\":\\"$city\\"}"
    done < "$input_file"
    result="$result]"
    wumbo_success "$result"
else
    wumbo_error "Input file not found: $input_file"
fi
''')

# Step 2: Data processing (Python)
process_template = python_template('''
import json

# Parse JSON data from previous step
data_json = wumbo_args[0] if wumbo_args else "[]"
try:
    data = json.loads(data_json)
except json.JSONDecodeError:
    data = []

# Process data: filter adults and calculate stats
adults = [person for person in data if person.get('age', 0) >= 18]

if adults:
    ages = [person['age'] for person in adults]
    result = {
        'total_adults': len(adults),
        'average_age': sum(ages) / len(ages),
        'min_age': min(ages),
        'max_age': max(ages),
        'cities': list(set(person['city'] for person in adults))
    }
else:
    result = {'total_adults': 0}

wumbo_success(result)
''')

# Step 3: Report generation (TypeScript)
report_template = typescript_template('''
interface ProcessedData {
    total_adults: number;
    average_age?: number;
    min_age?: number;
    max_age?: number;
    cities?: string[];
}

interface Report {
    title: string;
    timestamp: string;
    data: ProcessedData;
    summary: string;
}

function generateReport(processedData: ProcessedData): Report {
    const data = processedData;
    
    let summary: string;
    if (data.total_adults === 0) {
        summary = "No adult records found in the dataset.";
    } else {
        summary = `Found ${data.total_adults} adults with average age ${data.average_age?.toFixed(1)} ` +
                 `(range: ${data.min_age}-${data.max_age}). Cities: ${data.cities?.join(', ')}.`;
    }
    
    return {
        title: "Data Processing Report",
        timestamp: new Date().toISOString(),
        data: data,
        summary: summary
    };
}

// Parse input data
const processedData: ProcessedData = typeof wumboArgs[0] === 'string' 
    ? JSON.parse(wumboArgs[0])
    : wumboArgs[0];

const report = generateReport(processedData);
wumbo.success(report);
''')

# Execute pipeline
def run_data_pipeline(csv_file: str):
    """Run the complete multi-language data pipeline."""
    try:
        # Step 1: Extract data
        print("Step 1: Extracting data...")
        raw_data = extract_template(input_file=csv_file)
        
        # Step 2: Process data  
        print("Step 2: Processing data...")
        processed_data = process_template(raw_data)
        
        # Step 3: Generate report
        print("Step 3: Generating report...")
        report = report_template(processed_data)
        
        print("Pipeline completed successfully!")
        return report
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
        return None

# Create sample data file
sample_csv = '''Alice,25,New York
Bob,17,London  
Charlie,30,Paris
Diana,22,Tokyo
Eve,16,Sydney'''

with open('sample_data.csv', 'w') as f:
    f.write(sample_csv)

# Run pipeline
result = run_data_pipeline('sample_data.csv')
if result:
    print(json.dumps(result, indent=2))
```

This example demonstrates:
- **Multi-language coordination**: Shell → Python → TypeScript
- **Data flow**: Each step processes output from previous step
- **Error handling**: Proper error propagation and handling
- **Type safety**: TypeScript provides compile-time type checking
- **Real-world scenario**: Complete data processing pipeline

The Wumbo multi-language system makes it easy to combine the strengths of different languages in a single application while maintaining consistency and reliability across the entire pipeline.