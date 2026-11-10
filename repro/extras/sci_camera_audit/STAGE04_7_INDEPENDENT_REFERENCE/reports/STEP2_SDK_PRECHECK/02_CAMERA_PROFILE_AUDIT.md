# STEP2 Right D435 Camera Profile Audit

- Audit time: `2026-10-26T11:53:34+08:00`
- Target camera: `RIGHT_D435`
- Required serial: `317422072133`
- Detection result: `PASS`

## Current SDK enumeration

| Field | Observed value |
|---|---|
| Name | Intel RealSense D435 |
| Serial | `317422072133` |
| Firmware | `5.17.0.10` |
| SDK-reported recommended firmware | `5.16.0.1` |
| Product ID | `0B07` |
| Product line | `D400` |
| USB type descriptor | `3.2` |
| USB topology speed | `5000M` |
| Physical port | `/sys/devices/platform/3610000.xhci/usb2/2-1/2-1.1/2-1.1.1/2-1.1.1:1.0/video4linux/video0` |

The SDK also enumerated an abnormal D400 identity with serial `ffffffffffff`. It was not selected for streaming, reset, firmware access, configuration, or modification. Historical LEFT serial `342222072464` was not detected.

## Requested mode support

| Stream | Requested mode | Supported | Evidence |
|---|---|---|---|
| Depth | `848x480 Z16 30FPS` | YES | The Stereo Module advertises `848x480 Z16 @ 90/60/30/15/6 Hz`. |
| Color | `640x480 RGB8 30FPS` | YES | The RGB Camera advertises `640x480 RGB8 @ 60/30/15/6 Hz`. |

No substitute profile was selected. Because the capture gate failed before streaming, these are supported profiles, not actual running profiles.

## Requested-profile intrinsics

Depth `848x480 Z16`:

- Width/height: `848 x 480`
- `fx = 430.599609375`
- `fy = 430.599609375`
- `ppx = 421.502075195312`
- `ppy = 236.096893310547`
- Distortion: `Brown Conrady`
- Coefficients: `[0, 0, 0, 0, 0]`
- FOV: `89.11 x 58.26 degrees`

Color `640x480` for `{YUYV/RGB8/BGR8/RGBA8/BGRA8/Y8}`:

- Width/height: `640 x 480`
- `fx = 607.983520507812`
- `fy = 607.655639648438`
- `ppx = 319.550628662109`
- `ppy = 254.650497436523`
- Distortion: `Inverse Brown Conrady`
- Coefficients: `[0, 0, 0, 0, 0]`
- FOV: `55.52 x 43.08 degrees`

## Depth-to-color extrinsics

Rotation matrix:

```text
 0.99994900   0.00891122  -0.00475572
-0.00892269   0.99995700  -0.00239545
 0.00473417   0.00243776   0.99998600
```

Translation vector in metres:

```text
[0.01489641610533, 0.00015716343477834, 0.0000737125301384367]
```

## Depth scale

The Stereo Module advertises a Depth Units option with range `1e-06` to `0.01`, step `1e-06`, and default `0.001`. The option query also produced a hardware-monitor response error (`response -9`). Because no gated pipeline was started and no successful current-value read was obtained, the actual depth scale is recorded as `UNVERIFIED`; the advertised default is not substituted as a measured current value.
