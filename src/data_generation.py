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
        avoidance_index = int(number_of_samples * 0.70)

        lateral_position[:entry_index] = start_position

        for i in range(entry_index, avoidance_index):
            lateral_position[i] = (
                lateral_position[i - 1]
                + pedestrian_speed * dt
            )

        # Move away from the ego path after reaching the
        # avoidance point.
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