#include <librealsense2/rs.hpp>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <csignal>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr const char* kTargetSerial = "317422072133";
constexpr int kDepthWidth = 848;
constexpr int kDepthHeight = 480;
constexpr int kColorWidth = 640;
constexpr int kColorHeight = 480;
constexpr int kFps = 30;
constexpr int kMaximumCaptureSeconds = 20;
constexpr int kFrameTimeoutMilliseconds = 5000;
constexpr const char* kAuthorizationToken = "I_CONFIRM_PHYSICAL_SAFETY";

std::atomic<bool> g_stop_requested{false};

void signal_handler(int) { g_stop_requested.store(true); }

struct Options {
    bool help = false;
    bool check_config = false;
    bool capture = false;
    bool stream_authorized = false;
    int duration_seconds = kMaximumCaptureSeconds;
    int warmup_seconds = 2;
};

int parse_bounded_integer(const std::string& argument,
                          const std::string& prefix,
                          int minimum,
                          int maximum) {
    const std::string value_text = argument.substr(prefix.size());
    if (value_text.empty()) {
        throw std::runtime_error("missing value for " + prefix);
    }
    std::size_t consumed = 0;
    const int value = std::stoi(value_text, &consumed);
    if (consumed != value_text.size() || value < minimum || value > maximum) {
        throw std::runtime_error("value outside allowed range for " + prefix);
    }
    return value;
}

Options parse_options(int argc, char** argv) {
    Options options;
    const std::string duration_prefix = "--duration-seconds=";
    const std::string warmup_prefix = "--warmup-seconds=";
    const std::string authorization_argument =
        std::string("--authorize-stream=") + kAuthorizationToken;

    for (int index = 1; index < argc; ++index) {
        const std::string argument(argv[index]);
        if (argument == "--help" || argument == "-h") {
            options.help = true;
        } else if (argument == "--check-config") {
            options.check_config = true;
        } else if (argument == "--capture") {
            options.capture = true;
        } else if (argument == authorization_argument) {
            options.stream_authorized = true;
        } else if (argument.rfind("--authorize-stream=", 0) == 0) {
            throw std::runtime_error("invalid stream authorization token");
        } else if (argument.rfind(duration_prefix, 0) == 0) {
            options.duration_seconds = parse_bounded_integer(
                argument, duration_prefix, 1, kMaximumCaptureSeconds);
        } else if (argument.rfind(warmup_prefix, 0) == 0) {
            options.warmup_seconds =
                parse_bounded_integer(argument, warmup_prefix, 0, 10);
        } else {
            throw std::runtime_error("unknown argument: " + argument);
        }
    }

    if (options.capture && !options.stream_authorized) {
        throw std::runtime_error(
            "capture denied: the explicit physical-safety authorization token is required");
    }
    if (options.stream_authorized && !options.capture) {
        throw std::runtime_error(
            "authorization token supplied without --capture; refusing ambiguous request");
    }
    if (options.capture && options.check_config) {
        throw std::runtime_error("--capture and --check-config are mutually exclusive");
    }
    return options;
}

void print_help(const char* executable) {
    std::cout
        << "RIGHT D435 raw SDK precheck\n\n"
        << "Default behavior: print the fixed configuration and exit without creating "
           "an SDK context or opening a camera.\n\n"
        << "Usage:\n"
        << "  " << executable << " [--help]\n"
        << "  " << executable << " --check-config\n"
        << "  " << executable
        << " --capture --authorize-stream=" << kAuthorizationToken
        << " [--duration-seconds=1..20] [--warmup-seconds=0..10]\n\n"
        << "Safety:\n"
        << "  --help, --check-config, and the default invocation do not access a camera.\n"
        << "  Capture requires both --capture and the exact authorization token.\n"
        << "  The program selects serial " << kTargetSerial << " only.\n"
        << "  It does not use ROS, robot control, CAN, alignment, filters, or image saving.\n";
}

