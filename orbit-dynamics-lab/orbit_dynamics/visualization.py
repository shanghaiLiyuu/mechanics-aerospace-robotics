"""Visualization utilities for orbit propagation examples."""

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from .dynamics import EARTH_MU, EARTH_RADIUS, specific_energy


def plot_orbit_comparison(
    times: NDArray[np.float64],
    two_body: NDArray[np.float64],
    j2_orbit: NDArray[np.float64],
    output_path: str,
) -> None:
    """Save a 3D trajectory, altitude history, and integration-error panel."""

    figure = plt.figure(figsize=(14, 9), constrained_layout=True)
    grid = figure.add_gridspec(2, 2, width_ratios=(1.35, 1.0))
    orbit_axis = figure.add_subplot(grid[:, 0], projection="3d")
    altitude_axis = figure.add_subplot(grid[0, 1])
    energy_axis = figure.add_subplot(grid[1, 1])

    scale = 1e3
    orbit_axis.plot(*two_body[:, :3].T / scale, color="#34699a", linewidth=1.5, label="Two-body")
    orbit_axis.plot(*j2_orbit[:, :3].T / scale, color="#d1495b", linewidth=1.2, label="Two-body + J2")
    orbit_axis.scatter(*two_body[0, :3] / scale, color="#2a9d8f", s=55, label="Initial state")

    u, v = np.mgrid[0 : 2 * np.pi : 40j, 0 : np.pi : 20j]
    sphere = EARTH_RADIUS * np.array(
        [np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v)]
    ) / scale
    orbit_axis.plot_surface(*sphere, color="#8ecae6", alpha=0.32, linewidth=0)
    orbit_axis.set_title("Low Earth orbit propagation", fontsize=15)
    orbit_axis.set_xlabel("X [km]")
    orbit_axis.set_ylabel("Y [km]")
    orbit_axis.set_zlabel("Z [km]")
    orbit_axis.legend(loc="upper left")
    orbit_axis.set_box_aspect((1, 1, 1))
    orbit_axis.view_init(elev=25, azim=35)

    hours = times / 3600.0
    altitude_axis.plot(hours, (np.linalg.norm(two_body[:, :3], axis=1) - EARTH_RADIUS) / scale, color="#34699a")
    altitude_axis.plot(hours, (np.linalg.norm(j2_orbit[:, :3], axis=1) - EARTH_RADIUS) / scale, color="#d1495b")
    altitude_axis.set_title("Altitude history")
    altitude_axis.set_xlabel("Time [h]")
    altitude_axis.set_ylabel("Altitude [km]")
    altitude_axis.grid(alpha=0.25)

    energy = specific_energy(two_body, mu=EARTH_MU)
    relative_error = (energy - energy[0]) / abs(energy[0])
    energy_axis.plot(hours, relative_error, color="#34699a")
    energy_axis.set_title("RK4 two-body energy conservation")
    energy_axis.set_xlabel("Time [h]")
    energy_axis.set_ylabel("Relative energy error")
    energy_axis.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    energy_axis.grid(alpha=0.25)

    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
