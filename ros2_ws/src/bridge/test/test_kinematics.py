"""Tests for the pure Twist to wheel command conversion."""

import pytest

from bridge.kinematics import twist_to_wheels


@pytest.mark.parametrize(
    "linear_x, angular_z, expected",
    [
        (1, 0, (100, 100)),
        (-1, 0, (-100, -100)),
        (0, 1, (-100, 100)),
        (0, -1, (100, -100)),
        (0, 0, (0, 0)),
        (1, 1, (0, 100)),
        (2, -2, (100, 0)),
    ],
)
def test_twist_to_wheels(linear_x, angular_z, expected):
    assert twist_to_wheels(linear_x, angular_z) == expected
