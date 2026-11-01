"""Small-deformation finite element solver for three-dimensional trusses."""

from dataclasses import dataclass
from typing import Iterable, Mapping

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class Member:
    """A pin-jointed, linear-elastic bar with constant cross-section."""

    start: int
    end: int
    youngs_modulus: float
    area: float


@dataclass(frozen=True)
class Solution:
    """Nodal and member results; axial force is positive in tension."""

    displacements: FloatArray
    reactions: FloatArray
    axial_forces: FloatArray
    stresses: FloatArray


class TrussModel:
    """Assemble and solve K*u = F for a 3D truss.

    Coordinates and lengths use metres, forces use newtons, and stresses use
    pascals. Each node has three translational degrees of freedom.
    """

    def __init__(
        self,
        nodes: ArrayLike,
        members: Iterable[Member],
        loads: Mapping[int, ArrayLike] | None = None,
        supports: Mapping[int, ArrayLike] | None = None,
    ) -> None:
        self.nodes = np.asarray(nodes, dtype=float)
        self.members = tuple(members)
        self._validate_geometry()

        self.loads = np.zeros_like(self.nodes)
        for node, force in (loads or {}).items():
            self.loads[node] = self._vector3(force, f"load at node {node}")

        self.supports = np.zeros(self.nodes.shape, dtype=bool)
        for node, fixed in (supports or {}).items():
            fixed_vector = np.asarray(fixed, dtype=bool)
            if fixed_vector.shape != (3,):
                raise ValueError("Each support entry must contain three booleans")
            self.supports[node] = fixed_vector

    def _validate_geometry(self) -> None:
        if self.nodes.ndim != 2 or self.nodes.shape[1] != 3:
            raise ValueError("nodes must have shape (n, 3)")
        if not np.all(np.isfinite(self.nodes)):
            raise ValueError("Node coordinates must be finite")
        if not self.members:
            raise ValueError("At least one member is required")
        for member in self.members:
            if not (0 <= member.start < len(self.nodes)) or not (
                0 <= member.end < len(self.nodes)
            ):
                raise ValueError("Member node index is out of range")
            if member.start == member.end:
                raise ValueError("A member must connect two different nodes")
            if member.youngs_modulus <= 0 or member.area <= 0:
                raise ValueError("Young's modulus and area must be positive")

    @staticmethod
    def _vector3(value: ArrayLike, name: str) -> FloatArray:
        vector = np.asarray(value, dtype=float)
        if vector.shape != (3,):
            raise ValueError(f"{name} must have shape (3,)")
        return vector

    def _member_geometry(self, member: Member) -> tuple[FloatArray, float]:
        delta = self.nodes[member.end] - self.nodes[member.start]
        length = float(np.linalg.norm(delta))
        if length <= 0:
            raise ValueError("Member length must be positive")
        return delta / length, length

    def assemble(self) -> FloatArray:
        """Return the global stiffness matrix in newtons per metre."""

        size = 3 * len(self.nodes)
        stiffness = np.zeros((size, size), dtype=float)
        for member in self.members:
            direction, length = self._member_geometry(member)
            local = (
                member.youngs_modulus
                * member.area
                / length
                * np.outer(direction, direction)
            )
            dofs = np.r_[
                3 * member.start : 3 * member.start + 3,
                3 * member.end : 3 * member.end + 3,
            ]
            block = np.block([[local, -local], [-local, local]])
            stiffness[np.ix_(dofs, dofs)] += block
        return stiffness

    def solve(self) -> Solution:
        """Solve the constrained linear system and recover member results."""

        stiffness = self.assemble()
        external_force = self.loads.ravel()
        fixed = self.supports.ravel()
        free = ~fixed
        if not np.any(free):
            raise ValueError("At least one free degree of freedom is required")

        displacements = np.zeros_like(external_force)
        try:
            displacements[free] = np.linalg.solve(
                stiffness[np.ix_(free, free)], external_force[free]
            )
        except np.linalg.LinAlgError as exc:
            raise ValueError(
                "The reduced stiffness matrix is singular; check supports and connectivity"
            ) from exc
        if not np.all(np.isfinite(displacements)):
            raise ValueError("The solution is not finite; check model units and stability")

        nodal_displacements = displacements.reshape((-1, 3))
        reactions = (stiffness @ displacements - external_force).reshape((-1, 3))
        axial_forces = []
        stresses = []
        for member in self.members:
            direction, length = self._member_geometry(member)
            extension = np.dot(
                direction,
                nodal_displacements[member.end]
                - nodal_displacements[member.start],
            )
            force = member.youngs_modulus * member.area * extension / length
            axial_forces.append(force)
            stresses.append(force / member.area)

        return Solution(
            displacements=nodal_displacements,
            reactions=reactions,
            axial_forces=np.asarray(axial_forces),
            stresses=np.asarray(stresses),
        )
