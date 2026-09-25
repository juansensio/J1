"""Convert planar velocity commands to normalized wheel commands."""


def twist_to_wheels(linear_x, angular_z):
    """Return left and right wheel commands in the range [-100, 100]."""
    forward = max(-1.0, min(1.0, linear_x))
    turn = max(-1.0, min(1.0, angular_z))

    left = forward - turn
    right = forward + turn

    scale = max(1.0, abs(left), abs(right))

    left /= scale
    right /= scale

    return round(left * 100), round(right * 100)
