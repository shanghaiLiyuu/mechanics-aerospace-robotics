"""Plot a planar-arm trajectory and tracking diagnostics."""

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from .kinematics import PlanarArm


def plot_arm_tracking(
    arm: PlanarArm,
    times: NDArray[np.float64],
    desired_path: NDArray[np.float64],
    joint_trajectory: NDArray[np.float64],
    output_path: str,
) -> None:
    figure = plt.figure(figsize=(14, 8), constrained_layout=True)
    grid = figure.add_gridspec(2, 2, width_ratios=(1.2, 1.0))
    workspace_axis = figure.add_subplot(grid[:, 0])
    joint_axis = figure.add_subplot(grid[0, 1])
    error_axis = figure.add_subplot(grid[1, 1])

    actual_path = np.array([arm.end_effector(q) for q in joint_trajectory])
    workspace_axis.plot(
        desired_path[:, 0], desired_path[:, 1], "--", color="#6c757d", linewidth=2, label="Desired path"
    )
    workspace_axis.plot(actual_path[:, 0], actual_path[:, 1], color="#d1495b", linewidth=1.5, label="Tracked path")
    sample_indices = np.linspace(0, len(times) - 1, 9, dtype=int)
    colours = plt.cm.viridis(np.linspace(0.05, 0.9, len(sample_indices)))
    for index, colour in zip(sample_indices, colours):
        positions = arm.forward_kinematics(joint_trajectory[index])
        workspace_axis.plot(*positions.T, "-o", color=colour, linewidth=2.5, markersize=5, alpha=0.9)
    workspace_axis.scatter(0, 0, marker="s", s=80, color="#212529", label="Base")
    workspace_axis.set_title("Two-link arm: Cartesian straight-line tracking", fontsize=15)
    workspace_axis.set_xlabel("X [m]")
    workspace_axis.set_ylabel("Y [m]")
    workspace_axis.axis("equal")
    workspace_axis.grid(alpha=0.25)
    workspace_axis.legend(loc="best")

    for joint in range(arm.joint_count):
        joint_axis.plot(times, np.rad2deg(joint_trajectory[:, joint]), label=f"Joint {joint + 1}")
    joint_axis.set_title("Joint trajectories")
    joint_axis.set_xlabel("Time [s]")
    joint_axis.set_ylabel("Angle [deg]")
    joint_axis.grid(alpha=0.25)
    joint_axis.legend()

    error = np.linalg.norm(actual_path - desired_path, axis=1)
    error_axis.plot(times, error * 1e6, color="#d1495b")
    error_axis.set_title("End-effector tracking error")
    error_axis.set_xlabel("Time [s]")
    error_axis.set_ylabel("Position error [µm]")
    error_axis.grid(alpha=0.25)

    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
