# Depth Scale and Encoding

## Current precheck result

| Camera | Expected serial | Current raw topic | Encoding | Scale | Provenance |
|---|---|---|---|---|---|
| Left D435 | `342222072464` | UNVERIFIED | UNVERIFIED | UNVERIFIED | No accessible ROS Master/message/driver parameter |
| Right D435 | `317422072133` | UNVERIFIED | UNVERIFIED | UNVERIFIED | No accessible ROS Master/message/driver parameter |

The prior audit recorded that the historical launch log configured both depth streams as RealSense `Z16`, but it did not capture live ROS message headers or a reliable depth-scale value. That historical configuration is insufficient to claim a present ROS encoding or physical unit.

No default millimetre assumption was made. No conversion to metres or millimetres was performed.

Because no messages were received, row stride, byte order, buffer length, dtype, invalid values, quantiles, and saturation could not be checked.
