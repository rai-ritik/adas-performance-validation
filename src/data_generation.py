"""
Synthetic ego-vehicle telemetry generation.


This module currently generates only ego-vehicle motion.
Pedestrian trajectories, collision risk, ADAS outputs, and
failure injection will be added in later steps.


All values are synthetic project assumptions and are not
official automotive/OEM/regulatory specifications.
"""


from __future__ import annotations


from datetime import datetime, timedelta, timezone


import numpy as np
import pandas as pd


from src.scenario_config import ScenarioConfig



# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------


DEFAULT_FREQUENCY_HZ = 10.0
DEFAULT_DURATION_SECONDS = 20.0



# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------



def kmh_to_ms(speed_kmh: float | np.ndarray) -> float | np.ndarray:
    """Convert speed from km/h to m/s."""
    return speed_kmh / 3.6



def ms_to_kmh(speed_ms: float | np.ndarray) -> float | np.ndarray:
    """Convert speed from m/s to km/h."""
    return speed_ms * 3.6



def create_timestamps(
    duration_seconds: float = DEFAULT_DURATION_SECONDS,
    frequency_hz: float = DEFAULT_FREQUENCY_HZ,
    start_time: datetime | None = None,
) -> pd.DatetimeIndex:
    """
    Create regularly spaced telemetry timestamps.


    Parameters
    ----------
    duration_seconds:
        Duration of the simulated scenario.


    frequency_hz:
        Telemetry sampling frequency.


    start_time:
        Scenario start timestamp. If None, a UTC timestamp is used.


    Returns
    -------
    pandas.DatetimeIndex
        Timestamp sequence.
    """


    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be greater than zero.")


    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be greater than zero.")


    if start_time is None:
        start_time = datetime.now(timezone.utc)


    dt = 1.0 / frequency_hz
    number_of_samples = int(duration_seconds * frequency_hz)


    return pd.date_range(
        start=start_time,
        periods=number_of_samples,
        freq=pd.to_timedelta(dt, unit="s"),
    )



# ---------------------------------------------------------------------
# Vehicle motion profiles
# ---------------------------------------------------------------------



def generate_acceleration_profile(
    scenario: ScenarioConfig,
    number_of_samples: int,
    frequency_hz: float,
) -> np.ndarray:
    """
    Generate a synthetic acceleration profile for a scenario.

    The profile is scenario-dependent and designed to produce
    physically plausible ego-vehicle motion for the project.

    These are synthetic project assumptions, not production
    automotive braking specifications.
    """

    if number_of_samples <= 0:
        raise ValueError("number_of_samples must be greater than zero.")

    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be greater than zero.")

    acceleration = np.zeros(number_of_samples)

    profile = scenario.vehicle_speed_profile

    if profile == "constant":
        # Small natural variation around zero acceleration.
        acceleration = np.random.normal(
            loc=0.0,
            scale=0.08,
            size=number_of_samples,
        )

    elif profile == "approach_then_brake":
        brake_start = int(number_of_samples * 0.50)
        strong_brake_start = int(number_of_samples * 0.65)

        # Approach phase.
        acceleration[:brake_start] = np.random.normal(
            loc=-0.03,
            scale=0.05,
            size=brake_start,
        )

        # Initial braking.
        initial_brake_end = strong_brake_start

        acceleration[brake_start:initial_brake_end] = np.linspace(
            -0.5,
            -2.5,
            initial_brake_end - brake_start,
        )

        # Stronger braking.
        acceleration[strong_brake_start:] = np.linspace(
            -2.5,
            -3.0,
            number_of_samples - strong_brake_start,
        )

    elif profile == "constant_then_brake":
        brake_start = int(number_of_samples * 0.60)
        stabilization_start = int(number_of_samples * 0.80)

        # Constant-speed approach.
        acceleration[:brake_start] = np.random.normal(
            loc=0.0,
            scale=0.05,
            size=brake_start,
        )

        # Braking phase.
        acceleration[brake_start:stabilization_start] = np.linspace(
            -1.0,
            -3.0,
            stabilization_start - brake_start,
        )

        # Reduce braking toward the end rather than continuing
        # to accelerate the vehicle toward an impossible negative speed.
        acceleration[stabilization_start:] = np.linspace(
            -0.8,
            0.0,
            number_of_samples - stabilization_start,
        )

    else:
        raise ValueError(
            f"Unsupported vehicle speed profile: {profile}"
        )

    return acceleration



