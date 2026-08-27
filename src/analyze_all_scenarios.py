from src.data_generation import generate_scenario_telemetry
from src.scenario_config import SCENARIOS
from src.kpi_analysis import calculate_scenario_kpis

results = []

for scenario_id, scenario in SCENARIOS.items():
    telemetry = generate_scenario_telemetry(scenario)

    kpis = calculate_scenario_kpis(telemetry)

    results.append(kpis)

print("\n=== ADAS SCENARIO PERFORMANCE ===\n")

for result in results:
    print(
        f"{result['scenario_id']} | "
        f"Min TTC: {result['min_ttc_s']:.3f} s | "
        f"Detection: {result['detection_rate']:.1%} | "
        f"AEB Precision: {result['aeb_precision']:.1%} | "
        f"AEB Recall: {result['aeb_recall']:.1%} | "
        f"AEB F1: {result['aeb_f1']:.1%} | "
        f"FP: {result['aeb_fp']} | "
        f"FN: {result['aeb_fn']}"
    )