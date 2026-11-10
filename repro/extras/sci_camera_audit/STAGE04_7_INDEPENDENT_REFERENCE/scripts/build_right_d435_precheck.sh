#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_file="${script_dir}/right_d435_raw_precheck.cpp"
output_file="${script_dir}/right_d435_raw_precheck"

if ! command -v g++ >/dev/null 2>&1; then
    echo "BUILD_STATUS=FAIL"
    echo "BLOCKER=g++ not found"
    exit 1
fi

if ! command -v pkg-config >/dev/null 2>&1; then
    echo "BUILD_STATUS=FAIL"
    echo "BLOCKER=pkg-config not found"
    exit 1
fi

if ! pkg-config --exists realsense2; then
    echo "BUILD_STATUS=FAIL"
    echo "BLOCKER=realsense2 pkg-config metadata not found"
    exit 1
fi

header_file="/usr/local/include/librealsense2/rs.hpp"
library_file="/usr/local/lib/librealsense2.so"
if [[ ! -r "${header_file}" ]]; then
    echo "BUILD_STATUS=FAIL"
    echo "BLOCKER=missing ${header_file}"
    exit 1
fi
if [[ ! -e "${library_file}" ]]; then
    echo "BUILD_STATUS=FAIL"
    echo "BLOCKER=missing ${library_file}"
    exit 1
fi

read -r -a package_cflags <<< "$(pkg-config --cflags realsense2)"

echo "NATIVE_SDK_VERSION=$(pkg-config --modversion realsense2)"
echo "PKG_CONFIG_REPORTED_LIBS=$(pkg-config --libs realsense2)"
echo "SELECTED_HEADER=${header_file}"
echo "SELECTED_LIBRARY=${library_file}"
echo "CAMERA_ACCESS=NO"

g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic \
    "${package_cflags[@]}" \
    "${source_file}" \
    -L/usr/local/lib -Wl,-rpath,/usr/local/lib \
    -lrealsense2 \
    -o "${output_file}"

echo "BUILD_STATUS=PASS"
echo "OUTPUT=${output_file}"
