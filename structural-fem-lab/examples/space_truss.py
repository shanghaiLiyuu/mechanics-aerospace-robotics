"""Solve and visualize a braced space-truss block."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np

from truss3d import Member, TrussModel
from truss3d.visualization import plot_deformed_truss


def build_model() -> TrussModel:
    nodes = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
        ]
    )
    connectivity = [
        (0, 4), (1, 5), (2, 6), (3, 7),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (4, 6), (5, 7),
        (0, 5), (1, 4), (1, 6), (2, 5),
        (2, 7), (3, 6), (3, 4), (0, 7),
    ]
    members = [Member(i, j, 210e9, 5e-5) for i, j in connectivity]
    loads = {
        4: [500.0, 0.0, -1000.0],
        5: [500.0, 0.0, -1000.0],
        6: [1000.0, 0.0, -2000.0],
        7: [500.0, 0.0, -1000.0],
    }
    supports = {node: [True, True, True] for node in range(4)}
    return TrussModel(nodes, members, loads, supports)


def main() -> None:
    model = build_model()
    solution = model.solve()
    output = Path(__file__).parents[1] / "docs" / "images" / "space_truss.png"
    plot_deformed_truss(model, solution, str(output))

    displacement_norms = np.linalg.norm(solution.displacements, axis=1)
    total_load = np.sum(model.loads, axis=0)
    total_reaction = np.sum(solution.reactions[:4], axis=0)
    print(f"Maximum displacement: {np.max(displacement_norms) * 1e3:.4f} mm")
    print(f"Maximum tensile force: {np.max(solution.axial_forces):.2f} N")
    print(f"Maximum compressive force: {np.min(solution.axial_forces):.2f} N")
    print(f"Global equilibrium residual: {np.linalg.norm(total_load + total_reaction):.3e} N")
    print(f"Figure saved to: {output}")


if __name__ == "__main__":
    main()
