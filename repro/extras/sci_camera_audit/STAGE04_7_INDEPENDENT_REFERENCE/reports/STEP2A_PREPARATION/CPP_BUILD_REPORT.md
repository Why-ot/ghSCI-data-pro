# STEP2A Native C++ SDK Build Report

## Build environment

| Item | Observed value |
|---|---|
| Architecture | `aarch64` |
| Compiler | `g++ 9.4.0` |
| pkg-config | `0.29.1` |
| Native librealsense version | `2.55.1` |
| Header | `/usr/local/include/librealsense2/rs.hpp` |
| Linker library | `/usr/local/lib/librealsense2.so` |
| Runtime resolution | `/usr/local/lib/librealsense2.so.2.55` |

`pkg-config --libs realsense2` reports `-L/usr/local/lib/x86_64-linux-gnu -lrealsense2`, which is inconsistent with the aarch64 host. The build script records this fact and explicitly selects `/usr/local/lib` without installing, upgrading, rebuilding, or changing the SDK.

## Artifacts

| Artifact | SHA256 |
|---|---|
| `scripts/right_d435_raw_precheck.cpp` | `bdc3be562bae8b8f4ca5ee95f961a98057ec37b5a909acee7e57639f9e9f0af6` |
| `scripts/build_right_d435_precheck.sh` | `ae1116b2475a29135a6b0ecedc4f106c84a77510c5b1f228194da5ccd26b788e` |
| `scripts/right_d435_raw_precheck` | `e2e79e4034764cbe2be6b83a8b1b0051d5c8231d1b2e67315ecd8fa0d2033be0` |

The binary is an ELF64 little-endian AArch64 dynamically linked executable.

## Compilation result

- Language mode: `C++17`
- Flags: `-O2 -Wall -Wextra -Wpedantic`
- Compile result: `PASS`
- Compiler warnings observed: `NONE`
- Camera accessed during compilation: `NO`

## Static behavior and safeguards

- Default action prints fixed configuration and exits without creating an SDK context.
- `--help` does not access a camera.
- `--check-config` performs an offline constants/configuration self-check only.
- Streaming requires both `--capture` and the exact token `--authorize-stream=I_CONFIRM_PHYSICAL_SAFETY`.
- Missing authorization is rejected before SDK context creation; denial test exit code was `1`.
- Future streaming is bound with `config.enable_device("317422072133")`.
- No explicit device-list query is used by the program.
- Requested future streams are Depth `848x480 Z16 30FPS` and Color `640x480 RGB8 30FPS`.
- Maximum observation time is 20 seconds, with bounded warmup and a 5000 ms frame wait timeout.
- SIGINT/SIGTERM handling requests controlled exit.
- An RAII guard stops only the pipeline started by this program on normal, exception, or early-exit paths.
- No align, spatial filter, temporal filter, hole filling, or depth completion object is created.
- No sensor option is written; there are no firmware, EEPROM, emitter, or exposure changes.
- No full image sequence is saved.
- No ROS, Piper, CAN, joint, gripper, or robot-control API is present.

## Offline execution tests

| Test | Result | Camera stream |
|---|---|---|
| `--help` | PASS | Not started |
| Default invocation | PASS; `DEFAULT_ACTION=NO_STREAM` | Not started |
| `--check-config` | PASS; `OFFLINE_CONFIG_CHECK=PASS` | Not started |
| Unauthorized `--capture` | PASS; denied before SDK access | Not started |
| Dynamic link inspection | PASS; `/usr/local/lib/librealsense2.so.2.55` | Not started |

The authorized streaming path has been compiled but was not executed. Therefore simultaneous RGB-D negotiation, actual depth scale, live intrinsics/extrinsics retrieval, timestamps, FPS, continuity, and depth statistics remain runtime-unverified.
