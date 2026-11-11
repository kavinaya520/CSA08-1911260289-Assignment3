# Q6 - Nested Data: A Railway Timetable

Run: `python timetable.py` (output in output.txt, raw numbers in results.json). The five trains are sample data made for this assignment, not the real timetable.

## Structure
    timetable = { train_number: { "name": str,
                                  "stops": [ (station, arrival, departure), ... ],     # list of tuples
                                  "days": {"Mon", "Wed", ...} } }                    # set

Departure time of the third station of train 12601: `timetable[12601]["stops"][2][2]` = 10:45.
- dictionary for the train number: direct access by number; list for the stops: they have an order; tuple for one stop: a fixed record (station, arrival, departure) that must not change;
  set for the running days: only "does it run on this day" matters (no order, no repeated days, fast `in`).

## Station query
`trains_at(timetable, station, day)` examines the stops of the trains, keeps the trains that stop at the station and run on the day, and sorts them with `sorted(found, key=lambda row: row[0])` by time
(departure; a train that ends at the station shows its arrival time). Example (Salem, Monday): 10:45 train 12601, 11:00 train 22651, 12:15 train 16101. The timetable is printed neatly by the program.

Work for one query without an index: the program looks at the stops of all T trains, about T x s stops for s stops per train (total stops). With an index `station -> list of train numbers` the query looks only at the k trains
that stop at the station: O(k) where k is about (T x s) / (number of stations).

## Tests
Unknown station gives `[]`; a train that does not run on the day is not listed (Salem on Sunday lists only 12601); the indexed and scanning versions give the same answers (asserted for generated data).

## Experiment: 100, 1,000 and 10,000 trains (200 stations, 10 stops per train, 300 queries)

| Trains | Total stops | Stops examined per query (no index) | Trains examined per query (index) | No index (ms/query) | Index (ms/query) | Flat list (ms/query) | Index memory (KB) |
|---|---|---|---|---|---|---|---|
| 100 | 1,000 | 977 | 5.2 | 0.0551 | 0.00283 | 0.0222 | 28 |
| 1,000 | 10,000 | 9,776 | 50.0 | 0.4118 | 0.02783 | 0.2241 | 100 |
| 10,000 | 100,000 | 97,753 | 499.7 | 4.1728 | 0.48164 | 2.5408 | 846 |

## Conclusion
The index is built once (one pass over all stops) and answers each query by going straight to the trains of one station, so the work per query falls from about 100,000 stops to about 500 trains at 10,000 trains (about nine times less time per query at 10,000 trains in these runs).
Trade-off: extra memory (846 KB for 10,000 trains), the index must be updated whenever the timetable changes, and it only helps the question it was designed for.

## Alternative concept: one flat list of tuples scanned for every query
`(train, station, arrival, departure, days)` tuples: time per query O(total stops) (every tuple is examined), space O(total stops) with the train data repeated in every tuple. The nested dictionaries with an index need
O(trains at the station) time per query and O(total stops) extra space for the index. Measured per query at 10,000 trains: flat list 2.5408 ms, nested scan 4.1728 ms, index 0.48164 ms.
