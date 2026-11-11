# Q2 - Tuples, Mutability and Copying

Run: `python complete_code.py` (the Complete the Code program, output.txt) and `python experiments.py` (everything else, output_experiments.txt).

## Complete the Code
TODO 1: `good = [[0] * cols for _ in range(rows)]`. Output equals the expected output: `bad` has 7 in every row, `good` only in row 0, `True False`, `T. Nagar`.

## Why the bug happens: memory diagram
`[[0] * 3] * 3` repeats a reference to ONE inner list three times:

    bad  ----> [ ref ][ ref ][ ref ]        all three refs point to the same list
                  \     |     /
                   +--> [0, 7, 0, 0]

The list comprehension builds a new inner list for every row:

    good ----> [ ref ][ ref ][ ref ]
                 |      |      |
                 v      v      v
            [0,7,0,0] [0,0,0,0] [0,0,0,0]        three separate lists

`bad[0] is bad[1]` is True and the ids of the three rows are equal; in `good` the ids are different (shown in output_experiments.txt).

## Aliasing, shallow copy and deep copy

| Operation | Copy after a[0] = 100 and a[1].append(99) |
|---|---|
| alias b = a | 100 , [2, 3, 99] |
| copy.copy(a) | 1 , [2, 3, 99] |
| a[:] | 1 , [2, 3, 99] |
| copy.deepcopy(a) | 1 , [2, 3] |

A shallow copy (`copy.copy`, `a[:]`) copies the outer list only, so inner lists are shared: it is enough when the elements are immutable (numbers, strings, tuples).
A deep copy (`copy.deepcopy`) is needed when the list contains lists that will be changed independently (like the grid).

## Why a function can change the caller's list
Python passes a reference to the same list object. `board(grid)` changes that object, so the caller sees it; `rebind(grid)` only binds the local name to a new list, so the caller does not.

## Tuples as dictionary keys; lists inside tuples
A dictionary key must be hashable: its hash must not change. A tuple of numbers is immutable, so it can be a key; a list can change, so `{[13.04, 80.23]: ...}`
raises `TypeError: unhashable type: 'list'`. A tuple that contains a list is immutable only in its references: `t[0].append(9)` works, and `t[0] += [5]` raises TypeError
(the tuple item cannot be re-assigned) although the list was already extended - so the tuple's content did change.

## Measurements
- 1,000,000 values: `sys.getsizeof` list 8,000,056 bytes, tuple 8,000,040 bytes (shallow sizes; the tuple has no spare room).
- Creating: list 0.0216 s, tuple 0.0204 s. 200,000 index reads: list 0.0104 s, tuple 0.011 s (about the same).

## Conclusion
Use a tuple for a fixed record such as (latitude, longitude): it can be a dictionary key, it cannot be changed by mistake, and it is safe to share. Immutability protects against
accidental changes through aliases and keeps hash values stable. Use a list when the content must grow or change.

## Alternative concept: dictionary keyed by (row, col)
Only the zones with passengers are stored. Access is O(1) average in both designs (200,000 reads: list of lists 0.0065 s, dictionary 0.0065 s).
Space is O(rows x cols) for the grid and O(number of non-empty zones) for the dictionary: for 1000 x 1000 zones with 1,000 non-empty ones, 7,875 KB against 36.1 KB.
