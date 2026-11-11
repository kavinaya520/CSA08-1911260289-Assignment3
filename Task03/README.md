# Q3 - Dictionaries: Farmer Helpline Complaint Analysis

Run: `python complete_code.py` (output.txt) and `python complaints.py` (output_experiments.txt, results.json).

## Complete the Code
- TODO 1: `counts[word] = counts.get(word, 0) + 1` for every word not in `stop`.
- TODO 2: `sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:k]`.
Output: `[('seeds', 3), ('price', 2), ('received', 2)]` (equal to the expected output).

Why `price` comes before `received`: both occur twice, so the second part of the sort key (the word) decides, and "price" is before "received" alphabetically.

## Implementation
`complaints.py` counts with `get()` and with `setdefault()`, groups complaints by district and by crop into a dictionary of lists with `setdefault(key, []).append(...)`
(the number per district is `len` of each list), removes stop words with a set, and finds the top k words. Tests: empty text gives `{}`, "Seeds SEEDS seeds" gives `seeds: 3`,
punctuation is removed before splitting.

## Design and analysis
- How a dictionary finds a key: it computes `hash(key)`, uses it to pick a slot in a table, and compares the key stored there; if another key is in the slot it probes the next slots.
  The table is resized so that it stays mostly empty, so on average only a few slots are checked whatever the number of keys: average lookup is O(1), not dependent on the size.
- Dictionary vs `list.count()` for every distinct word: the dictionary reads each word once (O(n)); `list.count(word)` scans the whole list for every distinct word (O(n x d)).
- Order: since Python 3.7 a dictionary keeps the insertion order of its keys (this is part of the language).
- `keys()`, `values()` and `items()` return live views: after a key is added the view shows it (demonstrated in output_experiments.txt); `items()` gives (key, value) pairs.

## Experiment: 1,000, 10,000 and 100,000 complaints (150 distinct words)

| Complaints | Words n | Distinct d | dict + get (s) | setdefault (s) | list.count (s) | Counter (s) | n x d |
|---|---|---|---|---|---|---|---|
| 1,000 | 6,358 | 150 | 0.0055 | 0.0060 | 0.0209 | 0.0056 | 953,700 |
| 10,000 | 63,662 | 150 | 0.0426 | 0.0452 | 0.1570 | 0.0386 | 9,549,300 |
| 100,000 | 638,299 | 150 | 0.3809 | 0.3754 | 1.4423 | 0.3959 | 95,744,850 |

All four methods give identical counts (asserted). The dictionary loop, `setdefault` and `Counter` are all O(n) and about equal in time (most of the time is spent splitting
and cleaning the text); `list.count()` is slower by a factor that grows with d. `Counter.most_common` keeps ties in first-appearance order, so I sort with the key (-count, word) to get alphabetical ties.

## Engineering decision for 100,000 complaints a day
I would deploy `collections.Counter` (or the equivalent dictionary loop) for the counting and the sorted key for the top k. It is O(n) in time and O(d) in space, took about
0.40 s for 100,000 complaints, is short and well tested. `list.count()` is O(n x d): it already needs 1.44 s and gets slower with every new word in the vocabulary.

## Alternative concept: list.count() or Counter
- `list.count()` for each distinct word: time O(n x d) (95,744,850 element comparisons for 100,000 complaints), space O(n) for the word list plus O(d) for the result.
- `Counter`: time O(n), space O(d); the same algorithm as the dictionary loop but written in C, so it is shorter and a little faster on a plain list of words.
