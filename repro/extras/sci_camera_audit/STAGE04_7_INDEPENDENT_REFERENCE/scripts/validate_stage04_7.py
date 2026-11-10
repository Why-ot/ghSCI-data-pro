#!/usr/bin/env python3
"""Read-only consistency validator for the STAGE04.7 materialized protocol."""

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRS = {
    "protocol",
    "hardware",
    "reference_measurements",
    "raw_capture",
    "results",
    "reports",
    "scripts",
}
EXPECTED_FILES = {
    "protocol/PROTOCOL_FREEZE_v1.0.md",
    "hardware/STATIC_EXPERIMENT_SAFETY.md",
    "EQUIPMENT_REGISTER.csv",
    "REFERENCE_MEASUREMENT_SHEET.csv",
    "EXPERIMENT_MANIFEST.csv",
    "CAMERA_PROFILE_REQUIREMENTS.json",
    "PILOT_CAPTURE_PLAN.csv",
    "reports/FILE_SHA256SUMS.txt",
    "reports/STAGE04_7_STEP1_REPORT.md",
}


def read_csv(relative_path):
    with (ROOT / relative_path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main():
    missing_dirs = sorted(name for name in EXPECTED_DIRS if not (ROOT / name).is_dir())
    missing_files = sorted(name for name in EXPECTED_FILES if not (ROOT / name).is_file())
    assert not missing_dirs, f"missing directories: {missing_dirs}"
    assert not missing_files, f"missing files: {missing_files}"

    manifest = read_csv("EXPERIMENT_MANIFEST.csv")
    assert len(manifest) == 135, len(manifest)
    ids = [row["experiment_id"] for row in manifest]
    assert len(ids) == len(set(ids)), "duplicate experiment_id"
    assert {row["step_target"] for row in manifest} == {"S20", "S40", "S60"}
    assert {row["distance_mm"] for row in manifest} == {"400", "600", "800"}
    assert {row["position"] for row in manifest} == {"CENTER", "LEFT", "RIGHT"}
    assert {row["repeat_id"] for row in manifest} == {"1", "2", "3", "4", "5"}
    assert {row["planned_frames"] for row in manifest} == {"30"}
    assert {row["actual_frames"] for row in manifest} == {""}
    assert {row["camera_serial"] for row in manifest} == {"317422072133"}
    assert {row["status"] for row in manifest} == {"PLANNED"}
    assert sum(int(row["planned_frames"]) for row in manifest) == 4050

    reference = read_csv("REFERENCE_MEASUREMENT_SHEET.csv")
    assert len(reference) == 45, len(reference)
    assert all(row["measured_mm"] == "" for row in reference)
    assert {row["status"] for row in reference} == {"PLANNED"}

    pilot = read_csv("PILOT_CAPTURE_PLAN.csv")
    assert len(pilot) == 5, len(pilot)
    assert all(row["step_target"] == "S40" for row in pilot)
    assert all(row["distance_mm"] == "600" for row in pilot)
    assert all(row["position"] == "CENTER" for row in pilot)
    assert all(row["status"] == "PLANNED" for row in pilot)

    with (ROOT / "CAMERA_PROFILE_REQUIREMENTS.json").open(encoding="utf-8") as handle:
        profile = json.load(handle)
    assert profile["camera"]["serial"] == "317422072133"
    assert profile["requested_depth_profile"] == {
        "width": 848,
        "height": 480,
        "format": "Z16",
        "fps": 30,
    }
    assert profile["depth_postprocessing"] == "OFF"
    assert profile["capture_authorized_by_this_file"] is False

    print("VALIDATION_STATUS=PASS")
    print(f"EXPERIMENT_MANIFEST_ROWS={len(manifest)}")
    print("UNIQUE_EXPERIMENT_IDS=PASS")
    print("PLANNED_TOTAL_FRAMES=4050")
    print(f"REFERENCE_TEMPLATE_ROWS={len(reference)}")
    print(f"PILOT_PLAN_ROWS={len(pilot)}")
    print("JSON_PARSE=PASS")
    print("DIRECTORY_STRUCTURE=PASS")
    for relative_path in sorted(EXPECTED_FILES):
        data = (ROOT / relative_path).read_bytes()
        print(f"SHA256 {hashlib.sha256(data).hexdigest()}  {relative_path}")


if __name__ == "__main__":
    main()