void print_fixed_configuration() {
    std::cout << "DEFAULT_ACTION=NO_STREAM\n"
              << "TARGET_SERIAL=" << kTargetSerial << '\n'
              << "DEPTH_REQUEST=848x480 Z16 30FPS\n"
              << "COLOR_REQUEST=640x480 RGB8 30FPS\n"
              << "MAX_CAPTURE_SECONDS=" << kMaximumCaptureSeconds << '\n'
              << "FRAME_TIMEOUT_MILLISECONDS=" << kFrameTimeoutMilliseconds << '\n'
              << "ALIGN=OFF\n"
              << "SPATIAL_FILTER=OFF\n"
              << "TEMPORAL_FILTER=OFF\n"
              << "HOLE_FILLING=OFF\n"
              << "DEPTH_COMPLETION=OFF\n"
              << "FULL_IMAGE_SEQUENCE_SAVE=OFF\n"
              << "CAMERA_SETTINGS_WRITE=OFF\n";
}

class PipelineGuard {
  public:
    explicit PipelineGuard(rs2::pipeline& pipeline) : pipeline_(pipeline) {}
    PipelineGuard(const PipelineGuard&) = delete;
    PipelineGuard& operator=(const PipelineGuard&) = delete;

    void mark_started() { started_ = true; }

    void stop_now() {
        if (started_) {
            pipeline_.stop();
            started_ = false;
        }
    }

    ~PipelineGuard() {
        if (started_) {
            try {
                pipeline_.stop();
            } catch (...) {
                // Destructors must not throw. The primary exception is reported by main.
            }
        }
    }

  private:
    rs2::pipeline& pipeline_;
    bool started_ = false;
};

struct StreamTiming {
    std::vector<double> timestamps_ms;
    std::uint64_t frames = 0;
    std::uint64_t missing_frame_numbers = 0;
    std::uint64_t previous_frame_number = 0;
    bool has_previous_frame_number = false;
    std::string timestamp_domain;
    bool mixed_timestamp_domains = false;

    void add(const rs2::frame& frame) {
        const std::uint64_t number = frame.get_frame_number();
        if (has_previous_frame_number && number != previous_frame_number + 1) {
            if (number > previous_frame_number + 1) {
                missing_frame_numbers += number - previous_frame_number - 1;
            } else {
                ++missing_frame_numbers;
            }
        }
        previous_frame_number = number;
        has_previous_frame_number = true;
        ++frames;
        timestamps_ms.push_back(frame.get_timestamp());

        const char* domain_name =
            rs2_timestamp_domain_to_string(frame.get_frame_timestamp_domain());
        const std::string current_domain = domain_name ? domain_name : "UNKNOWN";
        if (timestamp_domain.empty()) {
            timestamp_domain = current_domain;
        } else if (timestamp_domain != current_domain) {
            mixed_timestamp_domains = true;
        }
    }
};

struct IntervalSummary {
    double minimum_ms = std::numeric_limits<double>::quiet_NaN();
    double median_ms = std::numeric_limits<double>::quiet_NaN();
    double p95_ms = std::numeric_limits<double>::quiet_NaN();
    double maximum_ms = std::numeric_limits<double>::quiet_NaN();
};

double vector_quantile(const std::vector<double>& sorted, double probability) {
    if (sorted.empty()) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    const double position = probability * static_cast<double>(sorted.size() - 1);
    const auto lower = static_cast<std::size_t>(std::floor(position));
    const auto upper = static_cast<std::size_t>(std::ceil(position));
    if (lower == upper) {
        return sorted[lower];
    }
    const double weight = position - static_cast<double>(lower);
    return sorted[lower] * (1.0 - weight) + sorted[upper] * weight;
}

IntervalSummary summarize_intervals(const std::vector<double>& timestamps_ms) {
    IntervalSummary result;
    if (timestamps_ms.size() < 2) {
        return result;
    }
    std::vector<double> intervals;
    intervals.reserve(timestamps_ms.size() - 1);
    for (std::size_t index = 1; index < timestamps_ms.size(); ++index) {
        intervals.push_back(timestamps_ms[index] - timestamps_ms[index - 1]);
    }
    std::sort(intervals.begin(), intervals.end());
    result.minimum_ms = intervals.front();
    result.median_ms = vector_quantile(intervals, 0.50);
    result.p95_ms = vector_quantile(intervals, 0.95);
    result.maximum_ms = intervals.back();
    return result;
}

