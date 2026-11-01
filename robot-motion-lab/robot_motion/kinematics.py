"""Kinematics and numerical inverse kinematics for planar serial arms."""

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


class PlanarArm:
    """A revolute-joint planar arm with arbitrary positive link lengths."""

    def __init__(self, link_lengths: ArrayLike) -> None:
        self.link_lengths = np.asarray(link_lengths, dtype=float)
        if self.link_lengths.ndim != 1 or len(self.link_lengths) == 0:
            raise ValueError("link_lengths must be a non-empty one-dimensional array")
        if not np.all(np.isfinite(self.link_lengths)) or np.any(self.link_lengths <= 0):
            raise ValueError("All link lengths must be finite and positive")

    @property
    def joint_count(self) -> int:
        return len(self.link_lengths)

    def forward_kinematics(self, joint_angles: ArrayLike) -> FloatArray:
        """Return all joint positions, including the base and end effector."""

        angles = self._angles(joint_angles)
        absolute_angles = np.cumsum(angles)
        increments = np.column_stack(
            (self.link_lengths * np.cos(absolute_angles), self.link_lengths * np.sin(absolute_angles))
        )
        return np.vstack((np.zeros(2), np.cumsum(increments, axis=0)))

    def end_effector(self, joint_angles: ArrayLike) -> FloatArray:
        return self.forward_kinematics(joint_angles)[-1]

    def jacobian(self, joint_angles: ArrayLike) -> FloatArray:
        """Return the 2-by-n planar end-effector velocity Jacobian."""

        positions = self.forward_kinematics(joint_angles)
        end = positions[-1]
        jacobian = np.empty((2, self.joint_count), dtype=float)
        for index in range(self.joint_count):
            relative = end - positions[index]
            jacobian[:, index] = [-relative[1], relative[0]]
        return jacobian

    def inverse_kinematics(self, target: ArrayLike, elbow: int = 1) -> FloatArray:
        """Analytical inverse kinematics for a two-link arm.

        elbow=1 and elbow=-1 select the two assembly modes.
        """

        if self.joint_count != 2:
            raise ValueError("Analytical inverse kinematics requires exactly two links")
        point = np.asarray(target, dtype=float)
        if point.shape != (2,):
            raise ValueError("target must have shape (2,)")
        if elbow not in (-1, 1):
            raise ValueError("elbow must be 1 or -1")
        first, second = self.link_lengths
        distance = float(np.linalg.norm(point))
        if distance > first + second or distance < abs(first - second):
            raise ValueError("Target is outside the arm workspace")
        cosine_second = (np.dot(point, point) - first**2 - second**2) / (2 * first * second)
        second_angle = elbow * np.arccos(np.clip(cosine_second, -1.0, 1.0))
        first_angle = np.arctan2(point[1], point[0]) - np.arctan2(
            second * np.sin(second_angle), first + second * np.cos(second_angle)
        )
        return np.array([first_angle, second_angle])

    def _angles(self, joint_angles: ArrayLike) -> FloatArray:
        angles = np.asarray(joint_angles, dtype=float)
        if angles.shape != (self.joint_count,):
            raise ValueError(f"joint_angles must have shape ({self.joint_count},)")
        return angles


def inverse_kinematics_dls(
    arm: PlanarArm,
    target: ArrayLike,
    initial_guess: ArrayLike,
    tolerance: float = 1e-8,
    max_iterations: int = 100,
    damping: float = 0.04,
    max_joint_step: float = 0.15,
) -> FloatArray:
    """Solve inverse kinematics with damped least squares (Levenberg-Marquardt form)."""

    point = np.asarray(target, dtype=float)
    angles = np.asarray(initial_guess, dtype=float).copy()
    if point.shape != (2,) or angles.shape != (arm.joint_count,):
        raise ValueError("Target or initial guess has an incompatible shape")
    if tolerance <= 0 or max_iterations <= 0 or damping <= 0 or max_joint_step <= 0:
        raise ValueError("Solver tolerances, iterations, damping, and step limit must be positive")

    for _ in range(max_iterations):
        error = point - arm.end_effector(angles)
        if np.linalg.norm(error) < tolerance:
            return angles
        jacobian = arm.jacobian(angles)
        regularized = jacobian @ jacobian.T + damping**2 * np.eye(2)
        delta = jacobian.T @ np.linalg.solve(regularized, error)
        norm = float(np.linalg.norm(delta))
        if norm > max_joint_step:
            delta *= max_joint_step / norm
        angles += delta
    raise RuntimeError("Damped least-squares inverse kinematics did not converge")


def track_cartesian_path(
    arm: PlanarArm,
    targets: ArrayLike,
    initial_guess: ArrayLike,
    **solver_options: float,
) -> FloatArray:
    """Track ordered Cartesian targets, warm-starting each inverse-kinematics solve."""

    path = np.asarray(targets, dtype=float)
    if path.ndim != 2 or path.shape[1] != 2 or len(path) == 0:
        raise ValueError("targets must have shape (n, 2) with n > 0")
    trajectory = np.empty((len(path), arm.joint_count), dtype=float)
    guess = np.asarray(initial_guess, dtype=float)
    for index, target in enumerate(path):
        guess = inverse_kinematics_dls(arm, target, guess, **solver_options)
        trajectory[index] = guess
    return trajectory
