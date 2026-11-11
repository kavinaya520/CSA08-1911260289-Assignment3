"""Q7: Merging phone contacts - design from first principles (dictionary keyed by normalised number)."""
import json
import random
import timeit

TITLES = {"dr", "mr", "mrs", "ms", "prof", "shri", "smt", "sri"}
DIGITS = "0123456789"


def normalise_number(raw):
    """'+91 98400 12345', '098400-12345', '9840012345' -> '9840012345'. None if it is not a 10-digit mobile number."""
    digits = "".join(ch for ch in raw if ch in DIGITS)
    if len(digits) < 10:
        return None
    last10 = digits[-10:]                      # drops +91 and a leading 0
    return last10 if last10[0] in "6789" else None


def normalise_name(raw):
    """'Dr. Ravi' -> 'ravi'; 'ravi  kumar' -> 'ravi kumar' (lower case, no punctuation, no titles)."""
    cleaned = "".join(ch if ch.isalnum() else " " for ch in raw.lower())
    return " ".join(w for w in cleaned.split() if w not in TITLES)


def keys_of(contact):
    """Keys that identify a person: the normalised numbers; the e-mails only if no usable number exists."""
    numbers = [("tel", n) for n in map(normalise_number, contact["numbers"]) if n]
    if numbers:
        return numbers
    return [("mail", e.strip().lower()) for e in contact["emails"] if e.strip()]