double timestamp_fps(const std::vector<double>& timestamps_ms) {
    if (timestamps_ms.size() < 2 || timestamps_ms.back() <= timestamps_ms.front()) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return 1000.0 * static_cast<double>(timestamps_ms.size() - 1) /
           (timestamps_ms.back() - timestamps_ms.front());
}

std::uint16_t histogram_quantile(const std::vector<std::uint64_t>& histogram,
                                 std::uint64_t population,
                                 double probability) {
    if (population == 0) {
        return 0;
    }
    const auto target = static_cast<std::uint64_t>(
        std::ceil(probability * static_cast<double>(population)));
    std::uint64_t cumulative = 0;
    for (std::size_t value = 1; value < histogram.size(); ++value) {
        cumulative += histogram[value];
        if (cumulative >= std::max<std::uint64_t>(1, target)) {
            return static_cast<std::uint16_t>(value);
        }
    }
    return std::numeric_limits<std::uint16_t>::max();
}

void print_intrinsics(const char* prefix, const rs2_intrinsics& intrinsics) {
    std::cout << prefix << "_WIDTH=" << intrinsics.width << '\n'
              << prefix << "_HEIGHT=" << intrinsics.height << '\n'
              << prefix << "_FX=" << intrinsics.fx << '\n'
              << prefix << "_FY=" << intrinsics.fy << '\n'
              << prefix << "_PPX=" << intrinsics.ppx << '\n'
              << prefix << "_PPY=" << intrinsics.ppy << '\n'
              << prefix << "_DISTORTION="
              << rs2_distortion_to_string(intrinsics.model) << '\n';
    std::cout << prefix << "_COEFFS=";
    for (int index = 0; index < 5; ++index) {
        if (index != 0) {
            std::cout << ',';
        }
        std::cout << intrinsics.coeffs[index];
    }
    std::cout << '\n';
}

void print_extrinsics(const rs2_extrinsics& extrinsics) {
    std::cout << "DEPTH_TO_COLOR_ROTATION=";
    for (int index = 0; index < 9; ++index) {
        if (index != 0) {
            std::cout << ',';
        }
        std::cout << extrinsics.rotation[index];
    }
    std::cout << "\nDEPTH_TO_COLOR_TRANSLATION_M=" << extrinsics.translation[0]
              << ',' << extrinsics.translation[1] << ','
              << extrinsics.translation[2] << '\n';
}

void print_timing(const char* prefix, const StreamTiming& timing) {
    const IntervalSummary intervals = summarize_intervals(timing.timestamps_ms);
    std::cout << prefix << "_FRAMES=" << timing.frames << '\n'
              << prefix << "_FPS=" << timestamp_fps(timing.timestamps_ms) << '\n'
              << prefix << "_TIMESTAMP_DOMAIN="
              << (timing.timestamp_domain.empty() ? "UNAVAILABLE"
                                                   : timing.timestamp_domain)
              << '\n'
              << prefix << "_TIMESTAMP_DOMAIN_MIXED="
              << (timing.mixed_timestamp_domains ? "YES" : "NO") << '\n'
              << prefix << "_MISSING_FRAME_NUMBERS="
              << timing.missing_frame_numbers << '\n'
              << prefix << "_INTERVAL_MIN_MS=" << intervals.minimum_ms << '\n'
              << prefix << "_INTERVAL_MEDIAN_MS=" << intervals.median_ms << '\n'
              << prefix << "_INTERVAL_P95_MS=" << intervals.p95_ms << '\n'
              << prefix << "_INTERVAL_MAX_MS=" << intervals.maximum_ms << '\n';
}

