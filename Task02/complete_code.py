"""Q2 Complete the Code (TODO 1 done)."""
rows, cols = 3, 4
bad = [[0] * cols] * rows      # every row is the SAME list object
bad[0][1] = 7

# TODO 1 (completed): a rows x cols grid of zeros in which every row is a separate list
good = [[0] * cols for _ in range(rows)]

good[0][1] = 7
print("bad :", bad)
print("good:", good)

print(bad[0] is bad[1], good[0] is good[1])

# Tuples are immutable, so they can be used as dictionary keys
stops = {(13.0827, 80.2707): "Chennai Central", (13.0418, 80.2341): "T. Nagar"}
print(stops[(13.0418, 80.2341)])
