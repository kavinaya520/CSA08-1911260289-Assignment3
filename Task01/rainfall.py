"""Q1: Village rain-gauge station - lists, slicing, moving average (naive vs running sum), list costs."""
import json
import random
import sys
import timeit
import time
import tracemalloc
from collections import deque


def make_readings(n, seed=2026):
    """n daily readings in mm; about 55% of the days are dry (0 mm). The seed makes runs repeatable."""
    rng = random.Random(seed)
    return [0.0 if rng.random() < 0.55 else round(rng.uniform(0.5, 60.0), 1) for _ in range(n)]


def weekly_totals(readings):
    """Total of every block of 7 days, using slicing (the last block can be shorter)."""
    return [round(sum(readings[i:i + 7]), 1) for i in range(0, len(readings), 7)]


def extremes(readings):
    """Maximum and minimum with their day numbers (first occurrence); None for an empty list."""
    if not readings:
        return None
    high, low = max(readings), min(readings)
    return high, readings.index(high) + 1, low, readings.index(low) + 1


def dry_days(readings):
    """Day numbers with 0 mm."""
    return [day for day, mm in enumerate(readings, 1) if mm == 0]


def moving_average_naive(readings, window=7):
    """Add the 7 values of every window again: 7 additions per window."""
    out = []
    for i in range(len(readings) - window + 1):
        total = 0.0
        for value in readings[i:i + window]:
            total += value
        out.append(total / window)
    return out


def moving_average_running(readings, window=7):
    """Running sum: add the new value and subtract the value that leaves the window."""
    if len(readings) < window:
        return []
    total = sum(readings[:window])
    out = [total / window]
    for i in range(window, len(readings)):
        total += readings[i] - readings[i - window]
        out.append(total / window)
    return out


def moving_average_deque(readings, window=7):
    """Alternative: a deque(maxlen=7) holds only the current window (streaming)."""
    win, total, out = deque(maxlen=window), 0.0, []
    for value in readings:
        if len(win) == window:
            total -= win[0]
        win.append(value)
        total += value
        if len(win) == window:
            out.append(total / window)
    return out


def count_additions(readings, window=7):
    """Count the additions and subtractions actually done by the two methods."""
    n = len(readings)
    naive = 0
    for i in range(n - window + 1):
        naive += window                      # one addition per value of the window
    running_add = running_sub = 0
    if n >= window:
        running_add = window
        for i in range(window, n):
            running_add += 1
            running_sub += 1
    return naive, running_add, running_sub


