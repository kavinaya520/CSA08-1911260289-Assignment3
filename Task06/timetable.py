"""Q6: Railway timetable - nested dict/list/tuple/set, station queries with and without an index."""
import json
import random
import timeit
import tracemalloc

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
# Sample data (made up for this assignment, not the real railway timetable)
timetable = {
    12601: {"name": "Chennai - Coimbatore Express",
            "stops": [("Chennai Central", "-", "06:10"), ("Katpadi", "07:55", "07:57"), ("Salem", "10:40", "10:45"), ("Coimbatore", "13:30", "-")],
            "days": {"Mon", "Wed", "Fri", "Sun"}},
    12602: {"name": "Coimbatore - Chennai Express",
            "stops": [("Coimbatore", "-", "15:20"), ("Salem", "18:05", "18:10"), ("Katpadi", "20:50", "20:52"), ("Chennai Central", "22:40", "-")],
            "days": {"Tue", "Thu", "Sat"}},
    12635: {"name": "Chennai - Madurai Superfast",
            "stops": [("Chennai Central", "-", "21:30"), ("Trichy", "03:10", "03:15"), ("Madurai", "05:45", "-")],
            "days": set(DAYS)},
    16101: {"name": "Chennai - Salem Passenger",
            "stops": [("Chennai Central", "-", "05:30"), ("Katpadi", "08:20", "08:25"), ("Salem", "12:15", "-")],
            "days": {"Mon", "Tue", "Wed", "Thu", "Fri"}},
    22651: {"name": "Salem - Madurai Link",
            "stops": [("Salem", "-", "11:00"), ("Karur", "13:10", "13:12"), ("Trichy", "14:35", "14:40"), ("Madurai", "17:30", "-")],
            "days": {"Mon", "Fri", "Sat"}},
}


def build_index(tt):
    """Index: station -> list of train numbers that stop there."""
    index = {}
    for number, train in tt.items():
        for station, _arr, _dep in train["stops"]:
            index.setdefault(station, []).append(number)
    return index


def trains_at(tt, station, day):
    """Scan every train and every stop. Returns (list of (departure, number, name), stops examined)."""
    found, examined = [], 0
    for number, train in tt.items():
        for stop_station, arrival, departure in train["stops"]:
            examined += 1
            if stop_station == station:
                if day in train["days"]:
                    found.append((departure if departure != "-" else arrival, number, train["name"]))   # a train that ends here shows its arrival time
                break
    return sorted(found, key=lambda row: row[0]), examined


def trains_at_indexed(tt, index, station, day):
    """Use the index: look only at the trains that stop at the station. Returns (list, trains examined)."""
    found = []
    candidates = index.get(station, [])
    for number in candidates:
        train = tt[number]
        if day in train["days"]:
            arrival, departure = next((arr, dep) for st, arr, dep in train["stops"] if st == station)
            found.append((departure if departure != "-" else arrival, number, train["name"]))
    return sorted(found, key=lambda row: row[0]), len(candidates)


def flat_list(tt):
    """Alternative: one flat list of (train, station, arrival, departure, days) tuples."""
    return [(n, st, arr, dep, tr["days"]) for n, tr in tt.items() for st, arr, dep in tr["stops"]]


def trains_at_flat(flat, station, day):
    """Scan the whole flat list: examines every tuple."""
    found = [(dep if dep != "-" else arr, n, n) for n, st, arr, dep, days in flat if st == station and day in days]
    return sorted(found, key=lambda row: row[0]), len(flat)


def make_timetable(trains, seed=3, stations=200, stops=10):
    """Random timetable with `trains` trains of `stops` stops each, from `stations` station names."""
    rng = random.Random(seed)
    names = [f"ST{i:03d}" for i in range(stations)]
    tt = {}
    for t in range(trains):
        picks = rng.sample(names, stops)
        minutes = sorted(rng.sample(range(0, 1400), stops))
        stop_list = [(st, f"{m // 60:02d}:{m % 60:02d}", f"{(m + 2) // 60:02d}:{(m + 2) % 60:02d}") for st, m in zip(picks, minutes)]
        tt[10000 + t] = {"name": f"Train {10000 + t}", "stops": stop_list, "days": set(rng.sample(DAYS, rng.randint(3, 7)))}
    return tt