def groups_dictionary(contacts):
    """Group contact indices with ONE dictionary (key -> first contact with that key) and union-find. O(n) average."""
    parent = list(range(len(contacts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    owner, lookups = {}, 0
    for i, contact in enumerate(contacts):
        for key in keys_of(contact):
            lookups += 1
            if key in owner:
                ra, rb = find(owner[key]), find(i)
                if ra != rb:
                    parent[rb] = ra
            else:
                owner[key] = i
    groups = {}
    for i in range(len(contacts)):
        groups.setdefault(find(i), []).append(i)
    return sorted(tuple(g) for g in groups.values()), lookups


def groups_pairwise(contacts):
    """Compare every pair of contacts: n(n-1)/2 comparisons."""
    key_sets = [set(keys_of(c)) for c in contacts]
    parent = list(range(len(contacts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comparisons = 0
    for i in range(len(contacts)):
        for j in range(i + 1, len(contacts)):
            comparisons += 1
            if not key_sets[i].isdisjoint(key_sets[j]):
                ra, rb = find(i), find(j)
                if ra != rb:
                    parent[rb] = ra
    groups = {}
    for i in range(len(contacts)):
        groups.setdefault(find(i), []).append(i)
    return sorted(tuple(g) for g in groups.values()), comparisons


def build_records(contacts, groups):
    """One record per person: sets of numbers and e-mails, all name variants, best display name."""
    records = []
    for group in groups:
        names, numbers, emails = set(), set(), set()
        for i in group:
            c = contacts[i]
            if normalise_name(c["name"]):
                names.add(normalise_name(c["name"]))
            numbers.update(n for n in map(normalise_number, c["numbers"]) if n)
            emails.update(e.strip().lower() for e in c["emails"] if e.strip())
        display = max(names, key=len).title() if names else "(no name)"
        records.append({"name": display, "variants": sorted(names), "numbers": sorted(numbers), "emails": sorted(emails), "merged": len(group)})
    return sorted(records, key=lambda r: (r["name"], r["numbers"]))


FIRST = ["Ravi", "Anitha", "Meena", "Karthik", "Priya", "Suresh", "Divya", "Arun", "Lakshmi", "Vijay", "Kavitha", "Mohan"]
LAST = ["Kumar", "S", "Raj", "Devi", "Nair", "Iyer", "Pillai", "Babu"]


def fmt_number(num, rng):
    """Write a 10-digit number in one of five formats."""
    return rng.choice([num, f"+91 {num[:5]} {num[5:]}", f"+91-{num}", f"0{num}", f"{num[:5]} {num[5:]}"])


def make_contacts(n, seed=21):
    """n contacts from three sources; about 30% are repeats of a person in another format; some fields missing."""
    rng = random.Random(seed)
    people = []
    contacts = []
    while len(contacts) < n:
        if people and rng.random() < 0.30:
            p = rng.choice(people)
        else:
            p = {"name": f"{rng.choice(FIRST)} {rng.choice(LAST)}", "num": str(rng.randrange(6_000_000_000, 10_000_000_000)),
                 "mail": f"user{len(people)}@example.com"}
            people.append(p)
        name = rng.choice([p["name"], "Dr. " + p["name"], p["name"].lower(), p["name"].split()[0], ""] if rng.random() < 0.9 else [""])
        contacts.append({"name": name, "numbers": [fmt_number(p["num"], rng)] if rng.random() < 0.95 else [],
                         "emails": [p["mail"]] if rng.random() < 0.5 else [], "source": rng.choice(["phone1", "phone2", "sim"])})
    return contacts


if __name__ == "__main__":
    print("Normalisation examples")
    for raw in ["+91 98400 12345", "9840012345", "098400-12345", "(0)98400 12345", "98400 12345", "12345", "044 2345 6789"]:
        print(f"  {raw!r:20} -> {normalise_number(raw)}")
    for raw in ["Dr. Ravi", "ravi   kumar", "RAVI KUMAR", "Meena S."]:
        print(f"  {raw!r:20} -> {normalise_name(raw)!r}")

    small = [
        {"name": "Dr. Ravi", "numbers": ["+91 98400 12345"], "emails": [], "source": "phone1"},
        {"name": "ravi kumar", "numbers": ["9840012345", "98400-54321"], "emails": ["ravi@mail.com"], "source": "phone2"},
        {"name": "Ravi Kumar", "numbers": ["098400 54321"], "emails": ["RAVI@mail.com"], "source": "sim"},
        {"name": "Anitha", "numbers": ["90000 00001"], "emails": [], "source": "phone1"},
        {"name": "Anitha", "numbers": ["90000 00002"], "emails": [], "source": "phone2"},
        {"name": "", "numbers": [], "emails": ["lone@x.com"], "source": "sim"},
        {"name": "Meena S", "numbers": [], "emails": [], "source": "sim"},
        {"name": "Meena S.", "numbers": ["+91-77000 11111"], "emails": [], "source": "phone1"},
        {"name": "Test", "numbers": ["12345"], "emails": [], "source": "sim"},
    ]
    groups, lookups = groups_dictionary(small)
    print(f"\nSmall list of {len(small)} contacts merged by hand (expected) vs program")
    expected = [(0, 1, 2), (3,), (4,), (5,), (6,), (7,), (8,)]
    print("  by hand : 0,1,2 are Ravi (shared numbers 9840012345 and 9840054321); every other contact stays alone")
    print("  program :", groups)
    assert groups == expected == groups_pairwise(small)[0]
    for r in build_records(small, groups):
        print(f"  {r['name']:<12} merged {r['merged']} | numbers {r['numbers']} | emails {r['emails']} | name variants {r['variants']}")
    print("  two different Anitha stay separate (different numbers); Meena S (no number) is not merged with Meena S.")
    print("  the contact with the invalid number '12345' is kept alone (no usable key)")

    print("\nTime for the dictionary design and for comparing every pair")
    print(f"{'contacts':>9} | {'dictionary s':>12} | {'lookups':>9} | {'pairwise s':>11} | {'pair comparisons':>16} | {'records':>8}")
    rows = []
    per_pair = None
    for n in (1_000, 100_000):
        data = make_contacts(n)
        t_dict = min(timeit.repeat(lambda: groups_dictionary(data), number=1, repeat=3))
        g, lk = groups_dictionary(data)
        if n == 1_000:
            t_pair = min(timeit.repeat(lambda: groups_pairwise(data), number=1, repeat=2))
            g2, cmp = groups_pairwise(data)
            assert g == g2
            per_pair = t_pair / cmp
            pair_txt, est = f"{t_pair:.4f}", False
        else:
            cmp = n * (n - 1) // 2
            t_pair = per_pair * cmp
            pair_txt, est = f"~{t_pair / 60:.1f} min (est.)", True
        print(f"{n:>9,} | {t_dict:>12.4f} | {lk:>9,} | {pair_txt:>11} | {cmp:>16,} | {len(g):>8,}")
        rows.append({"n": n, "dict_s": round(t_dict, 4), "lookups": lk, "pair_s": round(t_pair, 2), "pair_estimated": est,
                     "comparisons": cmp, "records": len(g)})
    print("  (the pairwise time for 100,000 contacts is the measured time per comparison at 1,000 contacts x 4,999,950,000 comparisons)")
    print("\nPairwise comparison measured for growing n (shows the n squared growth)")
    growth = []
    for n in (500, 1_000, 2_000, 4_000):
        data = make_contacts(n, seed=4)
        t = min(timeit.repeat(lambda: groups_pairwise(data), number=1, repeat=1))
        td = min(timeit.repeat(lambda: groups_dictionary(data), number=1, repeat=3))
        cmp = n * (n - 1) // 2
        print(f"  n = {n:>5}: pairwise {t:.4f} s ({cmp:,} comparisons) | dictionary {td:.5f} s")
        growth.append({"n": n, "pair_s": round(t, 4), "dict_s": round(td, 5), "comparisons": cmp})
    est = growth[-1]["pair_s"] / growth[-1]["comparisons"] * (100_000 * 99_999 // 2)
    print(f"  estimate for 100,000 contacts at the rate measured for 4,000: about {est / 60:.1f} minutes of pairwise comparison, "
          f"against {rows[1]['dict_s']} s for the dictionary")
    json.dump({"rows": rows, "growth": growth, "per_pair_us": round(per_pair * 1e6, 4), "est_100k_min": round(est / 60, 1)}, open("results.json", "w"), indent=1)
