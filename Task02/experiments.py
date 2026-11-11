"""Q2: tuples, mutability, aliasing, shallow and deep copy, memory and time of list vs tuple."""
import copy
import json
import random
import sys
import timeit
import tracemalloc

rows, cols = 3, 4
bad = [[0] * cols] * rows
good = [[0] * cols for _ in range(rows)]

print("Bug and correction with is and id()")
print("  bad  row ids :", [id(r) % 100000 for r in bad], "-> one object:", len({id(r) for r in bad}) == 1)
print("  good row ids :", [id(r) % 100000 for r in good], "-> separate objects:", len({id(r) for r in good}) == rows)

print("\nAliasing, shallow copy and deep copy of a = [1, [2, 3]]")
results = {}
for name, make in (("alias b = a", lambda a: a), ("copy.copy(a)", copy.copy), ("a[:]", lambda a: a[:]), ("copy.deepcopy(a)", copy.deepcopy)):
    a = [1, [2, 3]]
    b = make(a)
    a[0] = 100            # change an element of the outer list
    a[1].append(99)       # change the inner list
    results[name] = (b[0], b[1])
    print(f"  {name:<17} after a[0] = 100 and a[1].append(99): copy is {b}")
print("  shallow copies copy the outer list only, so the inner list is still shared; deepcopy copies everything")

print("\nA function that changes a list argument changes the caller's list")
grid = [[0] * cols for _ in range(rows)]


def board(g):
    """Changes the list object that the caller also refers to."""
    g[0][0] += 1


def rebind(g):
    """Assigns a new list to the local name only; the caller is not affected."""
    g = [[0] * cols for _ in range(rows)]
    return g


board(grid)
rebind(grid)
print("  after board(grid) and rebind(grid):", grid[0], "(board changed it, rebind did not)")

print("\nUnpacking tuples in a for loop")
stops = {(13.0827, 80.2707): "Chennai Central", (13.0418, 80.2341): "T. Nagar"}
for (lat, lon), name in stops.items():
    print(f"  {name}: latitude {lat}, longitude {lon}")

print("\nA list as a dictionary key")
try:
    {[13.0418, 80.2341]: "T. Nagar"}
except TypeError as err:
    print("  TypeError:", err)

print("\nA list stored inside a tuple")
t = ([1, 2], 3)
t[0].append(9)
print("  t[0].append(9) works:", t)
try:
    t[0] += [5]
except TypeError as err:
    print("  t[0] += [5] -> TypeError:", err)
print("  but the list inside was still extended:", t)

print("\nMemory and time: list vs tuple of 1,000,000 values")
n = 1_000_000
lst, tup = list(range(n)), tuple(range(n))
print(f"  sys.getsizeof(list) = {sys.getsizeof(lst):,} bytes | sys.getsizeof(tuple) = {sys.getsizeof(tup):,} bytes")
t_make_list = min(timeit.repeat(lambda: list(range(n)), number=1, repeat=3))
t_make_tuple = min(timeit.repeat(lambda: tuple(range(n)), number=1, repeat=3))
idx = random.Random(3).sample(range(n), 200_000)
t_idx_list = min(timeit.repeat(lambda: [lst[i] for i in idx], number=1, repeat=3))
t_idx_tuple = min(timeit.repeat(lambda: [tup[i] for i in idx], number=1, repeat=3))
print(f"  create list {t_make_list:.4f} s | create tuple {t_make_tuple:.4f} s")
print(f"  200,000 index reads: list {t_idx_list:.4f} s | tuple {t_idx_tuple:.4f} s")

print("\nAlternative: dictionary keyed by (row, col) holding only zones with passengers")
R, C, filled = 1000, 1000, 1000
rng = random.Random(5)
cells = {(rng.randrange(R), rng.randrange(C)): rng.randint(1, 50) for _ in range(filled)}
tracemalloc.start(); grid_list = [[0] * C for _ in range(R)]; m_grid = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
for (r, c), v in cells.items():
    grid_list[r][c] = v
tracemalloc.start(); grid_dict = dict(cells); m_dict = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
keys = list(cells)
probe = [rng.choice(keys) for _ in range(200_000)]
t_g = min(timeit.repeat(lambda: [grid_list[r][c] for r, c in probe], number=1, repeat=3))
t_d = min(timeit.repeat(lambda: [grid_dict[k] for k in probe], number=1, repeat=3))
assert all(grid_list[r][c] == grid_dict[(r, c)] for r, c in probe)
print(f"  1000 x 1000 grid: list of lists {m_grid / 1024:,.0f} KB | dict with {filled} non-empty zones {m_dict / 1024:,.1f} KB")
print(f"  200,000 reads: list of lists {t_g:.4f} s | dict {t_d:.4f} s")

json.dump({"size_list": sys.getsizeof(lst), "size_tuple": sys.getsizeof(tup), "make_list": round(t_make_list, 4),
           "make_tuple": round(t_make_tuple, 4), "idx_list": round(t_idx_list, 4), "idx_tuple": round(t_idx_tuple, 4),
           "grid_kb": round(m_grid / 1024), "dict_kb": round(m_dict / 1024, 1), "read_grid": round(t_g, 4), "read_dict": round(t_d, 4),
           "copies": {k: [str(x) for x in v] for k, v in results.items()}}, open("results.json", "w"), indent=1)
