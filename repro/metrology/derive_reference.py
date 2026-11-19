"""Derive the five reference values from the deposited caliper readings.

    python derive_reference.py

Reads reference_readings.csv and reproduces the values used in Table 3:
S00 6.05, S20 19.96, S40-A 39.97, S40-B 39.98, S60 59.97 mm.
No dependencies beyond the standard library.
"""

import csv
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "reference_readings.csv")

PAPER = {"S00": 6.05, "S20": 19.96, "S40A": 39.97, "S40B": 39.98, "S60": 59.97}


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))

    # S00 is a plate thickness, not a step
    s00 = [float(r["reading_mm"]) for r in rows
           if r["target"] == "S00" and r["measurand"] == "plate_thickness"]
    print(f"{'target':6s} {'n_read':>6s} {'base':>8s} {'total':>8s} {'step':>8s} {'paper':>7s} {'diff':>7s}")
    print("-" * 56)
    print(f"{'S00':6s} {len(s00):6d} {'-':>8s} {'-':>8s} {statistics.mean(s00):8.3f} "
          f"{PAPER['S00']:7.2f} {statistics.mean(s00) - PAPER['S00']:+7.3f}")

    for target in ("S20", "S40A", "S40B", "S60"):
        sub = [r for r in rows if r["target"] == target]
        # group by orientation group when the record carries one, else pool
        groups = sorted({r["group"] for r in sub if r["group"]})
        steps = []
        nread = 0
        if groups:
            for g in groups:
                gg = [r for r in sub if r["group"] == g]
                base = [float(r["reading_mm"]) for r in gg if r["measurand"] == "base_thickness"]
                total = [float(r["reading_mm"]) for r in gg if r["measurand"] == "total_height"]
                steps.append(statistics.mean(total) - statistics.mean(base))
                nread += len(base) + len(total)
            base_m = sum(statistics.mean([float(r["reading_mm"]) for r in sub
                                          if r["group"] == g and r["measurand"] == "base_thickness"])
                         for g in groups) / len(groups)
            total_m = sum(statistics.mean([float(r["reading_mm"]) for r in sub
                                           if r["group"] == g and r["measurand"] == "total_height"])
                          for g in groups) / len(groups)
        else:
            base = [float(r["reading_mm"]) for r in sub if r["measurand"] == "base_thickness"]
            total = [float(r["reading_mm"]) for r in sub if r["measurand"] == "total_height"]
            base_m, total_m = statistics.mean(base), statistics.mean(total)
            steps = [total_m - base_m]
            nread = len(base) + len(total)
        step = statistics.mean(steps)
        print(f"{target:6s} {nread:6d} {base_m:8.3f} {total_m:8.3f} {step:8.3f} "
              f"{PAPER[target]:7.2f} {step - PAPER[target]:+7.3f}")

    print()
    print("differences are rounding: the paper reports two decimals")


if __name__ == "__main__":
    main()