if __name__ == "__main__":
    readings = make_readings(365)
    print("Station year (365 days, seed 2026)")
    print("  first 14 readings:", readings[:14])
    print("  readings[7:14]  (days 8 to 14)         :", readings[7:14])
    print("  readings[-7:]   (last 7 days)          :", readings[-7:])
    print("  readings[::7]   (every 7th: days 1, 8, ...):", len(readings[::7]), "values, first 5 =", readings[::7][:5])

    weeks = weekly_totals(readings)
    full = len(readings) // 7
    best = max(range(full), key=lambda w: weeks[w])
    worst = min(range(full), key=lambda w: weeks[w])
    print(f"\nWeekly totals: {len(weeks)} blocks (52 full weeks + {len(readings) % 7} extra day)")
    print(f"  wettest full week: week {best + 1} = {weeks[best]} mm | driest full week: week {worst + 1} = {weeks[worst]} mm")
    high, hday, low, lday = extremes(readings)
    print(f"  maximum {high} mm on day {hday} | minimum {low} mm on day {lday}")
    dry = dry_days(readings)
    print(f"  dry days: {len(dry)} days, first 10 = {dry[:10]}")
    ma = moving_average_running(readings)
    print(f"  7-day moving average: {len(ma)} values, first 3 = {[round(x, 2) for x in ma[:3]]}")
    assert all(abs(a - b) < 1e-6 for a, b in zip(ma, moving_average_naive(readings)))
    assert all(abs(a - b) < 1e-6 for a, b in zip(ma, moving_average_deque(readings)))
    print("  naive, running-sum and deque versions agree: True")

    print("\nTests: empty list and a list shorter than 7")
    for name, data in (("empty", []), ("5 values", [1.0, 0.0, 2.5, 0.0, 4.0])):
        print(f"  {name:9}: weekly {weekly_totals(data)} | extremes {extremes(data)} | moving average {moving_average_running(data)}")

    print("\nAdditions for the moving average (window 7): derived vs counted")
    print("  naive: 7 * (n - 6)   running sum: 7 + (n - 7) additions and (n - 7) subtractions")
    sizes = [365, 36_500, 365_000]
    print(f"{'n':>8} | {'naive derived':>13} | {'naive counted':>13} | {'run add derived':>15} | {'run add counted':>15} | {'naive s':>8} | {'running s':>9} | {'deque s':>8}")
    rows = []
    for n in sizes:
        data = make_readings(n)
        c_naive, c_add, c_sub = count_additions(data)
        d_naive, d_add = 7 * (n - 6), 7 + (n - 7)
        assert (c_naive, c_add, c_sub) == (d_naive, d_add, n - 7)
        t_naive = min(timeit.repeat(lambda: moving_average_naive(data), number=1, repeat=3))
        t_run = min(timeit.repeat(lambda: moving_average_running(data), number=1, repeat=3))
        t_deq = min(timeit.repeat(lambda: moving_average_deque(data), number=1, repeat=3))
        print(f"{n:>8} | {d_naive:>13,} | {c_naive:>13,} | {d_add:>15,} | {c_add:>15,} | {t_naive:>8.4f} | {t_run:>9.4f} | {t_deq:>8.4f}")
        rows.append({"n": n, "naive_adds": d_naive, "running_adds": d_add, "running_subs": n - 7,
                     "t_naive": round(t_naive, 5), "t_running": round(t_run, 5), "t_deque": round(t_deq, 5)})

    print("\nCost of list operations (time of a pair of operations, microseconds)")
    print(f"{'n':>8} | {'append+pop()':>12} | {'insert(0)+pop(0)':>16} | {'sort random list (ms)':>21}")
    ops = []
    for n in sizes:
        base = make_readings(n)
        lst = base[:]
        t_app = timeit.timeit(lambda: (lst.append(1.0), lst.pop()), number=2000) / 2000 * 1e6
        t_ins = timeit.timeit(lambda: (lst.insert(0, 1.0), lst.pop(0)), number=200) / 200 * 1e6
        shuffled = base[:]
        random.Random(1).shuffle(shuffled)
        t_sort = min(timeit.repeat(lambda: sorted(shuffled), number=1, repeat=3)) * 1000
        print(f"{n:>8} | {t_app:>12.3f} | {t_ins:>16.3f} | {t_sort:>21.3f}")
        ops.append({"n": n, "append_pop_us": round(t_app, 3), "insert0_pop0_us": round(t_ins, 3), "sort_ms": round(t_sort, 3)})

    print("\nDesign question: a late reading for day d")
    late = readings[:]
    late.insert(100, 12.5)
    print("  list.insert(100, x) shifts every later reading: days after 100 now sit one position too far (length", len(late), ")")
    print("  readings[d - 1] = x is O(1) when a slot for every day already exists (placeholder None for a missing reading)")

    print("\nSpace: 365,000 readings as a list vs a dictionary keyed by day")
    data = make_readings(365_000)
    tracemalloc.start(); as_list = list(data); m_list = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
    tracemalloc.start(); as_dict = {d: v for d, v in enumerate(data, 1)}; m_dict = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
    print(f"  list {m_list / 1024:,.0f} KB | dict {m_dict / 1024:,.0f} KB (the float objects are shared with the original list)")

    json.dump({"weeks": len(weeks), "wettest": [best + 1, weeks[best]], "driest": [worst + 1, weeks[worst]],
               "max": [high, hday], "min": [low, lday], "dry_days": len(dry), "rows": rows, "ops": ops,
               "mem_list_kb": round(m_list / 1024), "mem_dict_kb": round(m_dict / 1024)}, open("results.json", "w"), indent=1)