def generate_vehicle_motion(
    scenario: ScenarioConfig,
    duration_seconds: float = DEFAULT_DURATION_SECONDS,
    frequency_hz: float = DEFAULT_FREQUENCY_HZ,
    start_time: datetime | None = None,
) -> pd.DataFrame:
    """
    Generate a timestamped ego-vehicle motion profile.

    Speed is generated first according to the scenario profile.
    Acceleration is then derived from the speed trajectory.

    These are synthetic project assumptions and are not
    production automotive/OEM/regulatory specifications.
    """

    timestamps = create_timestamps(
        duration_seconds=duration_seconds,
        frequency_hz=frequency_hz,
        start_time=start_time,
    )

    number_of_samples = len(timestamps)

    dt = 1.0 / frequency_hz

    initial_speed_kmh = scenario.initial_vehicle_speed_kmh

    # -------------------------------------------------------------
    # Generate desired speed trajectory
    # -------------------------------------------------------------

    speed_kmh = np.full(
        number_of_samples,
        initial_speed_kmh,
        dtype=float,
    )

    profile = scenario.vehicle_speed_profile

    if profile == "constant":
        # Small variation around the initial speed.
        speed_kmh += np.random.normal(
            loc=0.0,
            scale=0.2,
            size=number_of_samples,
        )

        speed_kmh = np.maximum(speed_kmh, 0.0)

    elif profile == "approach_then_brake":
        brake_start = int(number_of_samples * 0.50)

        # Before braking: approximately constant speed.
        speed_kmh[:brake_start] = (
            initial_speed_kmh
            + np.random.normal(
                loc=0.0,
                scale=0.15,
                size=brake_start,
            )
        )

        # Controlled reduction to a low but non-zero speed.
        final_speed_kmh = max(initial_speed_kmh * 0.35, 10.0)

        speed_kmh[brake_start:] = np.linspace(
            initial_speed_kmh,
            final_speed_kmh,
            number_of_samples - brake_start,
        )

    elif profile == "constant_then_brake":
        brake_start = int(number_of_samples * 0.60)

        # Constant-speed approach.
        speed_kmh[:brake_start] = (
            initial_speed_kmh
            + np.random.normal(
                loc=0.0,
                scale=0.15,
                size=brake_start,
            )
        )

        # Controlled braking to a non-zero terminal speed.
        final_speed_kmh = max(initial_speed_kmh * 0.30, 10.0)

        speed_kmh[brake_start:] = np.linspace(
            initial_speed_kmh,
            final_speed_kmh,
            number_of_samples - brake_start,
        )

    else:
        raise ValueError(
            f"Unsupported vehicle speed profile: {profile}"
        )

    # Prevent numerical noise from producing invalid speeds.
    speed_kmh = np.maximum(speed_kmh, 0.0)

    # -------------------------------------------------------------
    # Derive acceleration from speed
    # -------------------------------------------------------------

    speed_ms = kmh_to_ms(speed_kmh)

    acceleration = np.gradient(
        speed_ms,
        dt,
    )

    # -------------------------------------------------------------
    # Yaw rate
    # -------------------------------------------------------------

    yaw_rate = np.random.normal(
        loc=0.0,
        scale=0.05,
        size=number_of_samples,
    )

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "vehicle_speed_kmh": speed_kmh,
            "vehicle_acceleration_ms2": acceleration,
            "vehicle_yaw_rate_dps": yaw_rate,
        }
    )
