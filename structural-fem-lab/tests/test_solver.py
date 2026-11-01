import unittest

import numpy as np

from examples.space_truss import build_model
from truss3d import Member, TrussModel


class TrussSolverTests(unittest.TestCase):
    def test_single_bar_matches_analytical_solution(self) -> None:
        youngs_modulus = 200e9
        area = 1e-4
        length = 2.0
        load = 1000.0
        model = TrussModel(
            nodes=[[0.0, 0.0, 0.0], [length, 0.0, 0.0]],
            members=[Member(0, 1, youngs_modulus, area)],
            loads={1: [load, 0.0, 0.0]},
            supports={0: [True] * 3, 1: [False, True, True]},
        )
        result = model.solve()
        expected_displacement = load * length / (youngs_modulus * area)
        self.assertAlmostEqual(result.displacements[1, 0], expected_displacement, places=12)
        self.assertAlmostEqual(result.axial_forces[0], load, places=8)
        self.assertAlmostEqual(result.stresses[0], load / area, places=4)
        np.testing.assert_allclose(result.reactions[0], [-load, 0.0, 0.0], atol=1e-8)

    def test_space_truss_satisfies_global_equilibrium(self) -> None:
        model = build_model()
        result = model.solve()
        total_force = np.sum(model.loads + result.reactions, axis=0)
        np.testing.assert_allclose(total_force, np.zeros(3), atol=1e-7)
        np.testing.assert_allclose(result.reactions[4:], np.zeros((4, 3)), atol=1e-7)
        self.assertTrue(np.all(np.isfinite(result.displacements)))
        self.assertGreater(np.max(result.axial_forces), 0.0)
        self.assertLess(np.min(result.axial_forces), 0.0)

    def test_mechanism_is_rejected(self) -> None:
        model = TrussModel(
            nodes=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
            members=[Member(0, 1, 200e9, 1e-4)],
            loads={1: [0.0, 1.0, 0.0]},
            supports={0: [True] * 3},
        )
        with self.assertRaisesRegex(ValueError, "singular"):
            model.solve()

    def test_invalid_member_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            TrussModel(
                nodes=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                members=[Member(0, 1, -1.0, 1e-4)],
            )


if __name__ == "__main__":
    unittest.main()
