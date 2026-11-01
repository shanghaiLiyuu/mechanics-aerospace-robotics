"""Track a minimum-jerk Cartesian line with a two-link planar arm."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np

from robot_motion import PlanarArm, minimum_jerk, track_cartesian_path
from robot_motion.visualization import plot_arm_tracking


def main() -> None:
    arm = PlanarArm([1.0, 0.8])
    duration = 3.0
    times = np.linspace(0.0, duration, 100)
    desired_path, _, _ = minimum_jerk(
        times, duration, start=np.array([1.45, 0.35]), end=np.array([0.75, 1.15])
    )
    initial_guess = arm.inverse_kinematics(desired_path[0], elbow=1)
    joint_trajectory = track_cartesian_path(
        arm,
        desired_path,
        initial_guess,
        tolerance=1e-10,
        max_iterations=80,
    )
    actual_path = np.array([arm.end_effector(q) for q in joint_trajectory])
    maximum_error = np.max(np.linalg.norm(actual_path - desired_path, axis=1))

    output = Path(__file__).parents[1] / "docs" / "images" / "arm_tracking.png"
    plot_arm_tracking(arm, times, desired_path, joint_trajectory, str(output))
    print(f"Maximum Cartesian tracking error: {maximum_error * 1e6:.3f} µm")
    print(f"Trajectory samples: {len(times)}")
    print(f"Figure saved to: {output}")


if __name__ == "__main__":
    main()
