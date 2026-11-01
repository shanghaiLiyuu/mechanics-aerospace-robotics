import unittest

import numpy as np

from orbit_dynamics import (
    EARTH_J2,
    EARTH_MU,
    OrbitalElements,
    acceleration,
    kepler_to_state,
    orbital_period,
    propagate,
    specific_energy,
)


class OrbitDynamicsTests(unittest.TestCase):
    def test_circular_orbit_radius_and_speed(self) -> None:
        axis = 7_000_000.0
        state = kepler_to_state(
            OrbitalElements(axis, 0.0, 0.4, 0.2, 0.0, 0.0)
        )
        self.assertAlmostEqual(np.linalg.norm(state[:3]), axis, places=6)
        self.assertAlmostEqual(np.linalg.norm(state[3:]), np.sqrt(EARTH_MU / axis), places=6)
        self.assertAlmostEqual(np.dot(state[:3], state[3:]), 0.0, places=5)

    def test_one_period_returns_to_initial_state(self) -> None:
        axis = 7_000_000.0
        initial = kepler_to_state(OrbitalElements(axis, 0.0, 0.7, 0.1, 0.0, 0.0))
        _, states = propagate(initial, orbital_period(axis), step=10.0)
        self.assertLess(np.linalg.norm(states[-1] - initial), 100.0)

    def test_rk4_conserves_two_body_energy(self) -> None:
        initial = kepler_to_state(
            OrbitalElements(8_000_000.0, 0.01, 0.5, 0.3, 0.2, 0.1)
        )
        _, states = propagate(initial, 3600.0, step=20.0)
        energy = specific_energy(states)
        relative_error = np.max(np.abs((energy - energy[0]) / energy[0]))
        self.assertLess(relative_error, 1e-7)

    def test_j2_changes_acceleration(self) -> None:
        position = np.array([7_000_000.0, 0.0, 1_000_000.0])
        two_body = acceleration(position, j2=0.0)
        perturbed = acceleration(position, j2=EARTH_J2)
        self.assertGreater(np.linalg.norm(perturbed - two_body), 0.0)

    def test_surface_impact_is_detected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Surface impact"):
            propagate([6_500_000.0, 0.0, 0.0, 0.0, 0.0, 0.0], 200.0, 10.0)


if __name__ == "__main__":
    unittest.main()