def generate_pedestrian_lateral_position(
    scenario: ScenarioConfig,
    number_of_samples: int,
    frequency_hz: float,
) -> np.ndarray:
    """
    Generate the pedestrian's lateral position over time.

    Pedestrian movement is based on the configured walking speed
    and the scenario-specific behavior.
    """

    if number_of_samples <= 0:
        raise ValueError("number_of_samples must be greater than zero.")

    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be greater than zero.")

    start_position = scenario.pedestrian_start_lateral_m
    pedestrian_speed = scenario.pedestrian_speed_ms
    behavior = scenario.pedestrian_behavior

    dt = 1.0 / frequency_hz

    lateral_position = np.full(
        number_of_samples,
        start_position,
        dtype=float,
    )

    if pedestrian_speed < 0:
        raise ValueError("pedestrian_speed_ms cannot be negative.")

    if behavior == "normal_crossing":
        for i in range(1, number_of_samples):
            lateral_position[i] = (
                lateral_position[i - 1]
                + pedestrian_speed * dt
            )

            if lateral_position[i] >= abs(start_position):
                lateral_position[i:] = abs(start_position)
                break

    elif behavior == "sudden_crossing":
        entry_index = int(number_of_samples * 0.45)

        for i in range(entry_index + 1, number_of_samples):
            lateral_position[i] = (
                lateral_position[i - 1]
                + pedestrian_speed * dt
            )

            if lateral_position[i] >= abs(start_position):
                lateral_position[i:] = abs(start_position)
                break

    elif behavior == "occluded_crossing":
        for i in range(1, number_of_samples):
            lateral_position[i] = (
                lateral_position[i - 1]
                + pedestrian_speed * dt
            )

            if lateral_position[i] >= abs(start_position):
                lateral_position[i:] = abs(start_position)
                break

    elif behavior == "outside_vehicle_path":
        lateral_position = np.full(
            number_of_samples,
            start_position,
            dtype=float,
        )

    elif behavior == "multiple_crossing":
        for i in range(1, number_of_samples):
            lateral_position[i] = (
                lateral_position[i - 1]
                + pedestrian_speed * dt
            )

            if lateral_position[i] >= abs(start_position):
                lateral_position[i:] = abs(start_position)
                break

    elif behavior == "safe_avoidance":
        entry_index = int(number_of_samples * 0.45)
        avoidance_index = int(number_of_samples * 0.55)

        lateral_position[:entry_index] = start_position

        for i in range(entry_index, avoidance_index):
            lateral_position[i] = (
            lateral_position[i - 1]
            + pedestrian_speed * dt
            )

    # Move away from the ego path before entering it.
        lateral_position[avoidance_index:] = np.linspace(
        lateral_position[avoidance_index - 1],
        2.5,
        number_of_samples - avoidance_index,
        )
    
    else:
        raise ValueError(
            f"Unsupported pedestrian behavior: {behavior}"
        )

    return lateral_position

def generate_pedestrian_longitudinal_position(
    scenario: ScenarioConfig,
    number_of_samples: int,
    frequency_hz: float,
) -> np.ndarray:
    """
    Generate the pedestrian's longitudinal position over time.

    The position represents the pedestrian's location along
    the ego vehicle's direction of travel.
    """

    if number_of_samples <= 0:
        raise ValueError("number_of_samples must be greater than zero.")

    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be greater than zero.")

    start_position = scenario.pedestrian_start_longitudinal_m
    behavior = scenario.pedestrian_behavior

    longitudinal_position = np.full(
        number_of_samples,
        start_position,
        dtype=float,
    )

    if behavior in {
        "normal_crossing",
        "sudden_crossing",
        "occluded_crossing",
        "multiple_crossing",
    }:
        # For a crossing scenario, keep the pedestrian approximately
        # at the same longitudinal location while it crosses laterally.
        longitudinal_position = np.full(
            number_of_samples,
            start_position,
            dtype=float,
        )

    elif behavior == "outside_vehicle_path":
        # Pedestrian remains at its longitudinal location.
        longitudinal_position = np.full(
            number_of_samples,
            start_position,
            dtype=float,
        )

    elif behavior == "safe_avoidance":
        # Keep the longitudinal location approximately constant.
        # The avoidance behavior is represented primarily through
        # lateral movement at this stage.
        longitudinal_position = np.full(
            number_of_samples,
            start_position,
            dtype=float,
        )

    else:
        raise ValueError(
            f"Unsupported pedestrian behavior: {behavior}"
        )

    return longitudinal_position

