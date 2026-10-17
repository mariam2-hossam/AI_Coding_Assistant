# Sorting algorithms and binary search in Python

Bubble sort compares neighbours and swaps them. It is simple but slow, O(n^2).

```python
def bubble_sort(items):
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    result = items[:]            # do not change the original list
    n = len(result)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:          # already sorted, stop early
            break
    return result
```

Merge sort splits the list in two, sorts each half and merges them. It is O(n log n).

```python
def merge_sort(items):
    if len(items) <= 1:
        return items
    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])

    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
```

Quick sort picks a pivot and puts smaller values on the left and bigger values on the right.

```python
def quick_sort(items):
    if len(items) <= 1:
        return items
    pivot = items[len(items) // 2]
    smaller = [x for x in items if x < pivot]
    equal = [x for x in items if x == pivot]
    bigger = [x for x in items if x > pivot]
    return quick_sort(smaller) + equal + quick_sort(bigger)
```

Binary search works only on a sorted list and returns the index or -1.

```python
def binary_search(items, target):
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```