int run_capture(const Options& options) {
    // No context or device query occurs before this explicitly authorized function.
    rs2::pipeline pipeline;
    PipelineGuard pipeline_guard(pipeline);
    rs2::config configuration;
    configuration.enable_device(kTargetSerial);
    configuration.enable_stream(RS2_STREAM_DEPTH, kDepthWidth, kDepthHeight,
                                RS2_FORMAT_Z16, kFps);
    configuration.enable_stream(RS2_STREAM_COLOR, kColorWidth, kColorHeight,
                                RS2_FORMAT_RGB8, kFps);

    std::cout << "CAPTURE_AUTHORIZATION=ACCEPTED\n"
              << "CAPTURE_TARGET_SERIAL=" << kTargetSerial << '\n';

    const rs2::pipeline_profile active_profile = pipeline.start(configuration);
    pipeline_guard.mark_started();

    const rs2::device device = active_profile.get_device();
    const std::string actual_serial = device.get_info(RS2_CAMERA_INFO_SERIAL_NUMBER);
    if (actual_serial != kTargetSerial) {
        throw std::runtime_error("active device serial mismatch");
    }
    std::cout << "CAMERA_SERIAL=" << actual_serial << '\n'
              << "FIRMWARE_VERSION="
              << device.get_info(RS2_CAMERA_INFO_FIRMWARE_VERSION) << '\n';

    const auto depth_profile =
        active_profile.get_stream(RS2_STREAM_DEPTH).as<rs2::video_stream_profile>();
    const auto color_profile =
        active_profile.get_stream(RS2_STREAM_COLOR).as<rs2::video_stream_profile>();
    std::cout << "ACTUAL_DEPTH_PROFILE=" << depth_profile.width() << 'x'
              << depth_profile.height() << ' '
              << rs2_format_to_string(depth_profile.format()) << ' '
              << depth_profile.fps() << "FPS\n"
              << "ACTUAL_COLOR_PROFILE=" << color_profile.width() << 'x'
              << color_profile.height() << ' '
              << rs2_format_to_string(color_profile.format()) << ' '
              << color_profile.fps() << "FPS\n";

    const rs2::depth_sensor depth_sensor = device.first<rs2::depth_sensor>();
    const float depth_scale_m = depth_sensor.get_depth_scale();
    if (!(depth_scale_m > 0.0F)) {
        throw std::runtime_error("invalid non-positive depth scale");
    }
    std::cout << "DEPTH_SCALE_M_PER_UNIT=" << depth_scale_m << '\n';
    print_intrinsics("DEPTH_INTRINSICS", depth_profile.get_intrinsics());
    print_intrinsics("COLOR_INTRINSICS", color_profile.get_intrinsics());
    print_extrinsics(depth_profile.get_extrinsics_to(color_profile));

    const auto warmup_deadline = std::chrono::steady_clock::now() +
                                 std::chrono::seconds(options.warmup_seconds);
    std::uint64_t warmup_frames = 0;
    while (!g_stop_requested.load() &&
           std::chrono::steady_clock::now() < warmup_deadline) {
        const rs2::frameset frames =
            pipeline.wait_for_frames(kFrameTimeoutMilliseconds);
        if (frames.get_depth_frame() && frames.get_color_frame()) {
            ++warmup_frames;
        }
    }
    if (g_stop_requested.load()) {
        throw std::runtime_error("stop requested during warmup");
    }
    std::cout << "WARMUP_FRAMESETS=" << warmup_frames << '\n';

    std::vector<std::uint64_t> histogram(65536, 0);
    std::uint64_t total_samples = 0;
    std::uint64_t positive_samples = 0;
    std::uint64_t zero_samples = 0;
    std::uint64_t saturation_samples = 0;
    std::uint64_t valid_framesets = 0;
    StreamTiming depth_timing;
    StreamTiming color_timing;

    const auto observation_start = std::chrono::steady_clock::now();
    const auto observation_deadline =
        observation_start + std::chrono::seconds(options.duration_seconds);
    while (!g_stop_requested.load() &&
           std::chrono::steady_clock::now() < observation_deadline) {
        const rs2::frameset frames =
            pipeline.wait_for_frames(kFrameTimeoutMilliseconds);
        const rs2::depth_frame depth = frames.get_depth_frame();
        const rs2::video_frame color = frames.get_color_frame();
        if (!depth || !color) {
            continue;
        }
        ++valid_framesets;
        depth_timing.add(depth);
        color_timing.add(color);

        const auto* samples = static_cast<const std::uint16_t*>(depth.get_data());
        const std::size_t sample_count =
            static_cast<std::size_t>(depth.get_width()) * depth.get_height();
        total_samples += sample_count;
        for (std::size_t index = 0; index < sample_count; ++index) {
            const std::uint16_t value = samples[index];
            ++histogram[value];
            if (value == 0) {
                ++zero_samples;
            } else {
                ++positive_samples;
                if (value == std::numeric_limits<std::uint16_t>::max()) {
                    ++saturation_samples;
                }
            }
        }
    }

    const double elapsed_seconds = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - observation_start).count();
    pipeline_guard.stop_now();
    std::cout << "CAMERA_RESOURCE_RELEASED=YES\n";

    const double zero_fraction = total_samples == 0
                                     ? std::numeric_limits<double>::quiet_NaN()
                                     : static_cast<double>(zero_samples) /
                                           static_cast<double>(total_samples);
    const double valid_fraction = total_samples == 0
                                      ? std::numeric_limits<double>::quiet_NaN()
                                      : static_cast<double>(positive_samples) /
                                            static_cast<double>(total_samples);
    const auto minimum_raw = histogram_quantile(histogram, positive_samples, 0.0);
    const auto median_raw = histogram_quantile(histogram, positive_samples, 0.50);
    const auto p95_raw = histogram_quantile(histogram, positive_samples, 0.95);
    const auto p99_raw = histogram_quantile(histogram, positive_samples, 0.99);
    const auto maximum_raw = histogram_quantile(histogram, positive_samples, 1.0);
    const double millimetres_per_unit = static_cast<double>(depth_scale_m) * 1000.0;

    std::cout << std::setprecision(12)
              << "OBSERVATION_ELAPSED_SECONDS=" << elapsed_seconds << '\n'
              << "VALID_FRAMESETS=" << valid_framesets << '\n'
              << "TOTAL_DEPTH_SAMPLES=" << total_samples << '\n'
              << "ZERO_FRACTION=" << zero_fraction << '\n'
              << "POSITIVE_VALID_FRACTION=" << valid_fraction << '\n'
              << "MIN_RAW=" << minimum_raw << '\n'
              << "MEDIAN_RAW=" << median_raw << '\n'
              << "P95_RAW=" << p95_raw << '\n'
              << "P99_RAW=" << p99_raw << '\n'
              << "MAX_RAW=" << maximum_raw << '\n'
              << "MIN_MM=" << minimum_raw * millimetres_per_unit << '\n'
              << "MEDIAN_MM=" << median_raw * millimetres_per_unit << '\n'
              << "P95_MM=" << p95_raw * millimetres_per_unit << '\n'
              << "P99_MM=" << p99_raw * millimetres_per_unit << '\n'
              << "MAX_MM=" << maximum_raw * millimetres_per_unit << '\n'
              << "SATURATION_COUNT=" << saturation_samples << '\n';
    print_timing("DEPTH", depth_timing);
    print_timing("COLOR", color_timing);

    if (g_stop_requested.load()) {
        std::cout << "CAPTURE_EXIT=INTERRUPTED_SAFE_RELEASE\n";
        return 130;
    }
    std::cout << "CAPTURE_EXIT=PASS\n";
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        if (options.help) {
            print_help(argv[0]);
            return 0;
        }
        if (!options.capture) {
            print_fixed_configuration();
            if (options.check_config) {
                std::cout << "OFFLINE_CONFIG_CHECK=PASS\n";
            }
            return 0;
        }

        std::signal(SIGINT, signal_handler);
        std::signal(SIGTERM, signal_handler);
        return run_capture(options);
    } catch (const rs2::error& error) {
        std::cerr << "LIBREALSENSE_ERROR_FUNCTION=" << error.get_failed_function()
                  << '\n'
                  << "LIBREALSENSE_ERROR_ARGS=" << error.get_failed_args() << '\n'
                  << "LIBREALSENSE_ERROR=" << error.what() << '\n';
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "ERROR=" << error.what() << '\n';
        return 1;
    }
}