def calculate_pedestrian_distance(
    lateral_position_m: np.ndarray,
    longitudinal_position_m: np.ndarray,
) -> np.ndarray:
    """
    Calculate geometric distance between the ego reference point
    and the pedestrian using lateral and longitudinal position.

    Distance is calculated using the Euclidean distance formula.
    """

    lateral_position_m = np.asarray(lateral_position_m, dtype=float)
    longitudinal_position_m = np.asarray(
        longitudinal_position_m,
        dtype=float,
    )

    if lateral_position_m.shape != longitudinal_position_m.shape:
        raise ValueError(
            "Lateral and longitudinal position arrays "
            "must have the same shape."
        )

    return np.sqrt(
        lateral_position_m**2
        + longitudinal_position_m**2
    )

def calculate_relative_closing_speed(
    vehicle_speed_kmh: np.ndarray,
    pedestrian_longitudinal_position_m: np.ndarray,
    frequency_hz: float,
) -> np.ndarray:
    """
    Calculate longitudinal relative closing speed.

    Positive values indicate that the ego vehicle and pedestrian
    are closing in the longitudinal direction.

    Negative values indicate separation.
    """

    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be greater than zero.")

    vehicle_speed_kmh = np.asarray(
        vehicle_speed_kmh,
        dtype=float,
    )

    pedestrian_longitudinal_position_m = np.asarray(
        pedestrian_longitudinal_position_m,
        dtype=float,
    )

    if vehicle_speed_kmh.shape != pedestrian_longitudinal_position_m.shape:
        raise ValueError(
            "Vehicle speed and pedestrian longitudinal position "
            "arrays must have the same shape."
        )

    # Convert ego speed to m/s.
    vehicle_speed_ms = vehicle_speed_kmh / 3.6

    # Calculate pedestrian longitudinal velocity.
    dt = 1.0 / frequency_hz

    pedestrian_velocity_ms = np.gradient(
        pedestrian_longitudinal_position_m,
        dt,
    )

    # Positive = closing.
    relative_closing_speed_ms = (
        vehicle_speed_ms - pedestrian_velocity_ms
    )

    return relative_closing_speed_ms

def calculate_ttc(
    pedestrian_distance_m: np.ndarray,
    relative_closing_speed_ms: np.ndarray,
) -> np.ndarray:
    """
    Calculate simplified Time-to-Collision (TTC).

    TTC is defined only when the ego vehicle is closing on
    the pedestrian with a positive relative closing speed.
    """

    pedestrian_distance_m = np.asarray(
        pedestrian_distance_m,
        dtype=float,
    )

    relative_closing_speed_ms = np.asarray(
        relative_closing_speed_ms,
        dtype=float,
    )

    if pedestrian_distance_m.shape != relative_closing_speed_ms.shape:
        raise ValueError(
            "Distance and relative closing speed arrays "
            "must have the same shape."
        )

    ttc_seconds = np.full(
        pedestrian_distance_m.shape,
        np.nan,
        dtype=float,
    )

    closing = relative_closing_speed_ms > 0

    ttc_seconds[closing] = (
        pedestrian_distance_m[closing]
        / relative_closing_speed_ms[closing]
    )

    return ttc_seconds

