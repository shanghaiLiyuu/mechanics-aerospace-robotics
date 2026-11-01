"""Time-optimal-free, smooth point-to-point trajectory primitives."""

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


def minimum_jerk(
    time: ArrayLike,
    duration: float,
    start: ArrayLike | float,
    end: ArrayLike | float,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Evaluate a quintic minimum-jerk trajectory and its first two derivatives."""

    if duration <= 0:
        raise ValueError("duration must be positive")
    times = np.asarray(time, dtype=float)
    if np.any(times < 0) or np.any(times > duration):
        raise ValueError("All sample times must lie within [0, duration]")
    initial = np.asarray(start, dtype=float)
    final = np.asarray(end, dtype=float)
    try:
        displacement = np.broadcast_to(final - initial, np.broadcast_shapes(initial.shape, final.shape))
    except ValueError as exc:
        raise ValueError("start and end cannot be broadcast together") from exc

    tau = times / duration
    blend = 10 * tau**3 - 15 * tau**4 + 6 * tau**5
    blend_rate = (30 * tau**2 - 60 * tau**3 + 30 * tau**4) / duration
    blend_acceleration = (60 * tau - 180 * tau**2 + 120 * tau**3) / duration**2
    shape = times.shape + (1,) * displacement.ndim
    position = initial + blend.reshape(shape) * displacement
    velocity = blend_rate.reshape(shape) * displacement
    acceleration = blend_acceleration.reshape(shape) * displacement
    return position, velocity, acceleration
