import numpy as np

from src.aeb import determine_braking_trigger


def test_aeb_positive():
    assert determine_braking_trigger(
        True, True, 1.2
    ) is True


def test_aeb_outside_threshold():
    assert determine_braking_trigger(
        True, True, 2.0
    ) is False


def test_aeb_missed_detection():
    assert determine_braking_trigger(
        False, True, 1.0
    ) is False


def test_aeb_outside_path():
    assert determine_braking_trigger(
        True, False, 1.0
    ) is False


def test_aeb_invalid_ttc():
    assert determine_braking_trigger(
        True, True, np.nan
    ) is False