def determine_collision_risk(
    lateral_position_m: np.ndarray,
    relative_closing_speed_ms: np.ndarray,
    ttc_seconds: np.ndarray,
    path_threshold_m: float = 1.0,
    ttc_threshold_seconds: float = 3.0,
) -> np.ndarray:
    """
    Determine synthetic ground-truth collision risk.

    A collision risk exists when:
    1. The pedestrian is inside the ego vehicle's path.
    2. The ego vehicle is closing on the pedestrian.
    3. TTC is at or below the project-defined threshold.

    Thresholds are synthetic project assumptions.
    """

    lateral_position_m = np.asarray(
        lateral_position_m,
        dtype=float,
    )

    relative_closing_speed_ms = np.asarray(
        relative_closing_speed_ms,
        dtype=float,
    )

    ttc_seconds = np.asarray(
        ttc_seconds,
        dtype=float,
    )

    if not (
        lateral_position_m.shape
        == relative_closing_speed_ms.shape
        == ttc_seconds.shape
    ):
        raise ValueError(
            "Lateral position, relative closing speed, and TTC "
            "arrays must have the same shape."
        )

    pedestrian_in_path = (
        np.abs(lateral_position_m) <= path_threshold_m
    )

    vehicle_closing = relative_closing_speed_ms > 0

    critical_ttc = (
        np.isfinite(ttc_seconds)
        & (ttc_seconds <= ttc_threshold_seconds)
    )

    collision_risk = (
        pedestrian_in_path
        & vehicle_closing
        & critical_ttc
    )

    return collision_risk


def determine_warning_required(
    lateral_position_m: np.ndarray,
    relative_closing_speed_ms: np.ndarray,
    ttc_seconds: np.ndarray,
    path_threshold_m: float = 1.0,
    warning_ttc_threshold_seconds: float = 2.5,
) -> np.ndarray:
    """
    Determine whether a warning is required according to
    the project's synthetic ground-truth rules.

    A warning is required when:
    1. The pedestrian is inside the ego vehicle's path.
    2. The ego vehicle is closing on the pedestrian.
    3. TTC is at or below the project-defined warning threshold.

    Thresholds are synthetic project assumptions.
    """

    lateral_position_m = np.asarray(
        lateral_position_m,
        dtype=float,
    )

    relative_closing_speed_ms = np.asarray(
        relative_closing_speed_ms,
        dtype=float,
    )

    ttc_seconds = np.asarray(
        ttc_seconds,
        dtype=float,
    )

    if not (
        lateral_position_m.shape
        == relative_closing_speed_ms.shape
        == ttc_seconds.shape
    ):
        raise ValueError(
            "Lateral position, relative closing speed, and TTC "
            "arrays must have the same shape."
        )

    pedestrian_in_path = (
        np.abs(lateral_position_m) <= path_threshold_m
    )

    vehicle_closing = relative_closing_speed_ms > 0

    warning_ttc_reached = (
        np.isfinite(ttc_seconds)
        & (ttc_seconds <= warning_ttc_threshold_seconds)
    )

    warning_required = (
        pedestrian_in_path
        & vehicle_closing
        & warning_ttc_reached
    )

    return warning_required

def determine_braking_required(
    lateral_position_m: np.ndarray,
    relative_closing_speed_ms: np.ndarray,
    ttc_seconds: np.ndarray,
    path_threshold_m: float = 1.0,
    braking_ttc_threshold_seconds: float = 1.5,
) -> np.ndarray:
    """
    Determine whether AEB braking is required according to
    the project's synthetic ground-truth rules.

    Braking is required when:
    1. The pedestrian is inside the ego vehicle's path.
    2. The ego vehicle is closing on the pedestrian.
    3. TTC is at or below the project-defined braking threshold.

    Thresholds are synthetic project assumptions.
    """

    lateral_position_m = np.asarray(
        lateral_position_m,
        dtype=float,
    )

    relative_closing_speed_ms = np.asarray(
        relative_closing_speed_ms,
        dtype=float,
    )

    ttc_seconds = np.asarray(
        ttc_seconds,
        dtype=float,
    )

    if not (
        lateral_position_m.shape
        == relative_closing_speed_ms.shape
        == ttc_seconds.shape
    ):
        raise ValueError(
            "Lateral position, relative closing speed, and TTC "
            "arrays must have the same shape."
        )

    pedestrian_in_path = (
        np.abs(lateral_position_m) <= path_threshold_m
    )

    vehicle_closing = relative_closing_speed_ms > 0

    braking_ttc_reached = (
        np.isfinite(ttc_seconds)
        & (ttc_seconds <= braking_ttc_threshold_seconds)
    )

    braking_required = (
        pedestrian_in_path
        & vehicle_closing
        & braking_ttc_reached
    )

    return braking_required

