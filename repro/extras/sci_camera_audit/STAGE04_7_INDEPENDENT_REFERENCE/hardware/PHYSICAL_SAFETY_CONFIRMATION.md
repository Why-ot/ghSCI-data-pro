# STAGE04.7 Physical Safety Confirmation

This form must be completed by an authorized person at the physical experiment site. Remote process checks, camera enumeration, or software inactivity cannot establish mechanical safety. This document does not authorize robot movement.

## Confirmation checklist

| ID | Required confirmation | Initial result | On-site evidence/notes |
|---|---|---|---|
| PSC-01 | The robot is in a safe and mechanically stable state. | `NOT_CONFIRMED` |  |
| PSC-02 | The wrist-mounted RIGHT D435 and its mount are secure. | `NOT_CONFIRMED` |  |
| PSC-03 | There is no credible risk of unexpected arm movement during the camera precheck. | `NOT_CONFIRMED` |  |
| PSC-04 | USB and power connections are secure and do not create pull, snag, or electrical hazards. | `NOT_CONFIRMED` |  |
| PSC-05 | The experiment area is clear of interference and collision hazards. | `NOT_CONFIRMED` |  |
| PSC-06 | The required viewpoint can be used without any robot movement. | `NOT_CONFIRMED` |  |
| PSC-07 | The on-site responsible person has reviewed and confirmed all items. | `NOT_CONFIRMED` |  |
| PSC-08 | Confirmation time has been recorded. | `NOT_CONFIRMED` |  |

## Human sign-off fields

- On-site responsible person: `NOT_CONFIRMED`
- Role/authorization: `NOT_CONFIRMED`
- Confirmation time and timezone: `NOT_CONFIRMED`
- Signature or approved identifier: `NOT_CONFIRMED`
- Additional restrictions: `NOT_CONFIRMED`

## Gate result

`PHYSICAL_SAFETY_CONFIRMED = NO`

Do not change this gate based only on software inspection. An authorized person must complete every applicable field before a separately authorized camera-streaming task begins. If any item cannot be confirmed, stop the physical experiment. Do not use a robot command to compensate for an unsafe or unsuitable camera pose.
