import unittest

import numpy as np

from robot_motion import PlanarArm, inverse_kinematics_dls, minimum_jerk, track_cartesian_path


class KinematicsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.arm = PlanarArm([1.0, 0.8])

    def test_analytical_inverse_reconstructs_both_elbow_solutions(self) -> None:
        target = np.array([1.2, 0.7])
        for elbow in (-1, 1):
            angles = self.arm.inverse_kinematics(target, elbow=elbow)
            np.testing.assert_allclose(self.arm.end_effector(angles), target, atol=1e-12)

    def test_jacobian_matches_finite_difference(self) -> None:
        angles = np.array([0.4, -0.7])
        analytical = self.arm.jacobian(angles)
        numerical = np.empty_like(analytical)
        epsilon = 1e-7
        for joint in range(2):
            offset = np.zeros(2)
            offset[joint] = epsilon
            numerical[:, joint] = (
                self.arm.end_effector(angles + offset) - self.arm.end_effector(angles - offset)
            ) / (2 * epsilon)
        np.testing.assert_allclose(analytical, numerical, atol=1e-8)

    def test_damped_least_squares_tracks_path(self) -> None:
        targets = np.array([[1.4, 0.3], [1.3, 0.4], [1.2, 0.5]])
        initial = self.arm.inverse_kinematics(targets[0])
        trajectory = track_cartesian_path(self.arm, targets, initial, tolerance=1e-9)
        actual = np.array([self.arm.end_effector(q) for q in trajectory])
        np.testing.assert_allclose(actual, targets, atol=1e-8)

    def test_unreachable_target_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside"):
            self.arm.inverse_kinematics([3.0, 0.0])


class TrajectoryTests(unittest.TestCase):
    def test_minimum_jerk_boundary_conditions(self) -> None:
        position, velocity, acceleration = minimum_jerk([0.0, 2.0], 2.0, [1.0, -1.0], [4.0, 3.0])
        np.testing.assert_allclose(position[0], [1.0, -1.0])
        np.testing.assert_allclose(position[1], [4.0, 3.0])
        np.testing.assert_allclose(velocity, np.zeros((2, 2)), atol=1e-12)
        np.testing.assert_allclose(acceleration, np.zeros((2, 2)), atol=1e-12)

    def test_minimum_jerk_midpoint(self) -> None:
        position, _, _ = minimum_jerk(1.0, 2.0, 0.0, 4.0)
        self.assertAlmostEqual(float(position), 2.0, places=12)

    def test_invalid_sample_time_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            minimum_jerk(3.0, 2.0, 0.0, 1.0)


if __name__ == "__main__":
    unittest.main()