def generate_scenario_telemetry(
    scenario: ScenarioConfig,
    duration_seconds: float = DEFAULT_DURATION_SECONDS,
    frequency_hz: float = DEFAULT_FREQUENCY_HZ,
    start_time: datetime | None = None,
) -> pd.DataFrame:
    """
    Generate the physical telemetry and ground-truth state
    for one pedestrian-AEB scenario.

    This function combines the previously implemented components.
    ADAS perception, warning output, braking output, and failure
    injection will be added in later stages.
    """

    # -------------------------------------------------------------
    # 1. Ego vehicle motion
    # -------------------------------------------------------------

    vehicle_df = generate_vehicle_motion(
        scenario=scenario,
        duration_seconds=duration_seconds,
        frequency_hz=frequency_hz,
        start_time=start_time,
    )

    number_of_samples = len(vehicle_df)

    # -------------------------------------------------------------
    # 2. Pedestrian trajectory
    # -------------------------------------------------------------

    lateral_position = generate_pedestrian_lateral_position(
        scenario=scenario,
        number_of_samples=number_of_samples,
        frequency_hz=frequency_hz,
    )

    longitudinal_position = generate_pedestrian_longitudinal_position(
        scenario=scenario,
        number_of_samples=number_of_samples,
        frequency_hz=frequency_hz,
    )

    # -------------------------------------------------------------
    # 3. Geometric distance
    # -------------------------------------------------------------

    pedestrian_distance = calculate_pedestrian_distance(
        lateral_position_m=lateral_position,
        longitudinal_position_m=longitudinal_position,
    )

    # -------------------------------------------------------------
    # 4. Relative closing speed
    # -------------------------------------------------------------

    relative_closing_speed = calculate_relative_closing_speed(
        vehicle_speed_kmh=vehicle_df[
            "vehicle_speed_kmh"
        ].to_numpy(),
        pedestrian_longitudinal_position_m=longitudinal_position,
        frequency_hz=frequency_hz,
    )

    # -------------------------------------------------------------
    # 5. TTC
    # -------------------------------------------------------------

    ttc_seconds = calculate_ttc(
        pedestrian_distance_m=pedestrian_distance,
        relative_closing_speed_ms=relative_closing_speed,
    )

    # -------------------------------------------------------------
    # 6. Ground-truth collision risk
    # -------------------------------------------------------------

    collision_risk = determine_collision_risk(
        lateral_position_m=lateral_position,
        relative_closing_speed_ms=relative_closing_speed,
        ttc_seconds=ttc_seconds,
    )

    # -------------------------------------------------------------
    # 7. Ground-truth warning requirement
    # -------------------------------------------------------------

    warning_required = determine_warning_required(
        lateral_position_m=lateral_position,
        relative_closing_speed_ms=relative_closing_speed,
        ttc_seconds=ttc_seconds,
    )

    # -------------------------------------------------------------
    # 8. Ground-truth braking requirement
    # -------------------------------------------------------------

    braking_required = determine_braking_required(
        lateral_position_m=lateral_position,
        relative_closing_speed_ms=relative_closing_speed,
        ttc_seconds=ttc_seconds,
    )

    # -------------------------------------------------------------
    # 9. Assemble final scenario dataframe
    # -------------------------------------------------------------

    telemetry = vehicle_df.copy()

    telemetry["scenario_id"] = scenario.scenario_id

    telemetry["pedestrian_lateral_position_m"] = lateral_position
    telemetry["pedestrian_longitudinal_position_m"] = (
        longitudinal_position
    )
    telemetry["pedestrian_distance_m"] = pedestrian_distance
    telemetry["relative_closing_speed_ms"] = relative_closing_speed
    telemetry["ttc_seconds"] = ttc_seconds

    telemetry["ground_truth_pedestrian"] = True
    telemetry["ground_truth_collision_risk"] = collision_risk
    telemetry["ground_truth_warning_required"] = warning_required
    telemetry["ground_truth_braking_required"] = braking_required

    return telemetry