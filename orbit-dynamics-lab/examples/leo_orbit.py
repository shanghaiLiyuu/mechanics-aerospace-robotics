"""Compare two-body and J2-perturbed propagation for an inclined LEO."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np

from orbit_dynamics import (
    EARTH_J2,
    OrbitalElements,
    kepler_to_state,
    orbital_period,
    propagate,
    specific_energy,
)
from orbit_dynamics.visualization import plot_orbit_comparison


def main() -> None:
    elements = OrbitalElements(
        semi_major_axis=7_000_000.0,
        eccentricity=0.001,
        inclination=np.deg2rad(51.6),
        raan=np.deg2rad(20.0),
        argument_of_perigee=np.deg2rad(30.0),
        true_anomaly=0.0,
    )
    initial_state = kepler_to_state(elements)
    period = orbital_period(elements.semi_major_axis)
    duration = 2.0 * period
    times, two_body = propagate(initial_state, duration, step=20.0, j2=0.0)
    _, j2_orbit = propagate(initial_state, duration, step=20.0, j2=EARTH_J2)

    output = Path(__file__).parents[1] / "docs" / "images" / "leo_orbit.png"
    plot_orbit_comparison(times, two_body, j2_orbit, str(output))

    energy = specific_energy(two_body)
    energy_error = np.max(np.abs((energy - energy[0]) / energy[0]))
    separation = np.linalg.norm(two_body[-1, :3] - j2_orbit[-1, :3])
    print(f"Orbital period: {period / 60.0:.2f} min")
    print(f"Two-body maximum relative energy error: {energy_error:.3e}")
    print(f"Final J2/two-body position separation: {separation / 1e3:.3f} km")
    print(f"Figure saved to: {output}")


if __name__ == "__main__":
    main()
