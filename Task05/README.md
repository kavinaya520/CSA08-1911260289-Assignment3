# Q5 - List Comprehension: Cleaning Sensor Readings

Run: `python sensors.py` (output in output.txt). Valid readings are -50 C to 50 C (inclusive); alarm minutes are minutes of VALID readings outside 2-8 C (sensor errors are not alarms - assumption).

## Implementation
- For loop with `append` (`clean_loop`), list comprehensions (`clean_comprehension`), `filter()` and `map()` with lambda (`clean_map_filter`), alarms with `enumerate()` (`alarm_minutes`).
- Fahrenheit = C x 9 / 5 + 32.
- Dictionary comprehension `{minute: c for minute, c in enumerate(readings) if -50 <= c <= 50}` and set comprehension `{minute for minute, c in enumerate(readings) if ... and not 2 <= c <= 8}`.

## General form
    [expression for item in iterable if condition]

A comprehension becomes harder to read than a loop when it has several `for` parts or several conditions, needs more than one statement or has side effects: a loop with names and comments is then clearer.

## List comprehension vs generator expression
`[... for ...]` builds the whole list in memory; `(... for ...)` produces one value at a time when asked.

## Experiment: time and identical results

| n readings | for + append (s) | list comprehension (s) | map + filter (s) | Identical results |
|---|---|---|---|---|
| 10,000 | 0.0013 | 0.0012 | 0.0015 | True |
| 100,000 | 0.0128 | 0.0112 | 0.0178 | True |
| 1,000,000 | 0.1644 | 0.1426 | 0.1729 | True |

For 1,000,000 readings the list comprehension is the fastest, then the loop with append, then map and filter (the lambda is called for every element). All three give identical lists (checked).
Tests with all valid, all invalid and empty readings are in output.txt.

## Memory (1,000,000 readings, 959,795 valid)
`sys.getsizeof(list)` = 8,448,728 bytes, `sys.getsizeof(generator)` = 208 bytes. Peak memory while summing: list 8,251 KB, generator 0.4 KB; time 0.0621 s and 0.0605 s.

## Conclusion
A list comprehension is usually the best way to make a list (shortest and fastest), but not always the best choice: when the values are only read once (sum, max, a loop), a generator expression gives the same time
and about 20,000 times less memory; and when the logic is long a plain loop is easier to read. The measurements above support this.

## Alternative concept: generator expression
`sum(c for c in readings if -50 <= c <= 50)`: time O(n) in both; memory O(n) for the list comprehension and O(1) for the generator (measured above). The generator cannot be indexed or reused after it is consumed.
