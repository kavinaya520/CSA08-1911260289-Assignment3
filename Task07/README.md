# Q7 - Design a Contact-Merging Program from First Principles

Run: `python contacts.py` (output in output.txt, raw numbers in results.json).

## Stage 1 - Interpret the problem
- Input: contacts from two phones and a SIM; each has a name (maybe empty), zero or more numbers in different formats and zero or more e-mail addresses, and the source.
- Output: one record per person with the best name, a set of all numbers, a set of all e-mails and the name variants.
- Rule for the same person: two contacts are the same person if they share a normalised mobile number (and, only for a contact with no usable number, a normalised e-mail). The name is NOT used to decide, because
  names are spelt differently ("Dr. Ravi", "ravi kumar") and different people can have the same name. A contact that shares a number with two groups joins them (so merging is transitive).
- Data structures: dictionary key -> first contact that had the key (O(1) lookup); sets for numbers, e-mails and name variants (no duplicates); a list of contacts; union-find (parent list) to join contacts.
- Measurable requirements: (R1) "+91 98400 12345", "9840012345" and "098400-12345" give the same key; (R2) every contact appears in exactly one merged record; (R3) two contacts with different numbers and the same name stay separate;
  (R4) no number or e-mail is lost; (R5) 100,000 contacts are merged in well under a second, in time proportional to n.

## Stage 2 - Design
Number normalisation: keep only the digits; if there are at least 10 take the last 10 (this removes +91 and a leading 0); accept it only if it starts with 6, 7, 8 or 9 (a mobile number), otherwise there is no usable key.
Name normalisation: lower case, punctuation to spaces, remove titles (dr, mr, mrs, ms, prof, ...), single spaces. Display name: the longest name variant.

    FUNCTION merge(contacts)
        owner = empty dictionary; parent[i] = i for every contact i
        FOR i = 0 .. n-1
            keys = normalised numbers of contact i
            IF keys is empty THEN keys = normalised e-mails of contact i
            FOR EACH key IN keys
                IF key IN owner THEN join(owner[key], i)     # same person
                ELSE owner[key] = i
        group the contacts by find(i)
        FOR EACH group: numbers = SET of all numbers, emails = SET of all e-mails, names = SET of name variants
        RETURN the records

## Stage 3 - Implement and measure
`contacts.py` implements the design. Tests (output.txt): duplicates in five number formats, missing name, missing number (merged by e-mail or kept alone), invalid number `12345`, a contact that joins two others (Ravi's second number), two different "Anitha".
Hand check of the 9-contact list: contacts 0, 1 and 2 are Ravi (0 and 1 share 9840012345, 1 and 2 share 9840054321) -> one record with numbers {9840012345, 9840054321}, e-mail {ravi@mail.com}; every other contact stays alone (7 records); the program gives exactly this (asserted).

| Contacts | Dictionary design (s) | Dictionary lookups | Pairwise (s) | Pair comparisons | Records after merging |
|---|---|---|---|---|---|
| 1,000 | 0.0019 | 979 | 0.04 | 499,500 | 720 |
| 100,000 | 0.2404 | 97,455 | about 5.9 min (estimated) | 4,999,950,000 | 72,483 |

Pairwise comparison grows with n squared (measured):

| n | Pairwise (s) | Dictionary (s) | Pair comparisons |
|---|---|---|---|
| 500 | 0.0081 | 0.00087 | 124,750 |
| 1000 | 0.0354 | 0.0018 | 499,500 |
| 2000 | 0.1491 | 0.00345 | 1,999,000 |
| 4000 | 0.6195 | 0.00737 | 7,998,000 |

## Stage 4 - Defend the design
- A dictionary is better than comparing every pair because each contact needs only one lookup per key (O(1) average), so the work is O(n) and about 97,000 lookups handled 100,000 contacts in 0.2404 s; comparing pairs needs n(n - 1)/2 = 4,999,950,000 comparisons for 100,000 contacts (about 6.5 minutes by extrapolation of the measured 4,000-contact rate).
- Two different people with the same name: the name is not used as a key, so "Anitha" with 90000 00001 and "Anitha" with 90000 00002 remain two records (tested).
- Limitation: people who share a number (a family landline or one shared mobile) are merged wrongly, a contact with no number and no e-mail can never be matched ("Meena S" and "Meena S." stay separate), and landline numbers are not used as keys.

## Alternative concept: compare every pair
Time O(n^2) against O(n) on average for the dictionary: 1,000 contacts took 0.04 s against 0.0019 s; at 100,000 contacts the pairwise method is impractical (estimated 6.5 minutes against 0.2404 s).
Space: the dictionary needs O(n) for the keys; the pairwise method needs O(n) for the stored key sets and nothing else, so it saves the dictionary but not much (the data itself is O(n)).
Both give identical groups (asserted for 1,000 contacts).
