#include <epcsaft/native_model_v1.h>

#include <array>
#include <cmath>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <string>

namespace {

constexpr double kTemperatureK = 313.15;
constexpr double kPressureMinPa = 6105.45;
constexpr double kPressureMaxPa = 300000.0;
constexpr std::size_t kComponentCount = 9;
constexpr std::size_t kBasisRows = 8;
constexpr std::size_t kActiveParameters = 2;

const std::array<const char*, kComponentCount> kExpectedComponents = {
    "carbon-dioxide",
    "monoethanolamine",
    "water",
    "protonated-monoethanolamine",
    "carbamate-anion",
    "bicarbonate-anion",
    "carbonate-anion",
    "hydronium-cation",
    "hydroxide-anion",
};

[[noreturn]] void fail(const std::string& message) {
    std::cerr << "ERROR: " << message << '\n';
    std::exit(EXIT_FAILURE);
}

struct ValueProbe {
    std::array<double, kBasisRows * kComponentCount> basis{};
    std::array<double, kBasisRows> contractions{};
    std::array<double, kComponentCount> composition{};
    epcsaft_neutral_reference_result_v1 result{};

    ValueProbe() {
        result.struct_size = sizeof(result);
        result.component_count = kComponentCount;
        result.neutral_basis_row_count = kBasisRows;
        result.neutral_basis_capacity = basis.size();
        result.contraction_capacity = contractions.size();
        result.reference_composition_capacity = composition.size();
        result.neutral_basis = basis.data();
        result.log_fugacity_contractions = contractions.data();
        result.reference_composition = composition.data();
    }
};

int evaluate_value(
    const epcsaft_native_sdk_v1* sdk,
    const char* parameter_fingerprint,
    double temperature_k,
    double pressure_pa,
    ValueProbe& probe
) {
    return sdk->evaluate_neutral_reference(
        sdk->model_context,
        parameter_fingerprint,
        temperature_k,
        pressure_pa,
        &probe.result
    );
}

void require_status(
    const epcsaft_native_sdk_v1* sdk,
    const char* parameter_fingerprint,
    double temperature_k,
    double pressure_pa,
    int expected
) {
    ValueProbe probe;
    const int returned =
        evaluate_value(sdk, parameter_fingerprint, temperature_k, pressure_pa, probe);
    if (returned != expected || probe.result.status != expected) {
        fail(
            "neutral-reference status mismatch at " + std::to_string(temperature_k)
            + " K and " + std::to_string(pressure_pa)
            + " Pa: returned=" + std::to_string(returned)
            + " result=" + std::to_string(probe.result.status)
            + " error=" + probe.result.error
        );
    }
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 4) {
        fail("usage: mea_gate0_provider_probe MODEL PARAMETER_FINGERPRINT TOPOLOGY_FINGERPRINT");
    }
    const char* model_path = argv[1];
    const char* parameter_fingerprint = argv[2];
    const char* topology_fingerprint = argv[3];

    std::array<char, EPCSAFT_NATIVE_SDK_V1_ERROR_SIZE> load_error{};
    epcsaft_native_model_handle_v1* model =
        epcsaft_native_model_load_v1(model_path, load_error.data(), load_error.size());
    if (model == nullptr) {
        fail("cannot load exported model: " + std::string(load_error.data()));
    }
    const epcsaft_native_sdk_v1* sdk = epcsaft_native_model_sdk_v1(model);
    if (
        sdk == nullptr
        || sdk->abi_version != EPCSAFT_NATIVE_SDK_V1_ABI_VERSION
        || sdk->component_count != kComponentCount
        || sdk->neutral_reference_basis_row_count != kBasisRows
        || sdk->neutral_reference_result_size != sizeof(epcsaft_neutral_reference_result_v1)
        || sdk->neutral_reference_derivative_result_size
            != sizeof(epcsaft_neutral_reference_derivative_result_v1)
        || sdk->evaluate_neutral_reference == nullptr
        || sdk->evaluate_neutral_reference_derivatives == nullptr
    ) {
        fail("installed native SDK descriptor does not match the Gate 0 contract");
    }
    for (std::size_t index = 0; index < kComponentCount; ++index) {
        if (std::strcmp(sdk->component_ids[index], kExpectedComponents[index]) != 0) {
            fail("installed component order differs at index " + std::to_string(index));
        }
    }
    if (
        std::strcmp(epcsaft_native_model_fingerprint_v1(model), parameter_fingerprint)
        != 0
    ) {
        fail("exported model parameter fingerprint differs");
    }

