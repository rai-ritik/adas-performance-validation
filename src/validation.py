"""
Synthetic ADAS validation utilities.

This module compares ADAS outputs against independent
ground-truth signals.

All values are synthetic project assumptions and are not
official automotive/OEM/regulatory specifications.
"""

from __future__ import annotations

import numpy as np


def classify_binary_result(
    ground_truth: bool,
    prediction: bool,
) -> str:
    """
    Classify a binary ADAS result as TP, TN, FP, or FN.

    Parameters
    ----------
    ground_truth:
        Expected result from the physical ground-truth model.

    prediction:
        Result produced by the simulated ADAS system.

    Returns
    -------
    str
        One of: TP, TN, FP, FN.
    """

    if not isinstance(ground_truth, (bool, np.bool_)):
        raise TypeError(
            "ground_truth must be boolean."
        )

    if not isinstance(prediction, (bool, np.bool_)):
        raise TypeError(
            "prediction must be boolean."
        )

    if ground_truth and prediction:
        return "TP"

    if not ground_truth and not prediction:
        return "TN"

    if not ground_truth and prediction:
        return "FP"

    return "FN"

def calculate_binary_metrics(
    ground_truth: np.ndarray,
    prediction: np.ndarray,
) -> dict[str, float]:
    """
    Calculate basic binary classification metrics.

    Returns precision, recall, and F1 score.

    All metrics are calculated from the supplied
    ground-truth and ADAS prediction arrays.
    """

    ground_truth = np.asarray(ground_truth, dtype=bool)
    prediction = np.asarray(prediction, dtype=bool)

    if ground_truth.shape != prediction.shape:
        raise ValueError(
            "ground_truth and prediction must have the same shape."
        )

    true_positive = np.sum(
        ground_truth & prediction
    )

    false_positive = np.sum(
        ~ground_truth & prediction
    )

    false_negative = np.sum(
        ground_truth & ~prediction
    )

    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative

    precision = (
        true_positive / precision_denominator
        if precision_denominator > 0
        else 0.0
    )

    recall = (
        true_positive / recall_denominator
        if recall_denominator > 0
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }