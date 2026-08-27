"""
Synthetic Forward Collision Warning (FCW) model.

This module converts simulated perception and TTC information
into a synthetic warning output.

All numerical values are synthetic project assumptions.
They are not official OEM, Euro NCAP, UNECE, or regulatory requirements.
"""

from __future__ import annotations

import numpy as np


DEFAULT_WARNING_TTC_THRESHOLD_SECONDS = 2.5


def determine_warning_trigger(
    pedestrian_detected: bool,
    pedestrian_in_path: bool,
    ttc_seconds: float,
    warning_ttc_threshold_seconds: float = (
        DEFAULT_WARNING_TTC_THRESHOLD_SECONDS
    ),
) -> bool:
    """
    Determine whether the synthetic FCW should trigger a warning.

    A warning is triggered when:
    1. A pedestrian is detected.
    2. TTC is finite.
    3. TTC is at or below the warning threshold.
    """

    if warning_ttc_threshold_seconds <= 0:
        raise ValueError(
            "warning_ttc_threshold_seconds must be greater than zero."
        )

    if not isinstance(pedestrian_detected, (bool, np.bool_)):
        raise TypeError(
            "pedestrian_detected must be boolean."
        )

    if not np.isfinite(ttc_seconds):
        return False

    return bool(
        pedestrian_detected
        and pedestrian_in_path
        and ttc_seconds <= warning_ttc_threshold_seconds
    )

def apply_warning_latency(
    warning_signal: np.ndarray,
    latency_seconds: float,
    frequency_hz: float,
) -> np.ndarray:
    """
    Apply a fixed temporal delay to an FCW warning signal.

    Parameters
    ----------
    warning_signal:
        Boolean FCW signal over time.

    latency_seconds:
        Synthetic warning-system latency.

    frequency_hz:
        Telemetry sampling frequency.

    Returns
    -------
    np.ndarray
        Delayed boolean warning signal.
    """

    warning_signal = np.asarray(warning_signal, dtype=bool)

    if latency_seconds < 0:
        raise ValueError(
            "latency_seconds cannot be negative."
        )

    if frequency_hz <= 0:
        raise ValueError(
            "frequency_hz must be greater than zero."
        )

    delay_samples = int(round(latency_seconds * frequency_hz))

    if delay_samples == 0:
        return warning_signal.copy()

    delayed_signal = np.zeros_like(warning_signal, dtype=bool)

    if delay_samples < len(warning_signal):
        delayed_signal[delay_samples:] = (
            warning_signal[:-delay_samples]
        )

    return delayed_signal