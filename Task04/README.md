# Q4 - Sets: Elective Registration Clash Detection

Run: `python complete_code.py` (output.txt), `python electives.py` (output_experiments.txt, results.json) and `python make_venn.py` (needs matplotlib; makes venn.png).

## Complete the Code
    both = ai_elective & ot_elective                       # clash
    exactly_one = ai_elective ^ ot_elective                # symmetric difference
    neither = all_students - (ai_elective | ot_elective)   # not in the union

Output equals the expected output: clash `['192311004', '192311009']`, exactly one `['192311001', '192311002', '192311007', '192311010']`,
neither `['192311003', '192311005', '192311006', '192311008']`. With set methods (`intersection`, `symmetric_difference`, `difference` and `union`) the results are the same (checked in the program).

## Venn diagrams
See venn.png (A = AI elective, B = OT elective, rectangle = all students): A and B = clash; A or B = registered in any elective; A - B = only AI; B - A = only OT; A ^ B = exactly one; U - (A or B) = neither.

## Design and analysis
- A set keeps one copy of each value, because an element is stored by its hash and an equal element hashes to the same slot: adding a duplicate finds the existing element and changes nothing.
- `x in s` computes a hash and goes to the slot: O(1) average. `x in list` compares x with every element until it finds it: O(n).
- Sets cannot hold lists because lists are mutable and unhashable (a changing list would change its hash); tuples of immutable values are hashable, so they can be set elements.

## Experiment 1: membership (x not present, the worst case for a list)

| n register numbers | x in list (us) | x in set (us) | list / set |
|---|---|---|---|
| 10,000 | 53.482 | 0.0281 | 1,906 |
| 100,000 | 569.954 | 0.0269 | 21,204 |
| 1,000,000 | 8218.006 | 0.0286 | 287,001 |

## Experiment 2: finding the common students

| n = m | Nested loops: comparisons | Nested loops (s) | Sorted walk: comparisons | Sorted walk incl. sort (s) | set & (s) |
|---|---|---|---|---|---|
| 500 | 186,956 | 0.0053 | 743 | 0.0002 | 0.0001 |
| 1,000 | 765,408 | 0.0192 | 1,511 | 0.0004 | 0.0001 |
| 2,000 | 3,041,782 | 0.085 | 3,016 | 0.0009 | 0.0004 |
| 4,000 | 12,035,082 | 0.3029 | 5,996 | 0.0018 | 0.0006 |
| 100,000 | ~10,000,000,000 | too slow | 149,888 | 0.0643 | 0.0246 |
| 1,000,000 | ~1,000,000,000,000 | too slow | 1,500,926 | 1.0789 | 0.4371 |

Nested loops do up to n x m comparisons (O(n x m); fewer here because the inner loop stops at a match), the sorted walk does O(n + m) comparisons after sorting O(n log n + m log m), and `&` is O(min(n, m)) on average after the sets are built.
All three give the same students (asserted). Tests: empty and identical electives give the expected results (see output_experiments.txt); the small case was verified by hand: both = {004, 009}, exactly one = {001, 007, 002, 010}, neither = {003, 005, 006, 008}.

## Conclusion
Convert a list to a set before processing when you have many membership tests, need to remove duplicates or need set algebra (common, different, union). Information lost: the order of the items,
how many times an item occurred and indexing by position.

## Alternative concept: lists with nested loops or a sorted walk
Nested loops: time O(n x m), space O(1) extra. Sorted walk: time O(n log n + m log m), space O(n + m) for the sorted copies (O(1) if the lists are sorted in place). Sets: time O(n + m) on average to build and intersect, space O(n + m).
