# Q1 - Lists and Slicing: Daily Rainfall Records

Run: `python rainfall.py` (output in output.txt, raw numbers in results.json). The readings are made with `random.Random(2026)`, so every run gives the same data.

## Implementation (365 readings)
- Weekly totals with slicing: `[sum(readings[i:i+7]) for i in range(0, n, 7)]` gives 53 blocks (52 full weeks and one extra day).
- Wettest full week: week 22 with 220.9 mm. Driest full week: week 16 with 2.0 mm.
- Maximum 60.0 mm on day 17; minimum 0.0 mm on day 1 (`max()`, `min()` and `index()`).
- Dry days (0 mm): 197 days, found with `enumerate()`.
- 7-day moving average: 359 values for 365 days; the naive, running-sum and deque versions agree.

## Design: pseudocode of the moving average
    NAIVE:                                  RUNNING SUM:
    for i = 0 to n - 7                      total = sum of the first 7 readings
        total = 0                           add total / 7 to the result
        for each of the 7 values            for i = 7 to n - 1
            total = total + value               total = total + reading[i] - reading[i-7]
        add total / 7 to the result             add total / 7 to the result

## What the slices return
- `readings[7:14]` - the 7 readings with index 7 to 13, that is days 8 to 14 (the second week); the end index is not included.
- `readings[-7:]` - the last 7 readings (the last week of the year).
- `readings[::7]` - every 7th reading starting from day 1 (days 1, 8, 15, ...), 53 values.

## Why a list, and the cost of its operations
A list keeps the days in order and `readings[d - 1]` reaches any day in O(1). `append` and `pop()` at the end are O(1) (amortised),
`insert(i, x)` and `pop(i)` are O(n) because later items are shifted, `sort()` is O(n log n). Measured (time of the pair of operations):

| n | append + pop() (us) | insert(0) + pop(0) (us) | sort random list (ms) |
|---|---|---|---|
| 365 | 0.116 | 0.41 | 0.019 |
| 36500 | 0.128 | 25.471 | 4.266 |
| 365000 | 1.311 | 247.915 | 49.263 |

## Derived and counted additions
Naive: every window needs 7 additions, there are n - 6 windows, so 7(n - 6) additions. Running sum: 7 additions for the first window,
then one addition and one subtraction for each of the remaining n - 7 windows. The counts in the program (counted, not assumed) equal the formulas.

| n days | Naive additions (7(n-6)) | Running-sum additions (7+(n-7)) | Running-sum subtractions | Naive time (s) | Running sum (s) | deque (s) |
|---|---|---|---|---|---|---|
| 365 | 2,513 | 365 | 358 | 0.0001 | 0.0000 | 0.0001 |
| 36500 | 255,458 | 36,500 | 36,493 | 0.0117 | 0.0031 | 0.0053 |
| 365000 | 2,554,958 | 365,000 | 364,993 | 0.1166 | 0.0345 | 0.0681 |

The naive method does about 7 times more additions (2,554,958 against 365,000 for n = 365,000); the measured time is about 3 to 4 times smaller
for the running sum (not 7 times, because every step of both methods also pays for the loop, indexing and appending).

## Tests
Empty list: weekly totals `[]`, extremes `None`, moving average `[]`. List of 5 values: one weekly total (7.5), moving average `[]` (no complete window of 7).

## Design question: a reading that arrives late
`list.insert(i, x)` costs O(n - i): at n = 365,000 the insert at the front took about 247.915 us, against about
1.311 us for append. It also shifts every later reading by one position, so the day numbers after the insertion are wrong.
For 365 values the cost is negligible and a list is still fine; I would keep one slot for every day (placeholder None) and assign `readings[d - 1] = x`
(O(1)), or use a dictionary keyed by date if readings arrive in any order.

## Alternative concept: deque(maxlen=7) or a dictionary keyed by date
`moving_average_deque` keeps only the current window of 7 values in a `collections.deque(maxlen=7)`: O(n) time with a running total, and O(7) = O(1) space
for the window (the output list is still O(n)). A slicing moving average costs O(7n). A dictionary keyed by date gives O(1) access by date but needs
O(n) space with a larger constant: 30,453 KB for 365,000 readings, against 2,852 KB for the list. Measured at n = 365,000: naive
0.1166 s, running sum 0.0345 s, deque 0.0681 s.
