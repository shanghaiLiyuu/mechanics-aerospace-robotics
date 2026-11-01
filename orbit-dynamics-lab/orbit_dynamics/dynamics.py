"""Two-body and J2-perturbed orbital dynamics in an inertial frame."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]

EARTH_MU = 3.986004418e14  # m^3 / s^2
EARTH_RADIUS = 6_378_137.0  # m
EARTH_J2 = 1.08262668e-3


@dataclass(frozen=True)
class OrbitalElements:
    """Classical Keplerian elements using radians for all angles."""

    semi_major_axis: float
    eccentricity: float
    inclination: float
    raan: float
    argument_of_perigee: float
    true_anomaly: float


def _rotation_x(angle: float) -> FloatArray:
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])


def _rotation_z(angle: float) -> FloatArray:
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def kepler_to_state(elements: OrbitalElements, mu: float = EARTH_MU) -> FloatArray:
    """Convert classical elements to an inertial [x, y, z, vx, vy, vz] state."""

    a = elements.semi_major_axis
    e = elements.eccentricity
    nu = elements.true_anomaly
    if a <= 0 or mu <= 0:
        raise ValueError("Semi-major axis and gravitational parameter must be positive")
    if not 0 <= e < 1:
        raise ValueError("This converter supports elliptic orbits with 0 <= e < 1")

    semi_latus_rectum = a * (1.0 - e**2)
    radius = semi_latus_rectum / (1.0 + e * np.cos(nu))
    position_perifocal = radius * np.array([np.cos(nu), np.sin(nu), 0.0])
    velocity_perifocal = np.sqrt(mu / semi_latus_rectum) * np.array(
        [-np.sin(nu), e + np.cos(nu), 0.0]
    )
    rotation = (
        _rotation_z(elements.raan)
        @ _rotation_x(elements.inclination)
        @ _rotation_z(elements.argument_of_perigee)
    )
    return np.r_[rotation @ position_perifocal, rotation @ velocity_perifocal]


def orbital_period(semi_major_axis: float, mu: float = EARTH_MU) -> float:
    """Return the two-body orbital period in seconds."""

    if semi_major_axis <= 0 or mu <= 0:
        raise ValueError("Semi-major axis and gravitational parameter must be positive")
    return float(2.0 * np.pi * np.sqrt(semi_major_axis**3 / mu))


def acceleration(
    position: ArrayLike,
    mu: float = EARTH_MU,
    body_radius: float = EARTH_RADIUS,
    j2: float = 0.0,
) -> FloatArray:
    """Compute central-gravity acceleration with an optional J2 perturbation."""

    r = np.asarray(position, dtype=float)
    if r.shape != (3,):
        raise ValueError("position must have shape (3,)")
    radius = float(np.linalg.norm(r))
    if radius == 0:
        raise ValueError("Acceleration is undefined at the central body centre")
    z_ratio_squared = (r[2] / radius) ** 2
    central = -mu * r / radius**3
    perturbation_factor = 1.5 * j2 * mu * body_radius**2 / radius**5
    perturbation = perturbation_factor * np.array(
        [
            r[0] * (5.0 * z_ratio_squared - 1.0),
            r[1] * (5.0 * z_ratio_squared - 1.0),
            r[2] * (5.0 * z_ratio_squared - 3.0),
        ]
    )
    return central + perturbation


def state_derivative(
    state: ArrayLike,
    mu: float = EARTH_MU,
    body_radius: float = EARTH_RADIUS,
    j2: float = 0.0,
) -> FloatArray:
    """Return [velocity, acceleration] for a six-component state."""

    state_array = np.asarray(state, dtype=float)
    if state_array.shape != (6,):
        raise ValueError("state must have shape (6,)")
    return np.r_[
        state_array[3:],
        acceleration(state_array[:3], mu=mu, body_radius=body_radius, j2=j2),
    ]


def rk4_step(state: FloatArray, step: float, **dynamics_options: float) -> FloatArray:
    """Advance one classical fourth-order Runge-Kutta step."""

    k1 = state_derivative(state, **dynamics_options)
    k2 = state_derivative(state + 0.5 * step * k1, **dynamics_options)
    k3 = state_derivative(state + 0.5 * step * k2, **dynamics_options)
    k4 = state_derivative(state + step * k3, **dynamics_options)
    return state + step * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0


def propagate(
    initial_state: ArrayLike,
    duration: float,
    step: float,
    mu: float = EARTH_MU,
    body_radius: float = EARTH_RADIUS,
    j2: float = 0.0,
) -> tuple[FloatArray, FloatArray]:
    """Propagate an orbit and return uniformly spaced times and states."""

    if duration <= 0 or step <= 0 or step > duration:
        raise ValueError("Require duration >= step > 0")
    state = np.asarray(initial_state, dtype=float)
    if state.shape != (6,):
        raise ValueError("initial_state must have shape (6,)")
    count = int(np.ceil(duration / step))
    times = np.linspace(0.0, duration, count + 1)
    states = np.empty((count + 1, 6), dtype=float)
    states[0] = state
    options = {"mu": mu, "body_radius": body_radius, "j2": j2}
    for index in range(count):
        states[index + 1] = rk4_step(
            states[index], float(times[index + 1] - times[index]), **options
        )
        if np.linalg.norm(states[index + 1, :3]) <= body_radius:
            raise RuntimeError(f"Surface impact detected at t = {times[index + 1]:.1f} s")
    return times, states


def specific_energy(states: ArrayLike, mu: float = EARTH_MU) -> FloatArray:
    """Return two-body specific mechanical energy for one state or a state history."""

    array = np.asarray(states, dtype=float)
    if array.shape[-1] != 6:
        raise ValueError("states must end with a six-component state axis")
    radius = np.linalg.norm(array[..., :3], axis=-1)
    speed = np.linalg.norm(array[..., 3:], axis=-1)
    return 0.5 * speed**2 - mu / radius
