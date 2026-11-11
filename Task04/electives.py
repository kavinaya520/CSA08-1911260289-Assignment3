"""Q4: Elective clash detection - set algebra, membership speed, nested loops vs & vs sorted merge."""
import json
import random
import timeit


def clash_nested(a_list, b_list):
    """Nested loops: n * m comparisons. Returns (common, comparisons)."""
    common, comparisons = [], 0
    for x in a_list:
        for y in b_list:
            comparisons += 1
            if x == y:
                common.append(x)
                break
    return common, comparisons


def clash_sorted(a_list, b_list):
    """Sort both lists and walk through them together: O(n log n + m log m) to sort, O(n + m) to walk."""
    a, b = sorted(a_list), sorted(b_list)
    i = j = comparisons = 0
    common = []
    while i < len(a) and j < len(b):
        comparisons += 1
        if a[i] == b[j]:
            common.append(a[i]); i += 1; j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return common, comparisons


def clash_set(a_list, b_list):
    """set intersection: O(min(n, m)) average after the sets are built."""
    return sorted(set(a_list) & set(b_list))


def numbers(n, seed, start=192000000):
    """n distinct register numbers as strings, chosen from a pool of 2n."""
    rng = random.Random(seed)
    return [str(start + x) for x in rng.sample(range(2 * n), n)]


if __name__ == "__main__":
    ai = {"192311001", "192311004", "192311007", "192311009"}
    ot = {"192311002", "192311004", "192311009", "192311010"}
    everyone = {f"1923110{i:02d}" for i in range(1, 11)}
    print("Verification of the small case by hand")
    print("  AI = {001, 004, 007, 009}, OT = {002, 004, 009, 010}")
    print("  by hand: both = {004, 009}; exactly one = {001, 007, 002, 010}; neither = {003, 005, 006, 008}")
    assert sorted(ai & ot) == ["192311004", "192311009"]
    assert sorted(ai ^ ot) == ["192311001", "192311002", "192311007", "192311010"]
    assert sorted(everyone - (ai | ot)) == ["192311003", "192311005", "192311006", "192311008"]
    print("  program agrees with the hand result: True")

    print("\nDuplicates are removed automatically, reports are sorted")
    registrations = ["192311001", "192311004", "192311001", "192311004", "192311007"]
    print("  list with duplicates :", registrations, "->", len(registrations), "entries")
    print("  set(registrations)   :", sorted(set(registrations)), "->", len(set(registrations)), "students")

    print("\nTests: empty and identical electives")
    empty = set()
    print("  empty & empty:", empty & empty, "| AI & empty:", ai & empty, "| AI | empty == AI:", (ai | empty) == ai, "| AI - empty == AI:", (ai - empty) == ai)
    print("  identical: AI & AI == AI:", (ai & ai) == ai, "| AI ^ AI:", ai ^ ai, "| AI - AI:", ai - ai)
    print("\nSets cannot contain lists but can contain tuples")
    print("  {(1, 2), (3, 4)} works:", {(1, 2), (3, 4)})
    try:
        {[1, 2]}
    except TypeError as err:
        print("  {[1, 2]} -> TypeError:", err)

    print("\nMembership test: x in list vs x in set (x not present = worst case for the list)")
    print(f"{'n':>10} | {'x in list (us)':>14} | {'x in set (us)':>13} | {'ratio':>9}")
    member = []
    for n in (10_000, 100_000, 1_000_000):
        data = numbers(n, 1)
        s = set(data)
        absent = "1"                                  # never present: the list must be scanned completely
        reps_l = max(3, 2_000_000 // n)
        t_list = timeit.timeit(lambda: absent in data, number=reps_l) / reps_l * 1e6
        t_set = timeit.timeit(lambda: absent in s, number=200_000) / 200_000 * 1e6
        print(f"{n:>10,} | {t_list:>14.3f} | {t_set:>13.4f} | {t_list / t_set:>9,.0f}")
        member.append({"n": n, "list_us": round(t_list, 3), "set_us": round(t_set, 4), "ratio": round(t_list / t_set)})

    print("\nFinding common students: nested loops vs sorted walk vs set &")
    print(f"{'n = m':>9} | {'nested cmp':>11} | {'nested s':>9} | {'sorted cmp':>10} | {'sorted s':>9} | {'set & s':>8}")
    common_rows = []
    for n in (500, 1_000, 2_000, 4_000, 100_000, 1_000_000):
        a, b = numbers(n, 1), numbers(n, 2)
        ref = clash_set(a, b)
        if n <= 4_000:
            (c1, cmp1), t1 = clash_nested(a, b), min(timeit.repeat(lambda: clash_nested(a, b), number=1, repeat=1))
            assert sorted(c1) == ref
            t1s, cmp1s = f"{t1:.4f}", f"{cmp1:,}"
        else:
            t1, t1s, cmp1, cmp1s = None, "too slow", None, f"~{n * n:,}"
        (c2, cmp2) = clash_sorted(a, b)
        assert c2 == ref
        t2 = min(timeit.repeat(lambda: clash_sorted(a, b), number=1, repeat=2))
        t3 = min(timeit.repeat(lambda: clash_set(a, b), number=1, repeat=2))
        print(f"{n:>9,} | {cmp1s:>11} | {t1s:>9} | {cmp2:>10,} | {t2:>9.4f} | {t3:>8.4f}")
        common_rows.append({"n": n, "nested_cmp": cmp1, "nested_s": None if t1 is None else round(t1, 4),
                            "sorted_cmp": cmp2, "sorted_s": round(t2, 4), "set_s": round(t3, 4), "common": len(ref)})
    json.dump({"member": member, "common": common_rows}, open("results.json", "w"), indent=1)
