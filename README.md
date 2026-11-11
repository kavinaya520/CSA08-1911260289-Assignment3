# Python Programming - Assignment 3 (CO3)

Data structures: lists, tuples, dictionaries and sets.

- Name: Kavinaya A
- Register number: 1911260289
- Python version: 3.12
- Libraries: standard library only; matplotlib (see requirements.txt) is needed only to redraw Task04/venn.png
- GitHub: https://github.com/kavinaya520/CSA08-1911260289-Assignment3.git

## How to run
Run each program from inside its folder. Saved output: output.txt / output_experiments.txt (and the .png images of them); raw counts and timings: results.json. Timings depend on the computer, counts do not.

| Task | Folder | Commands | Result note |
|---|---|---|---|
| Q1 | Task01 | `cd Task01` then `python rainfall.py` | Naive moving average 2,554,958 additions vs 365,000 for the running sum (n = 365,000), as derived |
| Q2 | Task02 | `python complete_code.py` and `python experiments.py` | Expected output matched; shared-row bug shown with is/id(); dictionary grid uses 36.1 KB instead of 7,875 KB |
| Q3 | Task03 | `python complete_code.py` and `python complaints.py` | Expected output matched; list.count() 1.44 s vs Counter 0.40 s for 100,000 complaints |
| Q4 | Task04 | `python complete_code.py`, `python electives.py`, `python make_venn.py` | Expected output matched; x in set is up to 287,001 times faster than x in list at 1,000,000 |
| Q5 | Task05 | `python sensors.py` | Three versions identical; generator uses 208 bytes against 8,448,728 bytes for the list |
| Q6 | Task06 | `python timetable.py` | Index examines about 499.7 trains per query instead of 97,753 stops (10,000 trains) |
| Q7 | Task07 | `python contacts.py` | 100,000 contacts merged in 0.2404 s; pairwise comparison would need about 6.5 minutes |

Each task folder has a README.md with the design, predictions, measurements and the alternative-concept analysis.