if __name__ == "__main__":
    print("Nested structure: timetable[train number] -> {name, stops (list of tuples), days (set)}")
    print("  departure time of the third station of train 12601: timetable[12601][\"stops\"][2][2] =", timetable[12601]["stops"][2][2])

    print("\nTimetable (sample data)")
    print(f"{'Train':<6} {'Name':<32} {'Days':<22} Stops")
    for number, train in sorted(timetable.items()):
        days = "Daily" if len(train["days"]) == 7 else ",".join(d for d in DAYS if d in train["days"])
        route = " > ".join(f"{st}({dep if dep != '-' else arr})" for st, arr, dep in train["stops"])
        print(f"{number:<6} {train['name']:<32} {days:<22} {route}")

    index = build_index(timetable)
    print("\nQuery: trains stopping at Salem on Mon, sorted by time (departure; a train that ends here shows its arrival)")
    result, examined = trains_at(timetable, "Salem", "Mon")
    result_idx, examined_idx = trains_at_indexed(timetable, index, "Salem", "Mon")
    assert result == result_idx
    for dep, number, name in result:
        print(f"  {dep}  {number}  {name}")
    print(f"  stops examined without index: {examined} | trains examined with index: {examined_idx}")

    print("\nTests")
    print("  unknown station      :", trains_at(timetable, "Atlantis", "Mon")[0], trains_at_indexed(timetable, index, "Atlantis", "Mon")[0])
    print("  train not running day: Salem on Sun ->", trains_at(timetable, "Salem", "Sun")[0], "(16101 and 22651 do not run on Sunday)")

    print("\nQueries on generated timetables (200 stations, 10 stops per train, 300 queries)")
    print(f"{'trains':>7} | {'total stops':>11} | {'no-index examined/q':>19} | {'index examined/q':>16} | {'no-index ms/q':>13} | {'index ms/q':>10} | {'flat ms/q':>9} | {'index KB':>8}")
    rows = []
    for trains in (100, 1_000, 10_000):
        tt = make_timetable(trains)
        flat = flat_list(tt)
        rng = random.Random(9)
        queries = [(f"ST{rng.randrange(200):03d}", rng.choice(DAYS)) for _ in range(300)]
        tracemalloc.start(); idx = build_index(tt); mem = tracemalloc.get_traced_memory()[0]; tracemalloc.stop()
        ex1 = sum(trains_at(tt, s, d)[1] for s, d in queries) / len(queries)
        ex2 = sum(trains_at_indexed(tt, idx, s, d)[1] for s, d in queries) / len(queries)
        for s, d in queries[:30]:
            assert trains_at(tt, s, d)[0] == trains_at_indexed(tt, idx, s, d)[0]
        t1 = min(timeit.repeat(lambda: [trains_at(tt, s, d) for s, d in queries], number=1, repeat=2)) / len(queries) * 1000
        t2 = min(timeit.repeat(lambda: [trains_at_indexed(tt, idx, s, d) for s, d in queries], number=1, repeat=2)) / len(queries) * 1000
        t3 = min(timeit.repeat(lambda: [trains_at_flat(flat, s, d) for s, d in queries], number=1, repeat=2)) / len(queries) * 1000
        print(f"{trains:>7,} | {len(flat):>11,} | {ex1:>19,.0f} | {ex2:>16.1f} | {t1:>13.4f} | {t2:>10.5f} | {t3:>9.4f} | {mem / 1024:>8,.0f}")
        rows.append({"trains": trains, "stops": len(flat), "examined": round(ex1), "examined_idx": round(ex2, 1),
                     "ms": round(t1, 4), "ms_idx": round(t2, 5), "ms_flat": round(t3, 4), "index_kb": round(mem / 1024)})
    json.dump({"rows": rows}, open("results.json", "w"), indent=1)
