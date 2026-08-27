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
    """


    if number_of_samples <= 0:
        raise ValueError("number_of_samples must be greater than zero.")


    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be greater than zero.")


    acceleration = np.zeros(number_of_samples)


    profile = scenario.vehicle_speed_profile


    if profile == "constant":
        # Small realistic telemetry variation around zero.
        acceleration = np.random.normal(
            loc=0.0,
            scale=0.08,
            size=number_of_samples,
        )


    elif profile == "approach_then_brake":
        brake_start = int(number_of_samples * 0.55)


        # Mild acceleration/deceleration before the event.
        acceleration[:brake_start] = np.random.normal(
            loc=-0.05,
            scale=0.08,
            size=brake_start,
        )


        # Progressive braking.
        acceleration[brake_start:] = np.linspace(
            -0.5,
            -4.0,
            number_of_samples - brake_start,
        )


    elif profile == "constant_then_brake":
        brake_start = int(number_of_samples * 0.60)


        acceleration[:brake_start] = np.random.normal(
            loc=0.0,
            scale=0.08,
            size=brake_start,
        )


        acceleration[brake_start:] = np.linspace(
            -1.0,
            -5.0,
            number_of_samples - brake_start,
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


    Returns
    -------
    pandas.DataFrame
        Columns:


        timestamp
        vehicle_speed_kmh
        vehicle_acceleration_ms2
        vehicle_yaw_rate_dps
    """


    timestamps = create_timestamps(
        duration_seconds=duration_seconds,
        frequency_hz=frequency_hz,
        start_time=start_time,
    )


    number_of_samples = len(timestamps)
    dt = 1.0 / frequency_hz


    initial_speed_ms = kmh_to_ms(
        scenario.initial_vehicle_speed_kmh
    )


    acceleration = generate_acceleration_profile(
        scenario=scenario,
        number_of_samples=number_of_samples,
        frequency_hz=frequency_hz,
    )


    speed_ms = np.zeros(number_of_samples)
    speed_ms[0] = initial_speed_ms


    for i in range(1, number_of_samples):
        speed_ms[i] = speed_ms[i - 1] + acceleration[i - 1] * dt


    # Prevent physically invalid negative speed.
    speed_ms = np.maximum(speed_ms, 0.0)


    speed_kmh = ms_to_kmh(speed_ms)


    # Small yaw-rate variation for telemetry realism.
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