"""
Synthetic Autonomous Emergency Braking (AEB) model.

This module converts simulated perception and TTC information
into a synthetic automatic braking output.

All numerical values are synthetic project assumptions.
They are not official OEM, Euro NCAP, UNECE, or regulatory requirements.
"""


from __future__ import annotations

import numpy as np


DEFAULT_BRAKING_TTC_THRESHOLD_SECONDS = 1.5


def determine_braking_trigger(
    pedestrian_detected: bool,
    pedestrian_in_path: bool,
    ttc_seconds: float,
    braking_ttc_threshold_seconds: float = (
        DEFAULT_BRAKING_TTC_THRESHOLD_SECONDS
    ),
) -> bool:
    """
    Determine whether the synthetic AEB should trigger braking.

    Braking is triggered when:
    1. A pedestrian is detected.
    2. The pedestrian is in the ego vehicle's path.
    3. TTC is finite.
    4. TTC is at or below the braking threshold.
    """

    if braking_ttc_threshold_seconds <= 0:
        raise ValueError(
            "braking_ttc_threshold_seconds must be greater than zero."
        )

    if not isinstance(pedestrian_detected, (bool, np.bool_)):
        raise TypeError(
            "pedestrian_detected must be boolean."
        )

    if not isinstance(pedestrian_in_path, (bool, np.bool_)):
        raise TypeError(
            "pedestrian_in_path must be boolean."
        )

    if not np.isfinite(ttc_seconds):
        return False

    return bool(
        pedestrian_detected
        and pedestrian_in_path
        and ttc_seconds <= braking_ttc_threshold_seconds
    )