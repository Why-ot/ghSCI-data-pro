"""W6 core geometry: Z16 depth I/O, back-projection, 3D plane fitting, plane separation, ROI.

All quantities are SI (metres) unless a name says otherwise. The camera frame is the RealSense optical
frame: x right, y down, z forward (the Z axis *is* the optical-axis depth, not a Euclidean range).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

# --------------------------------------------------------------------------------------------- depth I/O


@dataclass
class Intrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    width: int | None = None
    height: int | None = None

    def validate(self) -> None:
        for name in ("fx", "fy", "cx", "cy"):
            v = getattr(self, name)
            if not np.isfinite(v) or v <= 0:
                raise ValueError(f"invalid intrinsic {name}={v}")
        if self.fx <= 0 or self.fy <= 0:
            raise ValueError("focal lengths must be positive")

    @classmethod
    def from_json(cls, path: str | Path) -> "Intrinsics":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(float(d["fx"]), float(d["fy"]), float(d["cx"]), float(d["cy"]),
                   d.get("width"), d.get("height"))

    def to_json(self) -> dict:
        return {"fx": self.fx, "fy": self.fy, "cx": self.cx, "cy": self.cy,
                "width": self.width, "height": self.height}


def read_depth_z16(path: str | Path, width: int, height: int) -> np.ndarray:
    """Read a headerless little-endian uint16 depth frame as a (h, w) array of raw units."""
    raw = np.frombuffer(Path(path).read_bytes(), dtype="<u2")
    if raw.size != width * height:
        raise ValueError(f"{path}: expected {width*height} uint16, got {raw.size}")
    return raw.reshape(height, width)


def depth_to_metres(raw: np.ndarray, depth_scale: float) -> np.ndarray:
    """Convert raw units to metres; 0 means 'no measurement' and stays 0."""
    if not np.isfinite(depth_scale) or depth_scale <= 0:
        raise ValueError(f"depth_scale must be positive, got {depth_scale}")
    return raw.astype(np.float64) * float(depth_scale)


def valid_mask(depth_m: np.ndarray) -> np.ndarray:
    """A pixel is valid iff it carries a finite, strictly positive depth."""
    return np.isfinite(depth_m) & (depth_m > 0)


def backproject(depth_m: np.ndarray, intr: Intrinsics) -> np.ndarray:
    """(h, w, 3) point cloud in metres. Invalid pixels become NaN."""
    h, w = depth_m.shape
    vv, uu = np.mgrid[0:h, 0:w]
    z = depth_m
    x = (uu - intr.cx) / intr.fx * z
    y = (vv - intr.cy) / intr.fy * z
    pts = np.stack([x, y, z], axis=-1)
    pts[~valid_mask(depth_m)] = np.nan
    return pts


# ------------------------------------------------------------------------------------------ plane fitting


@dataclass
class PlaneFit:
    normal: np.ndarray          # unit normal, oriented so that normal.z < 0 (points toward the camera)
    centroid: np.ndarray        # mean of the fitted points
    offset: float               # c in  n . x = c
    rms_m: float                # root-mean-square point-to-plane distance
    n_points: int
    singular_values: np.ndarray

    def distance(self, points: np.ndarray) -> np.ndarray:
        return points @ self.normal - self.offset


def fit_plane(points: np.ndarray, min_points: int = 50) -> PlaneFit:
    """Total-least-squares plane through 3D points (NaN rows ignored)."""
    pts = np.asarray(points, dtype=np.float64)
    pts = pts[np.isfinite(pts).all(axis=1)]
    if pts.shape[0] < min_points:
        raise ValueError(f"need >= {min_points} finite points, got {pts.shape[0]}")
    centroid = pts.mean(axis=0)
    centred = pts - centroid
    _, sv, vt = np.linalg.svd(centred, full_matrices=False)
    n = vt[-1]
    n = n / np.linalg.norm(n)
    if n[2] > 0:                       # orient toward the camera (z decreases away from it)
        n = -n
    offset = float(n @ centroid)
    d = centred @ n
    return PlaneFit(normal=n, centroid=centroid, offset=offset,
                    rms_m=float(np.sqrt(np.mean(d ** 2))), n_points=int(pts.shape[0]),
                    singular_values=sv)


def normal_angle_deg(a: PlaneFit, b: PlaneFit) -> float:
    """Angle between two plane normals, in degrees, in [0, 90]."""
    c = float(np.clip(abs(np.dot(a.normal, b.normal)), -1.0, 1.0))
    return float(np.degrees(np.arccos(c)))


def plane_separation(front: PlaneFit, back: PlaneFit, reference_point: np.ndarray | None = None,
                     along: np.ndarray | None = None) -> dict:
    """Distance between two planes measured along a common direction through a reference point.

    This is the only correct way to compare the S40 step: the difference of two ROI depth medians is
    an optical-axis statistic, not a plane separation, and is wrong as soon as the planes are tilted.

    With `along = None` the mean normal is used. With parallel planes the result equals |c1 - c2|.
    """
    n_bar = front.normal + back.normal
    if np.linalg.norm(n_bar) < 1e-9:
        raise ValueError("normals are antiparallel; cannot define a common direction")
    n_bar = n_bar / np.linalg.norm(n_bar) if along is None else np.asarray(along, float)
    n_bar = n_bar / np.linalg.norm(n_bar)
    x0 = front.centroid if reference_point is None else np.asarray(reference_point, float)

    denom_f = float(front.normal @ n_bar)
    denom_b = float(back.normal @ n_bar)
    if abs(denom_f) < 1e-9 or abs(denom_b) < 1e-9:
        raise ValueError("a plane is parallel to the reference direction; separation undefined")
    t_f = (front.offset - float(front.normal @ x0)) / denom_f
    t_b = (back.offset - float(back.normal @ x0)) / denom_b
    return {"separation_m": float(abs(t_f - t_b)),
            "signed_m": float(t_f - t_b),
            "t_front_m": float(t_f), "t_back_m": float(t_b),
            "along": n_bar.tolist(), "reference_point": x0.tolist(),
            "parallel_case_offset_diff_m": float(abs(front.offset - back.offset)),
            "normal_angle_deg": normal_angle_deg(front, back)}


def separation_sensitivity(front: PlaneFit, back: PlaneFit, samples: int = 5) -> dict:
    """How much the separation changes as the reference point moves across the overlap region.

    For non-parallel planes this is the honest uncertainty statement: the 'step height' is only defined
    once a reference position is fixed.
    """
    c = 0.5 * (front.centroid + back.centroid)
    base = plane_separation(front, back, c)["separation_m"]
    vals = []
    for du in np.linspace(-1, 1, samples):
        for dv in np.linspace(-1, 1, samples):
            p = c + np.array([du * 0.02, dv * 0.02, 0.0])
            vals.append(plane_separation(front, back, p)["separation_m"])
    vals = np.array(vals)
    return {"separation_at_centroid_m": float(base),
            "spread_over_40mm_window_m": float(vals.max() - vals.min()),
            "std_over_40mm_window_m": float(vals.std())}


# ----------------------------------------------------------------------------------------------------- ROI


@dataclass
class ROI:
    """A polygonal region of interest in pixel coordinates, plus a boundary exclusion margin."""
    name: str
    polygon: Sequence[Sequence[float]]      # [(u, v), ...] in pixels
    boundary_erode_px: int = 3
    min_valid_ratio: float = 0.60

    def to_json(self) -> dict:
        return {"name": self.name, "polygon": [list(p) for p in self.polygon],
                "boundary_erode_px": int(self.boundary_erode_px),
                "min_valid_ratio": float(self.min_valid_ratio)}

    @classmethod
    def from_json(cls, d: dict) -> "ROI":
        return cls(d["name"], d["polygon"], int(d.get("boundary_erode_px", 3)),
                   float(d.get("min_valid_ratio", 0.60)))

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.to_json(), sort_keys=True).encode()).hexdigest()


def polygon_mask(shape: tuple[int, int], polygon: Sequence[Sequence[float]]) -> np.ndarray:
    """Rasterise a polygon (u, v) into a boolean mask using the even-odd rule."""
    h, w = shape
    vv, uu = np.mgrid[0:h, 0:w]
    poly = np.asarray(polygon, dtype=float)
    if poly.ndim != 2 or poly.shape[1] != 2 or poly.shape[0] < 3:
        raise ValueError("polygon needs >= 3 (u, v) vertices")
    inside = np.zeros((h, w), dtype=bool)
    n = len(poly)
    for i in range(n):
        u1, v1 = poly[i]
        u2, v2 = poly[(i + 1) % n]
        cond = ((v1 > vv) != (v2 > vv))
        with np.errstate(divide="ignore", invalid="ignore"):
            u_int = (u2 - u1) * (vv - v1) / (v2 - v1 + 1e-12) + u1
        inside ^= cond & (uu < u_int)
    return inside


def erode(mask: np.ndarray, px: int) -> np.ndarray:
    """Square-structuring-element erosion, implemented without scipy morphology dependencies."""
    if px <= 0:
        return mask.copy()
    out = mask.copy()
    for _ in range(px):
        m = out.copy()
        out = m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)
        out[0, :] = out[-1, :] = False
        out[:, 0] = out[:, -1] = False
    return out


def roi_stats(mask_roi: np.ndarray, depth_m: np.ndarray, roi: ROI) -> dict:
    """Validity statistics for a ROI; `ok` is the gate used before any metric is computed."""
    finite = valid_mask(depth_m)
    n_px = int(mask_roi.sum())
    n_valid = int((mask_roi & finite).sum())
    ratio = n_valid / n_px if n_px else 0.0
    return {"roi_px": n_px, "valid_px": n_valid, "valid_ratio": float(ratio),
            "ok": bool(n_px > 0 and ratio >= roi.min_valid_ratio)}


def collect_points(mask_roi: np.ndarray, depth_m: np.ndarray, intr: Intrinsics) -> np.ndarray:
    pts = backproject(depth_m, intr)
    sel = pts[mask_roi]
    return sel[np.isfinite(sel).all(axis=1)]
