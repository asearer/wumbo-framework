
# 🌀 wumbo

**`wumbo`** is a highly adaptable, universal Python function template designed to serve as a flexible foundation for nearly any task. Whether you're transforming data, executing dynamic workflows, calling APIs, or prototyping pipelines — `wumbo` is your go-to tool.

> Think of `wumbo` like a Swiss Army knife for Python functions.

---

## 📦 Installation

You don’t need to install anything. Just copy the function into your project:

```python
def wumbo(*args, **kwargs):
    """
    Universal function template: wumbo

    Args:
        *args: Positional arguments (list, data, functions, etc.).
        **kwargs: Keyword arguments for optional configuration.

    Returns:
        Depends on the use case – modify as needed.
    """
    # Example: Logging inputs
    print("🌀 Wumbo initiated...")
    print("Args:", args)
    print("Kwargs:", kwargs)

    # Step 1: Preprocessing (optional)
    if kwargs.get("preprocess"):
        args = [kwargs["preprocess"](arg) for arg in args]
        print("Preprocessed Args:", args)

    # Step 2: Core logic placeholder
    results = []
    for arg in args:
        try:
            # Default operation or injected function
            if "operation" in kwargs and callable(kwargs["operation"]):
                result = kwargs["operation"](arg)
            else:
                result = arg  # Default passthrough
            results.append(result)
        except Exception as e:
            print(f"Error processing {arg}: {e}")
            if kwargs.get("fail_silently", True):
                results.append(None)
            else:
                raise e

    # Step 3: Postprocessing (optional)
    if kwargs.get("postprocess"):
        results = kwargs["postprocess"](results)

    # Step 4: Output
    if kwargs.get("as_dict", False):
        return {f"item_{i}": val for i, val in enumerate(results)}
    if kwargs.get("as_single", False) and len(results) == 1:
        return results[0]
    return results
```

---

## 🚀 Quick Start

### ✅ Basic Example

```python
wumbo(1, 2, 3)
# Output: [1, 2, 3]
```

### 🔧 Apply a Function

```python
wumbo(2, 4, 6, operation=lambda x: x ** 2)
# Output: [4, 16, 36]
```

### 🧼 Preprocess and Postprocess

```python
wumbo("hello", "world",
      preprocess=str.upper,
      operation=lambda x: f"[{x}]",
      postprocess=lambda results: " | ".join(results))
# Output: [HELLO] | [WORLD]
```

### 🧩 Custom Output

```python
wumbo(100, 200, as_dict=True)
# Output: {'item_0': 100, 'item_1': 200}
```

---

## 🔍 Parameters

| Parameter       | Type      | Description                                                                 |
|----------------|-----------|-----------------------------------------------------------------------------|
| `*args`        | any       | Positional arguments to process.                                            |
| `preprocess`   | function  | Function to apply to each argument before main operation.                   |
| `operation`    | function  | Core function to apply to each item. Defaults to passthrough.               |
| `postprocess`  | function  | Function to apply to the final result list.                                 |
| `fail_silently`| bool      | If `True`, errors are caught and replaced with `None`. Defaults to `True`.  |
| `as_dict`      | bool      | If `True`, returns results as a dictionary.                                 |
| `as_single`    | bool      | If `True` and only one result, returns the item instead of a list.          |

---

## 🧠 Why Use wumbo?

- Perfect for prototyping dynamic workflows.
- Reduces boilerplate code.
- Built-in error handling and data transformation.
- Easily extendable for APIs, ETL pipelines, and more.

---

## 🧪 Testing Ideas

```python
# JSON transformation
wumbo('{"a": 1}', operation=lambda x: json.loads(x))

# Mathematical operations
wumbo(3, 6, 9, operation=lambda x: x + 10)

# Filtering + Mapping
wumbo("apple", "banana", "cherry",
      preprocess=str.upper,
      operation=lambda x: x if "A" in x else None,
      postprocess=lambda r: list(filter(None, r)))
```

---

## 🔄 Customize It

Want to build an async version? Wrap the operation in `await` and define `async def wumbo`.

Need logging? Add `logging` or plug in a custom logger via kwargs.

---

## 🙏 Credits

Created by the idea of *doing everything and nothing at the same time.* Inspired by the flexibility of tools like Lodash, Ramda, and Python's own `functools`.

---

## 📜 License

MIT License. Use it, break it, improve it, remix it.
```

---
