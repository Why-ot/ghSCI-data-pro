# STAGE04.7 STEP2A Executive Report

```text
ORIGINAL_PROTOCOL_PRESERVED = YES
REVISED_PROTOCOL_CREATED = YES
PROTOCOL_SCIENTIFIC_GAPS_RESOLVED = YES
CPP_SOURCE_CREATED = YES
CPP_COMPILE = PASS
NATIVE_SDK_VERSION = 2.55.1
PHYSICAL_SAFETY_CONFIRMED = NO
CAMERA_STREAM_STARTED = NO
ACTUAL_DEPTH_FRAMES = 0
FORMAL_EXPERIMENT_STARTED = NO
READY_FOR_20S_PRECHECK = CONDITIONAL
PROTOCOL_FINAL_FROZEN = NO
```

## Outcome

The original protocol passed the required integrity gate and retained SHA256 `2c154df8309ec42db314b9aa3a0476d5e1cdf346877ec91961c4df38ae2dfd24`. It was not modified.

A separate revised candidate resolves the two STEP2 scientific-review gaps by defining four distinct uncertainty layers and the correct placement-level experimental unit. It also formalizes `h_ref`, `h_D435`, `e_h`, geometry restrictions, endpoint boundaries, covariance handling, and the unchanged `UNVERIFIED` research gates. The candidate is not frozen and requires user review.

The native C++ precheck program compiled successfully against librealsense 2.55.1 on aarch64. Default, help, offline configuration, unauthorized-capture denial, and dynamic-link tests passed without opening the camera. The actual runtime library is `/usr/local/lib/librealsense2.so.2.55`.

The code is prepared for a future explicitly authorized, serial-locked, maximum-20-second RGB-D test. Supported individual stream profiles have not been misrepresented as successful simultaneous streaming. No capture path was executed in STEP2A.

## Artifact hashes

| Artifact | SHA256 |
|---|---|
| Revised protocol candidate | `eefc0d3b195ca3892559d03d25711b5163a72849bebb04ff95d8b9fa1f22f9cd` |
| Physical safety confirmation form | `9978826d71955213071f7bc5215751b9be8e9e3470ed4e4f5264710fab0d14fc` |
| C++ source | `bdc3be562bae8b8f4ca5ee95f961a98057ec37b5a909acee7e57639f9e9f0af6` |
| Build script | `ae1116b2475a29135a6b0ecedc4f106c84a77510c5b1f228194da5ccd26b788e` |
| Compiled aarch64 binary | `e2e79e4034764cbe2be6b83a8b1b0051d5c8231d1b2e67315ecd8fa0d2033be0` |

## Remaining gate

`READY_FOR_20S_PRECHECK = CONDITIONAL` means software preparation is complete, but the camera must not be started until an authorized person completes physical safety confirmation and the user separately authorizes the precheck. This report does not freeze the candidate protocol or authorize capture, formal collection, robot motion, or Stage05.
