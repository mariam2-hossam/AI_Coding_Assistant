# Calling a web API with the requests library

Always set a timeout and check the status code. Install with `pip install requests`.

```python
import requests


def get_json(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()      # raises for 4xx and 5xx
        return response.json()
    except requests.exceptions.Timeout:
        print("The request timed out")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return None


if __name__ == "__main__":
    data = get_json("https://api.github.com/repos/python/cpython")
    if data:
        print(data["full_name"], data["stargazers_count"])
```
