from src.data_generation import generate_scenario_telemetry
from src.scenario_config import SCENARIOS
from src.kpi_analysis import calculate_scenario_kpis


def fmt_pct(value):
    if value != value:
        return "N/A"
    return f"{value:.1%}"


def fmt_ttc(value):
    if value != value:
        return "N/A"
    return f"{value:.3f}s"


def classify_status(kpi):
    if kpi["aeb_exercised"]:
        if kpi["aeb_fn"] > 0:
            return "INVESTIGATE AEB"
        return "AEB PASS"

    if kpi["fcw_exercised"]:
        if kpi["fcw_fn"] > 0 or kpi["fcw_fp"] > 0:
            return "INVESTIGATE FCW"
        return "FCW PASS"

    return "NOT EXERCISED"


results = []

for scenario_id, scenario in SCENARIOS.items():
    telemetry = generate_scenario_telemetry(scenario)
    kpi = calculate_scenario_kpis(telemetry)
    results.append(kpi)


print("\n" + "=" * 110)
print("ADAS PERFORMANCE INVESTIGATION")
print("=" * 110)

for result in results:
    print(
        f"{result['scenario_id']} | "
        f"Min TTC={fmt_ttc(result['min_ttc_s'])} | "
        f"Detection={fmt_pct(result['detection_rate'])} | "
        f"GT-W={result['gt_warning_events']} | "
        f"GT-AEB={result['gt_braking_events']} | "
        f"FCW={result['warning_count']} | "
        f"AEB={result['brake_count']} | "
        f"FCW Recall={fmt_pct(result['fcw_recall'])} | "
        f"AEB Recall={fmt_pct(result['aeb_recall'])} | "
        f"FCW FN={result['fcw_fn']} | "
        f"AEB FN={result['aeb_fn']} | "
        f"Status={classify_status(result)}"
    )

print("\n" + "=" * 110)
print("INTERPRETATION")
print("=" * 110)

for result in results:
    print(
        f"{result['scenario_id']}: "
        f"FCW exercised={result['fcw_exercised']}, "
        f"AEB exercised={result['aeb_exercised']}, "
        f"status={classify_status(result)}"
    )