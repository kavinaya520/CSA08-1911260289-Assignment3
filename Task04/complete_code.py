"""Q4 Complete the Code (TODO 1 done) - set operators only."""
ai_elective = {"192311001", "192311004", "192311007", "192311009"}
ot_elective = {"192311002", "192311004", "192311009", "192311010"}
all_students = {f"1923110{i:02d}" for i in range(1, 11)}

# TODO 1 (completed): students in both electives, in exactly one, and in neither
both = ai_elective & ot_elective
exactly_one = ai_elective ^ ot_elective
neither = all_students - (ai_elective | ot_elective)

print("clash      :", sorted(both))
print("exactly one:", sorted(exactly_one))
print("neither    :", sorted(neither))

# The same with set methods
both_m = ai_elective.intersection(ot_elective)
exactly_one_m = ai_elective.symmetric_difference(ot_elective)
neither_m = all_students.difference(ai_elective.union(ot_elective))
print("\nset methods give the same results:", both == both_m and exactly_one == exactly_one_m and neither == neither_m)
