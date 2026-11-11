"""Q5: Cold-storage temperature monitor - loop vs list comprehension vs map/filter, generators, memory."""
import json
import random
import sys
import timeit
import tracemalloc


def make_readings(n, seed=7):
    """n readings in Celsius: mostly near 5 C, about 4% sensor errors beyond +-50 C."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        if rng.random() < 0.04:
            out.append(round(rng.choice([-1, 1]) * rng.uniform(50.1, 99.0), 1))
        else:
            out.append(round(rng.gauss(5, 3), 1))
    return out


def clean_loop(readings):
    """for loop with append: valid Celsius and Fahrenheit lists."""
    celsius, fahrenheit = [], []
    for c in readings:
        if -50 <= c <= 50:
            celsius.append(c)
            fahrenheit.append(c * 9 / 5 + 32)
    return celsius, fahrenheit


def clean_comprehension(readings):
    """List comprehensions with a condition: [expression for item in iterable if condition]."""
    celsius = [c for c in readings if -50 <= c <= 50]
    fahrenheit = [c * 9 / 5 + 32 for c in celsius]
    return celsius, fahrenheit


def clean_map_filter(readings):
    """map() and filter() with lambda."""
    celsius = list(filter(lambda c: -50 <= c <= 50, readings))
    fahrenheit = list(map(lambda c: c * 9 / 5 + 32, celsius))
    return celsius, fahrenheit


def alarm_minutes(readings):
    """Minutes (0, 1, 2, ...) of VALID readings outside 2-8 C, using enumerate()."""
    return [minute for minute, c in enumerate(readings) if -50 <= c <= 50 and not 2 <= c <= 8]


if __name__ == "__main__":
    sample = [4.5, 60.2, 9.1, -70.0, 1.9, 5.0, 8.0, 2.0, -50.0, 50.0]
    print("Sample readings:", sample)
    c, f = clean_comprehension(sample)
    print("  valid Celsius   :", c)
    print("  Fahrenheit      :", [round(x, 1) for x in f])
    print("  alarm minutes   :", alarm_minutes(sample), "(valid readings outside 2-8 C; errors are not alarms)")
    print("  dictionary comprehension (minute -> Celsius, valid only):", {m: t for m, t in enumerate(sample) if -50 <= t <= 50})
    print("  set comprehension (alarm minutes)                       :", {m for m, t in enumerate(sample) if -50 <= t <= 50 and not 2 <= t <= 8})
    assert clean_loop(sample) == clean_comprehension(sample) == clean_map_filter(sample)

    print("\nTests: all valid, all invalid, empty")
    for name, data in (("all valid", [3.0, 5.0, 9.5]), ("all invalid", [55.0, -60.0, 99.9]), ("empty", [])):
        a, b, cc = clean_loop(data), clean_comprehension(data), clean_map_filter(data)
        assert a == b == cc
        print(f"  {name:11}: valid {b[0]} | alarms {alarm_minutes(data)} | three versions identical: True")

    print("\nTimes in seconds (best of 3) and identical results")
    print(f"{'n':>9} | {'for + append':>12} | {'comprehension':>13} | {'map + filter':>12} | {'identical':>9}")
    rows = []
    for n in (10_000, 100_000, 1_000_000):
        data = make_readings(n)
        ref = clean_comprehension(data)
        same = ref == clean_loop(data) == clean_map_filter(data)
        t1 = min(timeit.repeat(lambda: clean_loop(data), number=1, repeat=3))
        t2 = min(timeit.repeat(lambda: clean_comprehension(data), number=1, repeat=3))
        t3 = min(timeit.repeat(lambda: clean_map_filter(data), number=1, repeat=3))
        print(f"{n:>9,} | {t1:>12.4f} | {t2:>13.4f} | {t3:>12.4f} | {str(same):>9}")
        rows.append({"n": n, "loop": round(t1, 4), "comp": round(t2, 4), "map": round(t3, 4), "same": same, "valid": len(ref[0])})

    print("\nList comprehension vs generator expression (1,000,000 readings)")
    data = make_readings(1_000_000)
    as_list = [c for c in data if -50 <= c <= 50]
    as_gen = (c for c in data if -50 <= c <= 50)
    print(f"  sys.getsizeof(list) = {sys.getsizeof(as_list):,} bytes | sys.getsizeof(generator) = {sys.getsizeof(as_gen):,} bytes")
    t_list_sum = min(timeit.repeat(lambda: sum([c for c in data if -50 <= c <= 50]), number=1, repeat=3))
    t_gen_sum = min(timeit.repeat(lambda: sum(c for c in data if -50 <= c <= 50), number=1, repeat=3))
    tracemalloc.start(); sum([c for c in data if -50 <= c <= 50]); peak_list = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
    tracemalloc.start(); sum(c for c in data if -50 <= c <= 50); peak_gen = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
    print(f"  sum over list comprehension: {t_list_sum:.4f} s, peak memory {peak_list / 1024:,.0f} KB")
    print(f"  sum over generator          : {t_gen_sum:.4f} s, peak memory {peak_gen / 1024:,.1f} KB")
    assert abs(sum(as_list) - sum(c for c in data if -50 <= c <= 50)) < 1e-6
    json.dump({"rows": rows, "list_bytes": sys.getsizeof(as_list), "gen_bytes": sys.getsizeof(as_gen),
               "t_list_sum": round(t_list_sum, 4), "t_gen_sum": round(t_gen_sum, 4),
               "peak_list_kb": round(peak_list / 1024), "peak_gen_kb": round(peak_gen / 1024, 1)}, open("results.json", "w"), indent=1)