    require_status(
        sdk,
        parameter_fingerprint,
        kTemperatureK,
        100000.0,
        EPCSAFT_NATIVE_STATUS_OK_V1
    );
    require_status(
        sdk,
        parameter_fingerprint,
        kTemperatureK,
        (kPressureMinPa + kPressureMaxPa) / 2.0,
        EPCSAFT_NATIVE_STATUS_OK_V1
    );
    require_status(
        sdk,
        parameter_fingerprint,
        kTemperatureK,
        kPressureMinPa - 0.01,
        EPCSAFT_NATIVE_STATUS_DOMAIN_ERROR_V1
    );
    require_status(
        sdk,
        parameter_fingerprint,
        kTemperatureK,
        kPressureMaxPa + 0.01,
        EPCSAFT_NATIVE_STATUS_DOMAIN_ERROR_V1
    );
    require_status(
        sdk,
        parameter_fingerprint,
        kTemperatureK - 0.01,
        100000.0,
        EPCSAFT_NATIVE_STATUS_DOMAIN_ERROR_V1
    );
    require_status(
        sdk,
        parameter_fingerprint,
        kTemperatureK + 0.01,
        100000.0,
        EPCSAFT_NATIVE_STATUS_DOMAIN_ERROR_V1
    );

    std::array<epcsaft_active_parameter_request_v1, kActiveParameters> active{};
    active[0] = {
        sizeof(epcsaft_active_parameter_request_v1),
        EPCSAFT_NATIVE_PARAMETER_FAMILY_SEGMENT_DIAMETER_V1,
        EPCSAFT_NATIVE_PARAMETER_IDENTITY_COMPONENT_V1,
        3,
        -1,
        -1,
        3.48508556586,
        "angstrom",
    };
    active[1] = {
        sizeof(epcsaft_active_parameter_request_v1),
        EPCSAFT_NATIVE_PARAMETER_FAMILY_SEGMENT_DIAMETER_V1,
        EPCSAFT_NATIVE_PARAMETER_IDENTITY_COMPONENT_V1,
        4,
        -1,
        -1,
        3.53543525721,
        "angstrom",
    };
    ValueProbe value;
    std::array<double, kBasisRows> pressure_derivatives{};
    std::array<double, kBasisRows * kActiveParameters> parameter_derivatives{};
    epcsaft_neutral_reference_derivative_result_v1 derivative{};
    derivative.struct_size = sizeof(derivative);
    derivative.value = value.result;
    derivative.active_parameter_count = kActiveParameters;
    derivative.pressure_derivative_capacity = pressure_derivatives.size();
    derivative.parameter_derivative_capacity = parameter_derivatives.size();
    derivative.pressure_derivatives_per_pa = pressure_derivatives.data();
    derivative.parameter_derivatives = parameter_derivatives.data();

    const int derivative_status = sdk->evaluate_neutral_reference_derivatives(
        sdk->model_context,
        parameter_fingerprint,
        topology_fingerprint,
        kTemperatureK,
        7326.7,
        active.data(),
        active.size(),
        &derivative
    );
    const auto required_derivatives =
        EPCSAFT_NEUTRAL_REFERENCE_DERIVATIVE_PRESSURE_V1
        | EPCSAFT_NEUTRAL_REFERENCE_DERIVATIVE_PARAMETERS_V1;
    if (
        derivative_status != EPCSAFT_NATIVE_STATUS_OK_V1
        || derivative.status != EPCSAFT_NATIVE_STATUS_OK_V1
        || derivative.value.status != EPCSAFT_NATIVE_STATUS_OK_V1
        || derivative.derivative_availability != required_derivatives
        || derivative.source_pressure_min_pa != kPressureMinPa
        || derivative.source_pressure_max_pa != kPressureMaxPa
        || std::strcmp(derivative.parameter_fingerprint, parameter_fingerprint) != 0
        || std::strcmp(derivative.topology_fingerprint, topology_fingerprint) != 0
        || std::strcmp(
               derivative.helmholtz_basis_id,
               EPCSAFT_NATIVE_HELMHOLTZ_BASIS_ID_V1
           ) != 0
    ) {
        fail("neutral-reference derivative contract failed: " + std::string(derivative.error));
    }
    for (double value_item : pressure_derivatives) {
        if (!std::isfinite(value_item)) {
            fail("non-finite pressure derivative");
        }
    }
    for (double value_item : parameter_derivatives) {
        if (!std::isfinite(value_item)) {
            fail("non-finite active-parameter derivative");
        }
    }

    std::cout
        << "{\"abi_version\":" << sdk->abi_version
        << ",\"table_size\":" << sdk->table_size
        << ",\"component_count\":" << sdk->component_count
        << ",\"neutral_basis_row_count\":" << sdk->neutral_reference_basis_row_count
        << ",\"neutral_reference_result_size\":" << sdk->neutral_reference_result_size
        << ",\"neutral_reference_derivative_result_size\":"
        << sdk->neutral_reference_derivative_result_size
        << ",\"derivative_status\":" << derivative_status
        << ",\"derivative_availability\":" << derivative.derivative_availability
        << ",\"source_pressure_min_pa\":" << derivative.source_pressure_min_pa
        << ",\"source_pressure_max_pa\":" << derivative.source_pressure_max_pa
        << ",\"outside_pressure_status\":"
        << EPCSAFT_NATIVE_STATUS_DOMAIN_ERROR_V1
        << ",\"outside_temperature_status\":"
        << EPCSAFT_NATIVE_STATUS_DOMAIN_ERROR_V1
        << "}\n";
    epcsaft_native_model_destroy_v1(model);
    return EXIT_SUCCESS;
}
