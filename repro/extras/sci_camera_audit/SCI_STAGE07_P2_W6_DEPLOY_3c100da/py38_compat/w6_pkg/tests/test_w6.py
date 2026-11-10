"""W6 unit tests — synthetic geometry validation of the S40 measurement pipeline.

Every fixture is labelled SYNTHETIC. No test asserts anything about a real D435.
Run:  python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from w6 import core, uncertainty                      # noqa: E402
from w6.synthetic import (S40Truth, render_two_planes, quantize, add_outliers,   # noqa: E402
                          add_boundary_mixing)

INTR = core.Intrinsics(927.17, 927.367, 651.315, 349.621, 848, 480)
SHAPE = (480, 848)
STEP = 0.040


def make(z_front=0.60, step=STEP, tilt_deg=0.0, unparallel_deg=0.0, noise_mm=0.0, tag="SYNTHETIC"):
    """Two plates; `tilt_deg` rotates BOTH planes, `unparallel_deg` only the back one."""
    t = math.radians(tilt_deg)
    nf = np.array([math.sin(t), 0.0, -math.cos(t)])
    tb = math.radians(tilt_deg + unparallel_deg)
    nb = np.array([math.sin(tb), 0.0, -math.cos(tb)])
    cf = float(nf[2] * z_front)
    cb = float(cf - step)
    truth = S40Truth(tag=tag, step_m=step, front_normal=nf.tolist(), back_normal=nb.tolist(),
                     front_offset=cf, back_offset=cb, noise_sigma_mm=noise_mm, distance_m=z_front)
    return truth


def fit_pair(depth, label):
    pf = core.fit_plane(core.collect_points(label == 1, depth, INTR))
    pb = core.fit_plane(core.collect_points(label == 2, depth, INTR))
    return pf, pb


class TestSyntheticGeometry(unittest.TestCase):
    """The twelve required synthetic cases."""

    def test_01_ideal_parallel_40mm(self):
        depth, label = render_two_planes(INTR, SHAPE, make())
        pf, pb = fit_pair(depth, label)
        sep = core.plane_separation(pf, pb)
        self.assertAlmostEqual(sep["separation_m"], STEP, places=9)
        self.assertLess(pf.rms_m, 1e-9)
        self.assertAlmostEqual(sep["normal_angle_deg"], 0.0, places=6)

    def test_02_global_camera_tilt_preserves_separation(self):
        for ang in (5.0, 12.0, 25.0):
            depth, label = render_two_planes(INTR, SHAPE, make(tilt_deg=ang))
            pf, pb = fit_pair(depth, label)
            sep = core.plane_separation(pf, pb)
            self.assertAlmostEqual(sep["separation_m"], STEP, places=7,
                                   msg=f"tilt {ang} deg changed the separation")

    def test_03_roi_positions_do_not_bias_separation_but_median_difference_does(self):
        depth, label = render_two_planes(INTR, SHAPE, make(tilt_deg=10.0))
        pf, pb = fit_pair(depth, label)
        sep = core.plane_separation(pf, pb)["separation_m"]
        self.assertAlmostEqual(sep, STEP, places=7)
        # the naive estimator: difference of per-ROI median depth
        naive = abs(float(np.median(depth[label == 1])) - float(np.median(depth[label == 2])))
        self.assertGreater(abs(naive - STEP), 1e-3,
                           "the naive median-Z difference should be visibly biased at 10 deg")

    def test_04_small_unparallelism_reports_angle_and_reference_dependence(self):
        depth, label = render_two_planes(INTR, SHAPE, make(tilt_deg=0.0, unparallel_deg=0.5))
        pf, pb = fit_pair(depth, label)
        sep = core.plane_separation(pf, pb)
        self.assertAlmostEqual(sep["normal_angle_deg"], 0.5, delta=1e-3)
        sens = core.separation_sensitivity(pf, pb)
        self.assertGreater(sens["spread_over_40mm_window_m"], 0.0,
                           "non-parallel planes must show reference-point dependence")

    def test_05_random_depth_noise(self):
        rng = np.random.default_rng(7)
        truth = make(noise_mm=0.5)
        depth, label = render_two_planes(INTR, SHAPE, truth, rng=rng)
        pf, pb = fit_pair(depth, label)
        sep = core.plane_separation(pf, pb)["separation_m"]
        self.assertLess(abs(sep - STEP), 0.0005, "0.5 mm noise must not move the step by >0.5 mm")
        self.assertLess(pf.rms_m, 0.001)

    def test_06_quantization_error_bounded(self):
        depth, label = render_two_planes(INTR, SHAPE, make())
        raw = quantize(depth, 0.001)
        dm = core.depth_to_metres(raw, 0.001)
        pf, pb = fit_pair(dm, label)
        sep = core.plane_separation(pf, pb)["separation_m"]
        self.assertLessEqual(abs(sep - STEP), 0.0005)      # <= half a quantisation step

    def test_07_zero_and_invalid_pixels(self):
        depth, label = render_two_planes(INTR, SHAPE, make())
        depth = depth.copy()
        depth[100:140, 100:140] = 0.0
        depth[200:210, 500:560] = np.nan
        raw = quantize(depth, 0.001)
        dm = core.depth_to_metres(raw, 0.001)
        pf, pb = fit_pair(dm, label)
        self.assertAlmostEqual(core.plane_separation(pf, pb)["separation_m"], STEP, places=7)
        roi = core.ROI("front", [(150, 120), (450, 120), (450, 380), (150, 380)])
        mask = core.polygon_mask(dm.shape, roi.polygon)
        st = core.roi_stats(mask, dm, roi)
        self.assertLessEqual(st["valid_ratio"], 1.0)
        self.assertTrue(0.0 <= st["valid_ratio"] <= 1.0)

    def test_08_local_outliers_bias_is_visible_in_rms(self):
        rng = np.random.default_rng(11)
        depth, label = render_two_planes(INTR, SHAPE, make())
        clean = fit_pair(depth, label)
        dirty_d = add_outliers(depth, 4, rng, patch=14, delta_mm=25.0)
        dirty = fit_pair(dirty_d, label)
        self.assertGreater(dirty[0].rms_m, clean[0].rms_m + 1e-4,
                           "a 25 mm local bias must show up in the fit RMS")

    def test_09_boundary_mixing_and_erosion(self):
        depth, label = render_two_planes(INTR, SHAPE, make())
        mixed = add_boundary_mixing(depth, px=3)
        changed = int((np.abs(mixed - depth) > 1e-9).sum())
        self.assertGreater(changed, 0)
        m = np.zeros(SHAPE, bool); m[200:280, 300:400] = True
        self.assertLessEqual(int(core.erode(m, 3).sum()), int(m.sum()))

    def test_10_small_visible_area_fails_the_gate(self):
        truth = make()
        depth, label = render_two_planes(INTR, SHAPE, truth, front_size=0.02, back_size=0.02)
        n_front = int((label == 1).sum())
        self.assertLess(n_front, 2000)
        roi = core.ROI("front", [(0, 0), (847, 0), (847, 479), (0, 479)], min_valid_ratio=0.90)
        st = core.roi_stats(core.polygon_mask(depth.shape, roi.polygon), depth, roi)
        self.assertFalse(st["ok"], "a mostly-empty ROI must fail the validity gate")

    def test_11_wrong_depth_scale_is_detectable(self):
        depth, label = render_two_planes(INTR, SHAPE, make())
        raw = quantize(depth, 0.001)
        correct = core.depth_to_metres(raw, 0.001)
        wrong = core.depth_to_metres(raw, 0.002)
        s_correct = core.plane_separation(*fit_pair(correct, label))["separation_m"]
        s_wrong = core.plane_separation(*fit_pair(wrong, label))["separation_m"]
        self.assertAlmostEqual(s_correct, STEP, places=5)
        self.assertAlmostEqual(s_wrong / s_correct, 2.0, places=4,
                               msg="depth_scale errors scale the step linearly and must be recorded")

    def test_12_target_distance_does_not_change_the_step(self):
        for z in (0.35, 0.50, 0.70, 0.90):
            depth, label = render_two_planes(INTR, SHAPE, make(z_front=z))
            sep = core.plane_separation(*fit_pair(depth, label))["separation_m"]
            self.assertAlmostEqual(sep, STEP, places=6, msg=f"distance {z} m changed the step")


class TestEngineering(unittest.TestCase):
    """CLI-facing components: ROI config, intrinsics, uncertainty, schema, worksheet."""

    def test_roi_roundtrip_and_hash(self):
        roi = core.ROI("FRONT_PLANE_ROI", [(10, 20), (100, 20), (100, 200), (10, 200)], 3, 0.6)
        same = core.ROI.from_json(json.loads(json.dumps(roi.to_json())))
        self.assertEqual(roi.sha256(), same.sha256())
        other = core.ROI("FRONT_PLANE_ROI", [(10, 20), (101, 20), (100, 200), (10, 200)], 3, 0.6)
        self.assertNotEqual(roi.sha256(), other.sha256())

    def test_intrinsics_validation(self):
        INTR.validate()
        with self.assertRaises(ValueError):
            core.Intrinsics(0.0, 927.0, 651.0, 349.0).validate()      # fx must be > 0
        with self.assertRaises(ValueError):
            core.Intrinsics(927.0, float("nan"), 651.0, 349.0).validate()  # non-finite

    def test_depth_scale_rejects_nonpositive(self):
        with self.assertRaises(ValueError):
            core.depth_to_metres(np.ones((2, 2), np.uint16), 0.0)

    def test_within_and_between_placement_variability(self):
        w = uncertainty.within_placement([0.0400, 0.0401, 0.0399, 0.0402])
        self.assertEqual(w["n"], 4)
        self.assertGreater(w["std_m"], 0)
        b = uncertainty.between_placement([0.0400, 0.0402, 0.0398, 0.0401, 0.0403])
        self.assertEqual(b["n"], 5)
        self.assertFalse(uncertainty.between_placement([0.04])["std_m"] ==
                         uncertainty.between_placement([0.04])["std_m"])  # NaN != NaN

    def test_combine_u95_unknown_propagates(self):
        r = uncertainty.combine_u95({"instrument": 0.05, "repeatability": 0.02,
                                     "parallelism": "UNKNOWN"})
        self.assertEqual(r["u95_mm"], "UNKNOWN")
        self.assertIn("parallelism", r["unknown_components"])
        r2 = uncertainty.combine_u95({"a": 0.03, "b": 0.04})
        self.assertAlmostEqual(r2["u95_mm"], 2 * math.hypot(0.03, 0.04), places=9)

    def test_reference_worksheet_incomplete_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "ref.csv"
            p.write_text("placement_id,reading_mm,instrument_model,instrument_resolution_mm,operator,date\n"
                         "P1,40.01,,,,P1,40.02,,,,\n", encoding="utf-8")
            rep = uncertainty.validate_reference_rows(uncertainty.read_reference_rows(p))
            self.assertFalse(rep["complete"])
            self.assertGreater(rep["n_problems"], 0)

    def test_schema_check_reports_missing(self):
        with tempfile.TemporaryDirectory() as td:
            rep = uncertainty.check_placement_dir(td)
            self.assertFalse(rep["complete"])
            self.assertFalse(rep["camera_intrinsics"]["present"])

    def test_placement_layout_has_five(self):
        lay = uncertainty.placement_layout("X")
        self.assertEqual(len(lay), 5)
        self.assertIn("placement_05", lay)


if __name__ == "__main__":
    unittest.main(verbosity=2)
