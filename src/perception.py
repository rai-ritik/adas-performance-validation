"""
Synthetic ADAS pedestrian perception model.

This module simulates imperfect pedestrian detection.

All numerical values are synthetic project assumptions.
They are not official OEM, Euro NCAP, UNECE, or regulatory requirements.
"""

from __future__ import annotations
import numpy as np
import pandas as pd

def get_visibility_factor(visibility: str) -> float:
    factors = {
        "clear": 1.00,
        "partial": 0.90,
        "occluded": 0.65,
    }

    try:
        return factors[visibility]
    except KeyError:
        raise ValueError(
            f"Unsupported visibility condition: {visibility}"
        )


def get_lighting_factor(lighting: str) -> float:
    factors = {
        "day": 1.00,
        "night": 0.85,
    }

    try:
        return factors[lighting]
    except KeyError:
        raise ValueError(
            f"Unsupported lighting condition: {lighting}"
        )


def get_weather_factor(weather: str) -> float:
    factors = {
        "dry": 1.00,
        "rain": 0.90,
        "fog": 0.75,
    }

    try:
        return factors[weather]
    except KeyError:
        raise ValueError(
            f"Unsupported weather condition: {weather}"
        )
DEFAULT_BASE_DETECTION_PROBABILITY = 0.98


def calculate_detection_probability(
    visibility: str,
    lighting: str,
    weather: str,
    base_probability: float = DEFAULT_BASE_DETECTION_PROBABILITY,
) -> float:
    """
    Calculate synthetic pedestrian detection probability.

    The probability is derived from a base probability and
    environmental perception factors.

    All numerical values are synthetic project assumptions.
    """

    if not 0.0 <= base_probability <= 1.0:
        raise ValueError(
            "base_probability must be between 0 and 1."
        )

    visibility_factor = get_visibility_factor(visibility)
    lighting_factor = get_lighting_factor(lighting)
    weather_factor = get_weather_factor(weather)

    detection_probability = (
        base_probability
        * visibility_factor
        * lighting_factor
        * weather_factor
    )

    return float(
        np.clip(detection_probability, 0.0, 1.0)
    )

def simulate_pedestrian_detection(
    detection_probability: float,
    random_state: np.random.Generator | None = None,
) -> bool:
    """
    Simulate whether the pedestrian is detected.

    A random draw is compared against the detection probability.

    All behavior is part of the synthetic project model.
    """

    if not 0.0 <= detection_probability <= 1.0:
        raise ValueError(
            "detection_probability must be between 0 and 1."
        )

    if random_state is None:
        random_state = np.random.default_rng()

    random_value = random_state.random()

    return bool(random_value < detection_probability)
def generate_detection_confidence(
    detection_probability: float,
    detected: bool,
    random_state: np.random.Generator | None = None,
) -> float:
    """
    Generate synthetic confidence for a pedestrian detection result.

    Confidence depends on the underlying detection probability and
    whether the pedestrian was actually detected.

    All numerical behavior is a synthetic project assumption.
    """

    if not 0.0 <= detection_probability <= 1.0:
        raise ValueError(
            "detection_probability must be between 0 and 1."
        )

    if random_state is None:
        random_state = np.random.default_rng()

    if detected:
        noise = random_state.normal(loc=0.0, scale=0.05)

        confidence = detection_probability + noise
    else:
        noise = random_state.normal(loc=0.0, scale=0.03)

        confidence = 1.0 - detection_probability + noise

    return float(np.clip(confidence, 0.0, 1.0))

def simulate_pedestrian_perception(
    visibility: str,
    lighting: str,
    weather: str,
    number_of_samples: int,
    random_state: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic pedestrian detection and confidence arrays.

    Returns
    -------
    pedestrian_detected:
        Boolean detection result for each sample.

    detection_confidence:
        Confidence value in the range [0, 1] for each sample.
    """

    if number_of_samples <= 0:
        raise ValueError(
            "number_of_samples must be greater than zero."
        )

    if random_state is None:
        random_state = np.random.default_rng()

    detection_probability = calculate_detection_probability(
        visibility=visibility,
        lighting=lighting,
        weather=weather,
    )

    pedestrian_detected = np.array(
        [
            simulate_pedestrian_detection(
                detection_probability,
                random_state,
            )
            for _ in range(number_of_samples)
        ],
        dtype=bool,
    )

    detection_confidence = np.array(
        [
            generate_detection_confidence(
                detection_probability,
                detected,
                random_state,
            )
            for detected in pedestrian_detected
        ],
        dtype=float,
    )

    return pedestrian_detected, detection_confidence