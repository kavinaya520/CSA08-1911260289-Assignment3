"""Q3: Kisan call centre - word frequencies, grouping, top-k, dict vs list.count() vs Counter."""
import json
import random
import string
import timeit
from collections import Counter

STOP = {"not", "high", "is", "the", "a", "my", "and", "of"}


def words_of(text):
    """Lower-case the text, remove punctuation and split into words ([] for empty text)."""
    cleaned = text.lower().translate(str.maketrans("", "", string.punctuation))
    return cleaned.split()


def frequencies_get(texts, stop=STOP):
    """Dictionary loop with dict.get()."""
    counts = {}
    for text in texts:
        for word in words_of(text):
            if word not in stop:
                counts[word] = counts.get(word, 0) + 1
    return counts


def frequencies_setdefault(texts, stop=STOP):
    """The same count using dict.setdefault() (stores a list, then len() is the count)."""
    seen = {}
    for text in texts:
        for word in words_of(text):
            if word not in stop:
                seen.setdefault(word, []).append(1)
    return {word: len(ones) for word, ones in seen.items()}


def frequencies_list_count(texts, stop=STOP):
    """list.count() for every distinct word: n * d comparisons."""
    words = [w for text in texts for w in words_of(text) if w not in stop]
    return {word: words.count(word) for word in set(words)}


def frequencies_counter(texts, stop=STOP):
    """collections.Counter."""
    return Counter(w for text in texts for w in words_of(text) if w not in stop)


def top(counts, k):
    """k most frequent (word, count) pairs: highest count first, alphabetical for ties."""
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:k]


def group_by(records, key_index):
    """Group (district, crop, text) records into a dictionary of lists using setdefault()."""
    groups = {}
    for record in records:
        groups.setdefault(record[key_index], []).append(record[2])
    return groups


VOCAB = ["seeds", "fertiliser", "price", "subsidy", "received", "delayed", "pump", "water", "loan", "insurance", "crop", "pest",
         "rain", "drought", "tractor", "electricity", "market", "payment", "scheme", "soil", "test", "urea", "credit", "card",
         "disease", "yellow", "leaves", "damage"] + [f"w{i}" for i in range(122)]
DISTRICTS = ["Thanjavur", "Madurai", "Salem", "Erode", "Vellore"]
CROPS = ["paddy", "cotton", "sugarcane", "groundnut"]


def make_complaints(n, seed=11):
    """n complaints (district, crop, text); the vocabulary has 150 words."""
    rng = random.Random(seed)
    stop_list = sorted(STOP)
    out = []
    for _ in range(n):
        words = [rng.choice(VOCAB) if rng.random() < 0.85 else rng.choice(stop_list) for _ in range(rng.randint(5, 10))]
        out.append((rng.choice(DISTRICTS), rng.choice(CROPS), " ".join(words)))
    return out


if __name__ == "__main__":
    print("Small test (from the question)")
    calls = ["seeds not received seeds delayed", "fertiliser price high", "seeds price high subsidy not received"]
    stop = {"not", "high"}
    print(" ", top(frequencies_get(calls, stop), 3))
    freq = frequencies_get(calls, stop)
    print("  price and received both occur", freq["price"], "times; the tie is broken alphabetically ('price' < 'received').")
    assert frequencies_get(calls, stop) == frequencies_setdefault(calls, stop) == frequencies_list_count(calls, stop) == dict(frequencies_counter(calls, stop))

    print("\nEdge cases: empty text, upper/lower case, punctuation")
    print("  empty text      :", frequencies_get([""]), frequencies_get([]))
    print("  upper/lower case:", frequencies_get(["Seeds SEEDS seeds"]))
    print("  punctuation     :", frequencies_get(["Seeds, seeds! (late) price?"]))

    records = make_complaints(20)
    by_district = group_by(records, 0)
    by_crop = group_by(records, 1)
    print("\nComplaints per district (20 sample complaints):", {d: len(v) for d, v in sorted(by_district.items())})
    print("Complaints per crop                           :", {c: len(v) for c, v in sorted(by_crop.items())})
    print("First complaint for paddy:", by_crop["paddy"][0])

    print("\nDictionary views: keys(), values(), items() are live views (Python 3.7+ keeps insertion order)")
    d = {"seeds": 3, "price": 2}
    keys, items = d.keys(), d.items()
    d["urea"] = 1
    print("  keys view after adding a key :", list(keys), "| items:", list(items))

    print("\nTimings (seconds) for 1,000 / 10,000 / 100,000 complaints, 150 distinct words")
    print(f"{'complaints':>10} | {'words n':>8} | {'distinct d':>10} | {'dict get':>8} | {'setdefault':>10} | {'list.count':>10} | {'Counter':>8} | {'n*d':>12}")
    rows = []
    for n in (1_000, 10_000, 100_000):
        data = make_complaints(n)
        texts = [r[2] for r in data]
        words = sum(len([w for w in words_of(t) if w not in STOP]) for t in texts)
        ref = frequencies_get(texts)
        t1 = min(timeit.repeat(lambda: frequencies_get(texts), number=1, repeat=2))
        t2 = min(timeit.repeat(lambda: frequencies_setdefault(texts), number=1, repeat=2))
        t3 = min(timeit.repeat(lambda: frequencies_list_count(texts), number=1, repeat=1))
        t4 = min(timeit.repeat(lambda: frequencies_counter(texts), number=1, repeat=2))
        assert ref == frequencies_list_count(texts) == dict(frequencies_counter(texts)) == frequencies_setdefault(texts)
        print(f"{n:>10,} | {words:>8,} | {len(ref):>10} | {t1:>8.4f} | {t2:>10.4f} | {t3:>10.4f} | {t4:>8.4f} | {words * len(ref):>12,}")
        rows.append({"n": n, "words": words, "distinct": len(ref), "dict": round(t1, 4), "setdefault": round(t2, 4),
                     "list_count": round(t3, 4), "counter": round(t4, 4), "nd": words * len(ref)})
    tie = ["b", "a", "b", "a", "c"]
    print("\nTie-break check with the words", tie)
    print("  Counter.most_common(2):", Counter(tie).most_common(2), "<- ties stay in first-appearance order")
    print("  top(freq, 2) with key=(-count, word):", top(dict(Counter(tie)), 2), "<- alphabetical for ties")
    json.dump({"rows": rows}, open("results.json", "w"), indent=1)
