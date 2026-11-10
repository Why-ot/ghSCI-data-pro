# RIGHT D435 First Raw-Depth Stream Quality

## Scope

This document reports the single authorized Step2B diagnostic observation. It is not part of the formal 135-unit experiment and contains no saved RGB-D image sequence.

## Acquisition facts

- Camera: RIGHT D435, serial `317422072133`
- Firmware: `5.17.0.10`
- Native SDK: librealsense `2.55.1`
- Actual depth stream: `848x480 Z16 30FPS`
- Actual color stream: `640x480 RGB8 30FPS`
- Actual depth scale: `0.001 m/raw unit` (`1.0 mm/raw unit`)
- Warmup framesets: `49`
- Observation duration: `20.016360726 s`
- Depth frames: `600`
- Color frames: `600`
- Alignment and depth filters: `OFF`

## Depth validity observation

| Metric | Observed value |
|---|---:|
| Raw dtype | `uint16_t` / Z16 |
| Total depth samples | 244,224,000 |
| Zero count | 63,292,279 |
| Zero fraction | 0.259156671744 (25.9156671744%) |
| Positive count | 180,931,721 |
| Positive valid fraction | 0.740843328256 (74.0843328256%) |
| Saturation value | 65535 |
| Saturation count | 14,617 |
| Saturation fraction | 0.000059850793 (0.005985079%) |

Here, “positive valid” means only that the raw Z16 sample is greater than zero. It does not mean that the value is geometrically correct.

## Positive raw-depth distribution

Quantiles were computed over positive samples only, after the active sensor depth scale was read.

| Statistic | Raw units | Millimetres reported by program |
|---|---:|---:|
| Minimum | 173 | 173.000008217 |
| Median | 396 | 396.000018809 |
| P95 | 1136 | 1136.00005396 |
| P99 | 2138 | 2138.00010155 |
| Maximum | 65535 | 65535.0031127 |

The maximum corresponds to the saturated raw value and must not be interpreted as a trustworthy physical range measurement. Small floating-point deviations from exact integer millimetres arise from the SDK float representation of the `0.001 m/unit` depth scale.

## Timing and continuity

| Stream | Frames | Actual FPS | Missing frame numbers | Timestamp domain | Median interval |
|---|---:|---:|---:|---|---:|
| Depth | 600 | 29.9981871514 | 0 | Global Time | 33.3571777344 ms |
| Color | 600 | 29.9981864179 | 0 | Global Time | 33.3571777344 ms |

Neither stream changed timestamp domain during the observation. The observed interval ranges were `32.1242675781–33.4465332031 ms` for depth and `32.125–33.4467773438 ms` for color.

## Scientific limitation

The zero fraction, positive fraction, quantiles, and saturation count are observations of this one static diagnostic view. They do not prove a sensor fault, a true geometric discrepancy, or `PER_PIXEL_VALID_BUT_WRONG_GT`. No independent physical step measurement or reviewed comparison uncertainty was applied in Step2B.
