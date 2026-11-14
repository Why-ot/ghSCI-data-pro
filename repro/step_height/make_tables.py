"""Rebuild Tables 7, 8 and 9 from the per-unit ensemble.

Aggregation is the mean over placement units, as equation (6) of the paper defines the
primary endpoint. The median is printed alongside because the two differ by up to
0.23 mm in the row with the widest placement spread, which is worth knowing but is not
the reported statistic.

Anchor policy is the one implemented in measure_eh.py and stated in Section 6.1: 5.85 mm
for every session at the 355 mm standoff, re-measured from the flat-control units at
each new standoff.
"""

import csv
import io
import statistics as st
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ENS = r"C:\Users\lqx\Desktop\论文\_join\ensemble\ensemble_per_unit.csv"
REF = {"S00": 6.05, "S20": 19.96, "S40A": 39.97, "S40B": 39.98, "S60": 59.97}
rows = list(csv.DictReader(open(ENS, encoding="utf-8")))


def vals(ds, part, key=None):
    return [float(r["e_h_mm"]) for r in rows
            if r["dataset"] == ds and r["part"] == part
            and (key is None or key in r["unit"])]


def summary(ds, part, key=None):
    v = vals(ds, part, key)
    return {"n": len(v), "mean": st.mean(v), "median": st.median(v), "sd": st.stdev(v)}


print("Table 7 -- first session (live2), 355 mm\n")
print(f"{'target':14s} {'n':>2s} {'ref':>6s} {'mean':>7s} {'bias':>6s} {'SD_rep':>7s} {'median':>7s}")
for name, part, key in (("S00 flat", "S00", None), ("S20", "S20", None),
                        ("S40-A 0deg", "S40A", "_0deg_"), ("S40-A 180deg", "S40A", "_180deg_"),
                        ("S40-B black", "S40B", None), ("S60", "S60", None)):
    c = summary("live2", part, key)
    print(f"{name:14s} {c['n']:2d} {REF[part]:6.2f} {c['mean']:7.2f} {c['mean']-REF[part]:+6.2f} "
          f"{c['sd']:7.3f} {c['median']:7.2f}")

print("\nTable 8 -- second session (live3), 355 mm\n")
print(f"{'target':14s} {'n':>2s} {'mean':>7s} {'SD':>6s} {'vs s1':>7s} {'median':>7s}")
for name, part, key in (("S00 thick", "S00", None), ("S20", "S20", None),
                        ("S40-A 0deg", "S40A", "_0deg_"), ("S40-A 180deg", "S40A", "_180deg_"),
                        ("S40-B black", "S40B", None), ("S60", "S60", None)):
    c = summary("live3", part, key)
    b = summary("live2", part, key)
    print(f"{name:14s} {c['n']:2d} {c['mean']:7.2f} {c['sd']:6.3f} {c['mean']-b['mean']:+7.2f} {c['median']:7.2f}")

print("\nTable 9 -- standoff, 60 mm target\n")
print(f"{'condition':16s} {'standoff':>8s} {'n':>2s} {'mean':>7s} {'bias':>6s} {'SD':>6s} {'median':>7s}")
for name, ds, so in (("Session 1", "live2", 355), ("Session 2", "live3", 355),
                     ("Standoff A", "live4_d350", 376), ("Standoff B", "live4_d450", 448)):
    c = summary(ds, "S60")
    print(f"{name:16s} {so:8d} {c['n']:2d} {c['mean']:7.2f} {c['mean']-REF['S60']:+6.2f} "
          f"{c['sd']:6.3f} {c['median']:7.2f}")

print("\nNote: the 448 mm row has SD 1.32 mm across its five placements and moves by")
print("0.64 mm between RANSAC seeds; it supports the direction of the range effect but")
print("not its magnitude to better than about a millimetre.")
