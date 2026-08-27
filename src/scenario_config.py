"""
Scenario configuration for the synthetic pedestrian AEB dataset.

The values in this file are project-defined simulation parameters.
They are NOT official Toyota, Euro NCAP, UNECE, or regulatory requirements.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ScenarioConfig:
    """Configuration for one synthetic pedestrian-AEB scenario."""

    scenario_id: str
    scenario_name: str
    objective: str

    # Ego vehicle
    initial_vehicle_speed_kmh: float
    vehicle_speed_profile: str

    # Pedestrian
    pedestrian_behavior: str
    pedestrian_speed_ms: float
    pedestrian_start_lateral_m: float
    pedestrian_start_longitudinal_m: float

    # Environment
    weather: str
    lighting: str
    road_condition: str
    road_type: str
    traffic_density: str
    visibility: str

    # Scenario characteristics
    risk_type: str


SCENARIOS: Dict[str, ScenarioConfig] = {

    "P01": ScenarioConfig(
        scenario_id="P01",
        scenario_name="Normal Crossing",
        objective="Baseline pedestrian detection and AEB performance",
        initial_vehicle_speed_kmh=40.0,
        vehicle_speed_profile="constant",
        pedestrian_behavior="normal_crossing",
        pedestrian_speed_ms=1.4,
        pedestrian_start_lateral_m=-4.0,
        pedestrian_start_longitudinal_m=15.0,
        weather="dry",
        lighting="day",
        road_condition="dry",
        road_type="urban",
        traffic_density="medium",
        visibility="clear",
        risk_type="controlled_crossing",
    ),

    "P02": ScenarioConfig(
        scenario_id="P02",
        scenario_name="Sudden Crossing",
        objective="Evaluate reaction to rapid pedestrian entry",
        initial_vehicle_speed_kmh=40.0,
        vehicle_speed_profile="approach_then_brake",
        pedestrian_behavior="sudden_crossing",
        pedestrian_speed_ms=2.2,
        pedestrian_start_lateral_m=-6.0,
        pedestrian_start_longitudinal_m=22.0,
        weather="dry",
        lighting="day",
        road_condition="dry",
        road_type="urban",
        traffic_density="medium",
        visibility="clear",
        risk_type="high_risk_crossing",
    ),

    "P03": ScenarioConfig(
        scenario_id="P03",
        scenario_name="Night Crossing",
        objective="Evaluate pedestrian detection under low-light conditions",
        initial_vehicle_speed_kmh=40.0,
        vehicle_speed_profile="constant",
        pedestrian_behavior="normal_crossing",
        pedestrian_speed_ms=1.4,
        pedestrian_start_lateral_m=-4.0,
        pedestrian_start_longitudinal_m=30.0,
        weather="dry",
        lighting="night",
        road_condition="dry",
        road_type="urban",
        traffic_density="low",
        visibility="partial",
        risk_type="environmental_degradation",
    ),

    "P04": ScenarioConfig(
        scenario_id="P04",
        scenario_name="Rain Crossing",
        objective="Evaluate performance during rain and wet-road conditions",
        initial_vehicle_speed_kmh=40.0,
        vehicle_speed_profile="constant",
        pedestrian_behavior="normal_crossing",
        pedestrian_speed_ms=1.4,
        pedestrian_start_lateral_m=-4.0,
        pedestrian_start_longitudinal_m=30.0,
        weather="rain",
        lighting="day",
        road_condition="wet",
        road_type="urban",
        traffic_density="medium",
        visibility="partial",
        risk_type="environmental_degradation",
    ),

    "P05": ScenarioConfig(
        scenario_id="P05",
        scenario_name="Partial Occlusion",
        objective="Evaluate detection with partially obstructed pedestrian visibility",
        initial_vehicle_speed_kmh=35.0,
        vehicle_speed_profile="approach_then_brake",
        pedestrian_behavior="occluded_crossing",
        pedestrian_speed_ms=1.4,
        pedestrian_start_lateral_m=-4.0,
        pedestrian_start_longitudinal_m=25.0,
        weather="dry",
        lighting="day",
        road_condition="dry",
        road_type="urban",
        traffic_density="high",
        visibility="partial",
        risk_type="perception_challenge",
    ),

    "P06": ScenarioConfig(
        scenario_id="P06",
        scenario_name="Outside Path",
        objective="Evaluate false detections and unnecessary intervention",
        initial_vehicle_speed_kmh=40.0,
        vehicle_speed_profile="constant",
        pedestrian_behavior="outside_vehicle_path",
        pedestrian_speed_ms=1.4,
        pedestrian_start_lateral_m=5.0,
        pedestrian_start_longitudinal_m=30.0,
        weather="dry",
        lighting="day",
        road_condition="dry",
        road_type="urban",
        traffic_density="medium",
        visibility="clear",
        risk_type="non_threatening",
    ),

    "P07": ScenarioConfig(
        scenario_id="P07",
        scenario_name="Multiple Pedestrians",
        objective="Evaluate handling of multiple pedestrian targets",
        initial_vehicle_speed_kmh=35.0,
        vehicle_speed_profile="approach_then_brake",
        pedestrian_behavior="multiple_crossing",
        pedestrian_speed_ms=1.4,
        pedestrian_start_lateral_m=-5.0,
        pedestrian_start_longitudinal_m=28.0,
        weather="dry",
        lighting="day",
        road_condition="dry",
        road_type="urban",
        traffic_density="high",
        visibility="clear",
        risk_type="multi_target",
    ),

    "P08": ScenarioConfig(
        scenario_id="P08",
        scenario_name="High-Speed Approach",
        objective="Evaluate collision risk and warning timing at high speed",
        initial_vehicle_speed_kmh=80.0,
        vehicle_speed_profile="constant_then_brake",
        pedestrian_behavior="normal_crossing",
        pedestrian_speed_ms=1.4,
        pedestrian_start_lateral_m=-4.0,
        pedestrian_start_longitudinal_m=45.0,
        weather="dry",
        lighting="day",
        road_condition="dry",
        road_type="rural",
        traffic_density="low",
        visibility="clear",
        risk_type="high_speed",
    ),

    "P09": ScenarioConfig(
        scenario_id="P09",
        scenario_name="Fog / Low Visibility",
        objective="Evaluate perception under degraded visibility",
        initial_vehicle_speed_kmh=35.0,
        vehicle_speed_profile="constant",
        pedestrian_behavior="normal_crossing",
        pedestrian_speed_ms=1.4,
        pedestrian_start_lateral_m=-4.0,
        pedestrian_start_longitudinal_m=30.0,
        weather="fog",
        lighting="day",
        road_condition="wet",
        road_type="rural",
        traffic_density="low",
        visibility="occluded",
        risk_type="environmental_degradation",
    ),

    "P10": ScenarioConfig(
        scenario_id="P10",
        scenario_name="Safe Avoidance",
        objective="Evaluate avoidance of unnecessary AEB intervention",
        initial_vehicle_speed_kmh=40.0,
        vehicle_speed_profile="constant",
        pedestrian_behavior="safe_avoidance",
        pedestrian_speed_ms=1.2,
        pedestrian_start_lateral_m=-5.0,
        pedestrian_start_longitudinal_m=35.0,
        weather="dry",
        lighting="day",
        road_condition="dry",
        road_type="urban",
        traffic_density="medium",
        visibility="clear",
        risk_type="safe_scenario",
    ),
}


def get_scenario(scenario_id: str) -> ScenarioConfig:
    """
    Return the configuration for a scenario.

    Parameters
    ----------
    scenario_id:
        Scenario identifier such as 'P01'.

    Returns
    -------
    ScenarioConfig
        Configuration associated with the scenario.

    Raises
    ------
    KeyError
        If the scenario ID is not defined.
    """
    try:
        return SCENARIOS[scenario_id]
    except KeyError as exc:
        raise KeyError(
            f"Unknown scenario_id: {scenario_id}. "
            f"Available scenarios: {list(SCENARIOS)}"
        ) from exc