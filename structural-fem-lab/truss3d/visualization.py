"""Matplotlib visualization for space-truss results."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm, colors

from .core import Solution, TrussModel


def plot_deformed_truss(
    model: TrussModel,
    solution: Solution,
    output_path: str,
    scale: float | None = None,
) -> None:
    """Save an original/deformed geometry comparison with axial-force colours."""

    maximum_displacement = float(np.max(np.linalg.norm(solution.displacements, axis=1)))
    if maximum_displacement == 0:
        raise ValueError("Cannot auto-scale a zero-displacement solution")
    span = float(np.max(np.ptp(model.nodes, axis=0)))
    scale = scale or 0.18 * span / maximum_displacement
    deformed = model.nodes + scale * solution.displacements

    figure = plt.figure(figsize=(11, 8), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    for member in model.members:
        original = model.nodes[[member.start, member.end]]
        axis.plot(*original.T, color="#aab2bd", linewidth=1, linestyle="--", alpha=0.7)

    maximum_force = max(float(np.max(np.abs(solution.axial_forces))), 1.0)
    norm = colors.Normalize(vmin=-maximum_force, vmax=maximum_force)
    for member, force in zip(model.members, solution.axial_forces):
        points = deformed[[member.start, member.end]]
        axis.plot(
            *points.T,
            color=cm.coolwarm(norm(force)),
            linewidth=3,
            solid_capstyle="round",
        )
    axis.scatter(*deformed.T, s=28, color="#172b4d", depthshade=False)
    axis.scatter(*model.nodes[:4].T, s=65, marker="s", color="#344563", label="Fixed supports")

    colour_bar = figure.colorbar(
        cm.ScalarMappable(norm=norm, cmap=cm.coolwarm), ax=axis, shrink=0.62, pad=0.08
    )
    colour_bar.set_label("Axial force [N]  (tension + / compression -)")
    axis.set_title("3D space truss: deformed shape and member forces", fontsize=15)
    axis.set_xlabel("X [m]")
    axis.set_ylabel("Y [m]")
    axis.set_zlabel("Z [m]")
    axis.view_init(elev=24, azim=-55)
    axis.legend(loc="upper left")

    all_points = np.vstack((model.nodes, deformed))
    centre = np.mean(all_points, axis=0)
    radius = max(float(np.max(np.ptp(all_points, axis=0))) / 2, 1e-9)
    axis.set_xlim(centre[0] - radius, centre[0] + radius)
    axis.set_ylim(centre[1] - radius, centre[1] + radius)
    axis.set_zlim(centre[2] - radius, centre[2] + radius)
    axis.set_box_aspect((1, 1, 1))
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
