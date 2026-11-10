"""W6 synthetic S40 generator — every output is labelled SYNTHETIC and carries its true parameters.

Nothing here imitates a D435. The generator produces idealised two-plane geometry with known ground
truth so that the analysis pipeline can be validated; the resulting numbers are *never* sensor results.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np

from .core import Intrinsics, PlaneFit, fit_plane

SYNTHETIC_TAG = "SYNTHETIC"


@dataclass
class S40Truth:
    """Ground truth of one synthetic capture."""
    tag: str
    step_m: float
    front_normal: list
    back_normal: list
    front_offset: float
    back_offset: float
    noise_sigma_mm: float = 0.0
    depth_scale: float = 0.001
    tilt_deg: float = 0.0
    unparallel_deg: float = 0.0
    distance_m: float = 0.60
    invalid_fraction: float = 0.0
    outlier_count: int = 0
    boundary_mix_px: int = 0
    notes: str = ""

    def to_json(self) -> dict:
        d = asdict(self)
        d["tag"] = SYNTHETIC_TAG
        return d


def render_two_planes(intr: Intrinsics, shape: tuple[int, int], truth: S40Truth,
                      front_uv: tuple[float, float] = (0.35, 0.40),
                      back_uv: tuple[float, float] = (0.65, 0.60),
                      front_size: float = 0.22, back_size: float = 0.22,
                      rng: np.random.Generator | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Render two axis-aligned rectangular plates at nominal depths (metres). Returns (depth_m, label)."""
    h, w = shape
    vv, uu = np.mgrid[0:h, 0:w]
    x = (uu - intr.cx) / intr.fx
    y = (vv - intr.cy) / intr.fy

    # front plane: z = d_f + a*x + b*y  (small tilt), back plane likewise, offset by the step
    nf = np.array(truth.front_normal, float)
    nb = np.array(truth.back_normal, float)
    z = np.full((h, w), np.nan)

    def plane_z(n, c):
        # n . (x*z, y*z, z) = c  ->  z = c / (n . (x, y, 1))
        denom = n[0] * x + n[1] * y + n[2]
        return c / denom

    zf = plane_z(nf, truth.front_offset)
    zb = plane_z(nb, truth.back_offset)

    label = np.zeros((h, w), np.int8)
    uf, vf = front_uv[0] * w, front_uv[1] * h
    ub, vb = back_uv[0] * w, back_uv[1] * h
    half_f = 0.5 * front_size / truth.distance_m * intr.fx
    half_b = 0.5 * back_size / truth.distance_m * intr.fx
    mf = (np.abs(uu - uf) <= half_f) & (np.abs(vv - vf) <= half_f)
    mb = (np.abs(uu - ub) <= half_b) & (np.abs(vv - vb) <= half_b)
    z[mf] = zf[mf]
    z[mb] = zb[mb]
    label[mf] = 1
    label[mb] = 2

    if rng is not None and truth.noise_sigma_mm > 0:
        n = rng.normal(0.0, truth.noise_sigma_mm / 1000.0, size=z.shape)
        z = z + n
    if truth.invalid_fraction > 0 and rng is not None:
        drop = rng.random(z.shape) < truth.invalid_fraction
        z[drop] = np.nan
    return z, label


def quantize(z_m: np.ndarray, depth_scale: float = 0.001) -> np.ndarray:
    """Convert metres to raw Z16 units (NaN -> 0 = no measurement)."""
    raw = np.zeros(z_m.shape, dtype=np.uint16)
    ok = np.isfinite(z_m) & (z_m > 0)
    raw[ok] = np.clip(np.round(z_m[ok] / depth_scale), 0, 65535).astype(np.uint16)
    return raw


def add_outliers(z_m: np.ndarray, n: int, rng: np.random.Generator, patch: int = 12,
                 delta_mm: float = 25.0) -> np.ndarray:
    """Insert `n` small square patches of constant depth bias (a synthetic 'valid but wrong' defect)."""
    z = z_m.copy()
    h, w = z.shape
    for _ in range(n):
        r = int(rng.integers(patch, h - patch)); c = int(rng.integers(patch, w - patch))
        z[r:r + patch, c:c + patch] += delta_mm / 1000.0
    return z


def add_boundary_mixing(z_m: np.ndarray, px: int = 3) -> np.ndarray:
    """Blend depth across the step edge to imitate mixed pixels at a depth discontinuity."""
    z = z_m.copy()
    finite = np.isfinite(z)
    med = np.nanmedian(z[finite]) if finite.any() else 0.0
    edge = np.zeros_like(finite)
    edge[:, :-1] = finite[:, :-1] & finite[:, 1:] & (np.abs(np.diff(z, axis=1)) > 0.01)
    edge = edge | np.roll(edge, 1, axis=1) | np.roll(edge, -1, axis=1)
    for _ in range(max(0, px - 1)):
        edge = edge | np.roll(edge, 1, axis=0) | np.roll(edge, -1, axis=0)
    z[edge] = 0.5 * z[edge] + 0.5 * med
    return z
