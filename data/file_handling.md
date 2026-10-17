# Reading and writing files in Python with error handling

Always use `with` so the file closes by itself, and catch the errors you expect.

```python
import csv
import json


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {path}")
    except PermissionError:
        print(f"No permission to read: {path}")
    return None


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Could not read {path}: {e}")
        return None


def read_csv(path):
    rows = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(row)
    except FileNotFoundError:
        print(f"File not found: {path}")
    return rows


def write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
```
